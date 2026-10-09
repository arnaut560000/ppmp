"""Read-only OOXML inventory for Phase 1; never modifies or recalculates the source."""
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from hashlib import sha256
from pathlib import Path
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\Users\arnaut\OneDrive\Desktop\PPMP.xlsx')
OUT = Path(__file__).resolve().parents[1] / 'docs' / 'phase-1'
OUT.mkdir(parents=True, exist_ok=True)
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def col_number(ref):
    number = 0
    for char in re.match(r'[A-Z]+', ref).group():
        number = number * 26 + ord(char) - 64
    return number

def col_name(number):
    result = ''
    while number:
        number, rem = divmod(number - 1, 26)
        result = chr(65 + rem) + result
    return result

def decimal(value):
    try:
        return Decimal(str(value)) if value not in ('', None) else None
    except InvalidOperation:
        return None

data = SOURCE.read_bytes()
summary = {'source_path': str(SOURCE), 'source_sha256': sha256(data).hexdigest(),
           'source_size_bytes': len(data), 'inspection_date': '2026-10-08',
           'method': 'OOXML read only; stored values and formulas; no recalculation', 'sheets': []}
catalog = []
groups = []
with zipfile.ZipFile(SOURCE) as archive:
    strings = []
    if 'xl/sharedStrings.xml' in archive.namelist():
        strings = [''.join(node.itertext()) for node in ET.fromstring(archive.read('xl/sharedStrings.xml'))]
    workbook = ET.fromstring(archive.read('xl/workbook.xml'))
    rels = {node.attrib['Id']: node.attrib['Target'] for node in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
    for sheet in workbook.find('s:sheets', NS):
        target = rels[sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
        member = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        root = ET.fromstring(archive.read(member))
        rows = {}
        formulas = []
        errors = []
        for row in root.findall('s:sheetData/s:row', NS):
            cells = {}
            for cell in row:
                value_node = cell.find('s:v', NS)
                inline = cell.find('s:is', NS)
                value = value_node.text if value_node is not None else ''.join(inline.itertext()) if inline is not None else ''
                if cell.attrib.get('t') == 's': value = strings[int(value)]
                formula = cell.find('s:f', NS)
                ref = cell.attrib['r']
                if value not in ('', None) or formula is not None:
                    cells[col_number(ref)] = {'cell': ref, 'value': value, 'type': cell.attrib.get('t', 'n')}
                if formula is not None: formulas.append({'cell': ref, 'formula': formula.text, 'attributes': formula.attrib})
                if cell.attrib.get('t') == 'e': errors.append({'cell': ref, 'value': value})
            if cells: rows[int(row.attrib['r'])] = cells
        value = lambda row, col: rows.get(row, {}).get(col, {}).get('value', '')
        sheet_groups = []
        for col, cell in sorted(rows.get(4, {}).items()):
            if col < 6: continue
            group = {'source_sheet': sheet.attrib['name'], 'label': cell['value'],
                     'source_header': cell['cell'], 'start_column_number': col,
                     'quantity_cells': [f'{col_name(col + 2*q)}{{row}}' for q in range(4)],
                     'amount_cells': [f'{col_name(col + 2*q + 1)}{{row}}' for q in range(4)],
                     'annual_quantity_cell': f'{col_name(col+8)}{{row}}',
                     'annual_amount_cell': f'{col_name(col+9)}{{row}}',
                     'owner_department': None, 'classification': 'UNCONFIRMED',
                     'mapping_status': 'NEEDS_AGENCY_CONFIRMATION'}
            groups.append(group);sheet_groups.append(group)
        candidates = []
        totals = []
        other_labels = []
        for rn in sorted(rows):
            if rn <= 7: continue
            a,b,c,d = (value(rn, col) for col in range(1,5))
            if b:
                if not a and not c and d in ('', None) and re.match(r'^(GRAND\s+)?TOTAL\b', b.strip(), re.I):
                    totals.append({'row':rn,'label':b})
                    continue
                record = {'source_sheet':sheet.attrib['name'], 'source_row':rn,
                          'source_key':f'{sheet.attrib["name"]}:{rn}',
                          'expense_object':a, 'description':b, 'unit':c,
                          'unit_cost_raw':d, 'unit_cost_numeric':str(decimal(d)) if decimal(d) is not None else None,
                          'mapping_status':'CANDIDATE_NOT_APPROVED'}
                candidates.append(record);catalog.append(record)
            elif a: other_labels.append({'row':rn,'label':a,'unit':c,'unit_cost_raw':d})
        stats=Counter(); group_stats=[]; examples=defaultdict(list)
        amount_checks=Counter(); amount_issues=[]
        for group in sheet_groups:
            gs=Counter();col=group['start_column_number']
            for item in candidates:
                rn=item['source_row']
                for q in range(4):
                    raw=value(rn,col+2*q);n=decimal(raw)
                    kind='blank' if raw in ('',None) else 'zero' if n == 0 else 'positive' if n is not None and n>0 else 'negative' if n is not None else 'text'
                    gs['quarter_quantity_'+kind]+=1
                    if kind in ('positive','negative','text') and len(examples['quantity_'+kind])<8:
                        examples['quantity_'+kind].append({'cell':f'{col_name(col+2*q)}{rn}','value':raw,'group':group['label']})
                    raw_amount=value(rn,col+2*q+1)
                    kind_a='blank' if raw_amount in ('',None) else 'dash' if str(raw_amount).strip()=='-' else 'numeric' if decimal(raw_amount) is not None else 'other_text'
                    gs['quarter_amount_'+kind_a]+=1
                    amount=decimal(raw_amount);cost=decimal(item['unit_cost_raw'])
                    if kind_a=='other_text' and len(examples['amount_other_text'])<8:
                        examples['amount_other_text'].append({'cell':f'{col_name(col+2*q+1)}{rn}','value':raw_amount})
                    if n is not None and amount is not None and cost is not None:
                        amount_checks['numeric_pairs_checked']+=1
                        expected=(n*cost).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
                        if abs(expected-amount)>Decimal('0.01'):
                            amount_checks['mismatch_over_one_cent']+=1
                            amount_issues.append({'cell':f'{col_name(col+2*q+1)}{rn}','group':group['label'],'quantity':str(n),'unit_cost':str(cost),'stored_amount':str(amount),'proposed_calculated_amount':str(expected)})
                    elif n is not None and n>0 and (amount is None or cost is None):
                        amount_checks['positive_quantity_with_missing_price_or_numeric_amount']+=1
                        amount_issues.append({'cell':f'{col_name(col+2*q+1)}{rn}','group':group['label'],'quantity':str(n),'unit_cost_raw':item['unit_cost_raw'],'stored_amount_raw':raw_amount,'issue':'Missing price or numeric amount'})
            stats.update(gs)
            group_stats.append({'group':group['label'],'counts':dict(gs)})
        by_description=defaultdict(list)
        by_exact=defaultdict(list)
        for item in candidates:
            by_description[item['description'].strip().casefold()].append(item)
            by_exact[(item['expense_object'],item['description'],item['unit'],item['unit_cost_raw'])].append(item['source_row'])
        duplicates=[{'description':items[0]['description'],'rows':[x['source_row'] for x in items],
                     'units':sorted(set(x['unit'] for x in items)),
                     'unit_costs':sorted(set(x['unit_cost_raw'] for x in items))}
                    for items in by_description.values() if len(items)>1]
        protection=root.find('s:sheetProtection',NS)
        validations=root.find('s:dataValidations',NS)
        summary['sheets'].append({
            'name':sheet.attrib['name'],'title':value(1,1),
            'dimension':root.find('s:dimension',NS).attrib.get('ref'),
            'nonempty_row_count':len(rows),'candidate_item_rows':len(candidates),
            'excluded_total_rows':totals,
            'reporting_groups':len(sheet_groups),'formula_cell_count':len(formulas),
            'formula_examples':formulas[:12],'error_cells':errors,
            'sheet_protection':protection.attrib if protection is not None else None,
            'data_validation_count':len(validations) if validations is not None else 0,
            'category_counts':dict(Counter(x['expense_object'] for x in candidates)),
            'unit_counts':dict(Counter(x['unit'] for x in candidates)),
            'candidate_missing_unit_rows':[x['source_row'] for x in candidates if not x['unit']],
            'candidate_missing_or_nonnumeric_cost_rows':[x['source_row'] for x in candidates if x['unit_cost_numeric'] is None],
            'duplicate_description_groups':duplicates,
            'exact_duplicate_candidate_row_sets':[v for v in by_exact.values() if len(v)>1],
            'other_labeled_rows':other_labels,'quarter_cell_counts':dict(stats),
            'quarter_cell_examples':dict(examples),'group_quantity_counts':group_stats,
            'quarter_amount_checks':dict(amount_checks),'quarter_amount_issues':amount_issues,
            'print_options':{key:(root.find('s:'+key,NS).attrib if root.find('s:'+key,NS) is not None else None) for key in ['pageSetup','pageMargins','printOptions']},
        })
for name,content in [('WORKBOOK_INVENTORY.json',summary),('REPORTING_GROUPS.json',groups),('CATALOG_CANDIDATES.json',catalog)]:
    (OUT/name).write_text(json.dumps(content,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for sheet in summary['sheets']:
    print(json.dumps({key:sheet[key] for key in ['name','title','dimension','candidate_item_rows','reporting_groups','formula_cell_count','category_counts','candidate_missing_unit_rows','candidate_missing_or_nonnumeric_cost_rows','quarter_cell_counts']},ensure_ascii=True))
    print('duplicate_descriptions:',len(sheet['duplicate_description_groups']))
    print('other_labels:',json.dumps(sheet['other_labeled_rows'][:20]))
print('Source SHA-256:',summary['source_sha256'])
assert SOURCE.read_bytes()==data,'Source changed during inspection; rerun to get a consistent snapshot.'
assert len({x['source_key'] for x in catalog})==len(catalog)
for sheet in summary['sheets']:
    quantity_count=sum(v for k,v in sheet['quarter_cell_counts'].items() if k.startswith('quarter_quantity_'))
    assert quantity_count==sheet['candidate_item_rows']*sheet['reporting_groups']*4
