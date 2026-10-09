from pathlib import Path
import re

OUT = Path(__file__).resolve().parent

# A graph model produces both PlantUML and a complete flow register.
nodes = {
    'U': ('rectangle', 'All authenticated roles / login user'),
    'A': ('rectangle', 'System Administrator'),
    'E': ('rectangle', 'Department Preparer'),
    'H': ('rectangle', 'Department Head'),
    'B': ('rectangle', 'Budget Reviewer'),
    'R': ('rectangle', 'Procurement Reviewer'),
    'F': ('rectangle', 'Authorized Approver'),
    'V': ('rectangle', 'Auditor / Viewer'),
    'P1': ('usecase', '1.0\nAuthenticate and Manage Access'),
    'P2': ('usecase', '2.0\nMaintain Planning Reference Data'),
    'P3': ('usecase', '3.0\nPrepare and Submit Department PPMP'),
    'P4': ('usecase', '4.0\nReview and Decide on Submitted Versions'),
    'P5': ('usecase', '5.0\nConsolidate and Produce Reports'),
    'P6': ('usecase', '6.0\nRecord Audit Events and Notifications'),
    'D1': ('database', 'D1 Identity and Access\nusers, departments, memberships, roles,\npermissions, role assignments, sessions'),
    'D2': ('database', 'D2 Planning Reference Data\nfiscal years, planning groups, owner mappings,\nitems, units, expense objects, annual prices,\nfunds, methods, allocations, workflow templates'),
    'D3': ('database', 'D3 PPMP Plans and Versions\nplan identities, version headers,\nversion items, quarterly quantities, snapshots'),
    'D4': ('database', 'D4 Private Attachments\nversion-linked metadata and file objects'),
    'D5': ('database', 'D5 Review Records\nreview instances, assigned stages,\nappend-only decisions and comments'),
    'D6': ('database', 'D6 Consolidations and Exports\nreport runs, selected versions, source-line links,\nexport metadata and private output files'),
    'D7': ('database', 'D7 Append-only Audit Log'),
    'D8': ('database', 'D8 Event Outbox and Notifications'),
}

packets = {
 'AUTH': 'login identifier, password or session credential, optional MFA response; credentials never included in audit records',
 'AUTH_RESULT': 'success/denial, user_id, session identifier, permitted department scope and roles; no password hashes returned',
 'ACCOUNT_CHANGE': 'target user_id, name, login identifier, account state, department membership, role, department/global scope, expected record revision',
 'ACCESS_RESULT': 'saved account/assignment IDs, effective access scope, validation or permission errors',
 'ACCESS_RECORDS': 'users, password hashes for authentication only, active state, department memberships, scoped roles, permission grants, session state; readers receive only needed fields',
 'ACCESS_WRITE': 'validated user/membership/role changes, credential hash or session changes; no plain-text credential storage',
 'SETUP_CHANGE': 'fiscal_year_id, group_id and owner_department_id, expense_object_id, item_id, unit_id, annual unit cost, fund_id, method_id, allocation amount, deadline, workflow template and stage assignments; supplied subset depends on operation',
 'SETUP_RESULT': 'saved reference IDs, effective dates/version, missing mapping warnings, validation/conflict errors',
 'REFERENCE': 'active years, owned planning groups, canonical item IDs/descriptions/specifications, units, expense objects, annual prices, funding/method lists, allocations, submission periods and versioned workflow rules',
 'REFERENCE_WRITE': 'validated reference rows, ownership mappings, annual prices, allocations and workflow template versions; historical references retained',
 'DRAFT_REQUEST': 'authenticated actor, owned group_id, fiscal_year_id, plan/version ID, requested action, expected lock_version; items with catalog item_id, Q1-Q4 quantities and optional approved extension fields',
 'FILE_REQUEST': 'version_id, attachment_id for read/remove, uploaded bytes for add, original filename, MIME type, size, expected draft revision',
 'DRAFT_RESULT': 'scoped draft detail, item/unit/price snapshots, Q1-Q4 quantities and amounts, annual totals, comments/status, validation or stale-edit errors, attachment result or authorized download',
 'PLAN_READ': 'plan_id, owner_department_id, planning_group_id, fiscal_year_id; versions, content state, base_version_id, item snapshots, quarterly values, lock_version and submission timestamps',
 'DRAFT_WRITE': 'plan/version identity, content state (draft/submitted), editable content or frozen submission snapshot, item_id and description/unit/expense/price snapshots, quarter quantities, derived amounts/totals, creator, submitted_at and lock_version',
 'ATTACH_READ': 'attachment_id, version_id, storage key, filename, MIME type, size, checksum, uploader, uploaded_at and authorized file bytes',
 'ATTACH_WRITE': 'validated file object plus version-linked metadata, or permitted draft-only unlink; submitted attachment objects remain immutable',
 'REVIEW_READ': 'version-specific stage assignments, pending/completed state, decisions, comments, reviewer IDs and timestamps',
 'SUBMISSION': 'plan_id, immutable submitted version_id, owner_department_id, group_id, fiscal_year_id, content hash, workflow template version, submitter_id, submitted_at',
 'REVIEW_QUERY': 'actor_id, permitted department/global scope, pending queue filters, version_id or attachment_id',
 'HEAD_DECISION': 'version_id, assigned stage_id, endorse/return, required reason for return, optional line_id, expected stage revision',
 'BUDGET_DECISION': 'version_id, assigned stage_id, pass/return, allocation reference, budget observations and comment, expected stage revision',
 'PROC_DECISION': 'version_id, assigned stage_id, pass/return, specification/unit/method findings and comment, expected stage revision',
 'FINAL_DECISION': 'version_id, assigned stage_id, approve/return/reject, reason/comment, expected stage revision',
 'REVIEW_PACKET': 'authorized queue or immutable version detail, item and quarterly totals, attachments, allocation context, prior decisions, action receipt or validation/permission/conflict error',
 'REVIEW_WRITE': 'review instance, frozen stage sequence and assignments, actor-specific decision, line/version comment, timestamp, current stage and review state',
 'PLAN_STATE_WRITE': 'version_id, returned/rejected/approved state, approval timestamp, plan effective_approved_version_id where appropriate; content never edited by a reviewer',
 'REPORT_QUERY': 'actor_id and scope, fiscal_year_id, group/department filters, expense/item/quarter/fund filters, status, as_of timestamp, requested format and report type',
 'CONSOLIDATE_REQUEST': 'fiscal_year_id, selected groups, explicit approved version IDs or current-effective selection, report grouping, requested Excel/PDF format',
 'REPORT_RESULT': 'authorized dashboard, department PPMP or consolidated matrix; quarterly quantities/amounts, annual totals, coverage/missing-group warnings, source version IDs, export job state or authorized file download',
 'REPORT_READ': 'report_run_id, selected source versions, source version-item-quarter links, aggregation rule, creator, created_at, export state, file metadata and authorized bytes',
 'REPORT_WRITE': 'report run, selection snapshot, source lineage records, totals, coverage warnings, grouping definition, export status, output file key/checksum and creator',
 'DOMAIN_EVENT': 'unique event_id, actor_id, role/scope snapshot, event type, resource type/ID, department/group/year/version IDs where applicable, redacted change summary, outcome, correlation_id, occurred_at and notification audience rule',
 'INBOX_QUERY': 'authenticated recipient_id, unread/all filter, notification_id and mark-read request',
 'INBOX_RESULT': 'recipient-owned notification IDs, safe subject/message, resource link, occurred_at, read_at and unread count',
 'AUDIT_QUERY': 'actor_id and audit permission scope, user/resource/department/year filters, date range and pagination',
 'AUDIT_RESULT': 'authorized redacted audit records with actor, operation, target IDs, change summary, outcome, timestamp and correlation_id',
 'OUTBOX_READ': 'unprocessed committed event records and recipient notifications, event status, attempts, read_at',
 'OUTBOX_WRITE': 'unique committed event_id with payload, processing state/attempts, deduplicated recipient notifications, read_at updates',
 'AUDIT_WRITE': 'append-only event_id, actor/scope snapshot, operation, target IDs, redacted before/after summary, outcome, timestamp, correlation_id',
 'AUDIT_READ': 'stored audit records limited to authorized query scope',
}

flows = []
def flow(src, dst, label, packet):
    flows.append((f'F{len(flows)+1:03}', src, dst, label, packet))

for args in [
 ('U','P1','Login / logout / session request','AUTH'),
 ('P1','U','Authentication result','AUTH_RESULT'),
 ('A','P1','Account and department access changes','ACCOUNT_CHANGE'),
 ('P1','A','Account administration result','ACCESS_RESULT'),
 ('D1','P1','Identity, access and session records','ACCESS_RECORDS'),
 ('P1','D1','Validated accounts, access and sessions','ACCESS_WRITE'),
 ('A','P2','Catalog, planning and workflow changes','SETUP_CHANGE'),
 ('P2','A','Reference-data result','SETUP_RESULT'),
 ('D1','P2','Administrator permission scope','ACCESS_RECORDS'),
 ('D2','P2','Existing reference records','REFERENCE'),
 ('P2','D2','Validated reference records','REFERENCE_WRITE'),
 ('E','P3','Draft, revision and submission request','DRAFT_REQUEST'),
 ('E','P3','Attachment upload / retrieval / unlink','FILE_REQUEST'),
 ('P3','E','Draft detail, totals and validation result','DRAFT_RESULT'),
 ('D1','P3','User and department permissions','ACCESS_RECORDS'),
 ('D2','P3','Owned groups, catalog, prices and rules','REFERENCE'),
 ('D3','P3','Existing plan and version content','PLAN_READ'),
 ('P3','D3','Draft content or immutable submitted version','DRAFT_WRITE'),
 ('D4','P3','Version attachment records and bytes','ATTACH_READ'),
 ('P3','D4','Validated draft attachments','ATTACH_WRITE'),
 ('D5','P3','Return comments and review status','REVIEW_READ'),
 ('P3','P4','Submitted version reference','SUBMISSION'),
 ('H','P4','Review queue / version / attachment request','REVIEW_QUERY'),
 ('H','P4','Endorsement or return with comments','HEAD_DECISION'),
 ('P4','H','Head review packet and action result','REVIEW_PACKET'),
 ('B','P4','Review queue / version / attachment request','REVIEW_QUERY'),
 ('B','P4','Budget findings and decision','BUDGET_DECISION'),
 ('P4','B','Budget review packet and action result','REVIEW_PACKET'),
 ('R','P4','Review queue / version / attachment request','REVIEW_QUERY'),
 ('R','P4','Procurement findings and decision','PROC_DECISION'),
 ('P4','R','Procurement review packet and action result','REVIEW_PACKET'),
 ('F','P4','Review queue / version / attachment request','REVIEW_QUERY'),
 ('F','P4','Approval, return or rejection','FINAL_DECISION'),
 ('P4','F','Approval packet and action result','REVIEW_PACKET'),
 ('D1','P4','Current reviewer authority and scope','ACCESS_RECORDS'),
 ('D2','P4','Workflow templates and budget context','REFERENCE'),
 ('D3','P4','Submitted content and effective version','PLAN_READ'),
 ('D4','P4','Submitted attachment records and bytes','ATTACH_READ'),
 ('D5','P4','Existing stages, comments and decisions','REVIEW_READ'),
 ('P4','D5','Review assignments, decisions and comments','REVIEW_WRITE'),
 ('P4','D3','Version state and effective approved version','PLAN_STATE_WRITE'),
 ('U','P5','Scoped dashboard / report / export request','REPORT_QUERY'),
 ('R','P5','Approved-version consolidation request','CONSOLIDATE_REQUEST'),
 ('P5','U','Scoped report, totals or export result','REPORT_RESULT'),
 ('D1','P5','Report permissions and department scope','ACCESS_RECORDS'),
 ('D2','P5','Group mappings and report reference data','REFERENCE'),
 ('D3','P5','Selected versions and quarterly item data','PLAN_READ'),
 ('D5','P5','Approval evidence and status history','REVIEW_READ'),
 ('D6','P5','Existing report lineage and output files','REPORT_READ'),
 ('P5','D6','Report snapshot, lineage and export files','REPORT_WRITE'),
 ('U','P6','Notification query / read acknowledgement','INBOX_QUERY'),
 ('P6','U','Recipient notifications and unread count','INBOX_RESULT'),
 ('V','P6','Authorized audit-history query','AUDIT_QUERY'),
 ('P6','V','Filtered audit history','AUDIT_RESULT'),
 ('D1','P6','Recipient membership and audit permissions','ACCESS_RECORDS'),
 ('D7','P6','Scoped audit entries','AUDIT_READ'),
 ('P6','D7','Redacted append-only audit entries','AUDIT_WRITE'),
 ('D8','P6','Committed events and recipient inbox records','OUTBOX_READ'),
 ('P6','D8','Committed events, inbox messages and read state','OUTBOX_WRITE'),
]: flow(*args)
for i in range(1,6): flow(f'P{i}','P6',f'Process {i}.0 audit / notification event','DOMAIN_EVENT')

header = '''left to right direction
skinparam shadowing false
skinparam defaultFontName Arial
skinparam defaultFontSize 12
skinparam ArrowFontSize 10
skinparam linetype polyline
skinparam nodesep 35
skinparam ranksep 55
skinparam rectangleBackgroundColor #F1F5F9
skinparam usecaseBackgroundColor #DBEAFE
skinparam databaseBackgroundColor #FEF3C7
'''

def diagram(name,title,graph,extra=None,note=''):
    local = dict(nodes)
    local.update(extra or {})
    used = set()
    for _,s,t,_,_ in graph: used.update((s,t))
    lines=[f'@startuml {name}',header,f'title {title}']
    for key in local:
        if key in used:
            shape,label=local[key]
            label=label.replace('\n',r'\n')
            lines.append(f'{shape} "{label}" as {key}')
    lines.append('')
    for fid,s,t,label,packet in graph:
        lines.append(f'{s} --> {t} : {fid} {label}\\n[{packet}]')
    lines += ['legend bottom','Rectangle = external role; oval = data-transforming process',
              'Cylinder = logical data store; arrow = named data payload',
              'U groups all roles for shared login, reports and inbox functions.',
              'Numbered process peers in Level 2 are outside the decomposed process.',
              'Packet fields: FLOW_REGISTER.md; relationships: DATA_DICTIONARY.md', 'endlegend']
    if note: lines += ['note as DesignNote',note,'end note']
    lines.append('@enduml')
    (OUT/f'{name}.puml').write_text('\n'.join(lines)+'\n',encoding='utf-8')

diagram('01_level1','PPMP Management System - Level 1 DFD',flows,
        note='Proposed internal approval workflow; exact stage order requires agency confirmation.\nOnly approved versions feed official consolidation. Draft dashboards are labelled separately.')

context=[]
external={k for k,v in nodes.items() if v[0]=='rectangle'}
for fid,s,t,label,packet in flows:
    if s in external: context.append((fid,s,'P0',label,packet))
    elif t in external: context.append((fid,'P0',t,label,packet))
diagram('00_context','PPMP Management System - Context DFD',context,
        {'P0':('usecase','0\nGovernment PPMP Management System')})

# Every Level 2 boundary retains exactly the Level 1 flow ID and packet.
# Assign each boundary to the appropriate internal subprocess.
subprocesses={
 'P1': [('P11','1.1 Authenticate Session'),('P12','1.2 Validate Account and Role Changes'),('P13','1.3 Persist Access and Return Result')],
 'P2': [('P21','2.1 Authorize Reference Change'),('P22','2.2 Validate Mappings, Prices and Workflow'),('P23','2.3 Persist Versioned Reference Data')],
 'P3': [('P31','3.1 Load Authorized Draft and Reference Data'),('P32','3.2 Validate Items and Calculate Quarter Totals'),('P33','3.3 Validate and Store Private Attachments'),('P34','3.4 Save Draft or Create Revision'),('P35','3.5 Freeze and Submit Version'),('P36','3.6 Build Process Audit Event')],
 'P4': [('P41','4.1 Create Review Instance and Load Packet'),('P42','4.2 Validate Reviewer, Stage and Decision'),('P43','4.3 Record Decision and Update Version State')],
 'P5': [('P51','5.1 Authorize Report and Select Versions'),('P52','5.2 Aggregate Quarters and Preserve Lineage'),('P53','5.3 Persist Report and Generate Export')],
 'P6': [('P61','6.1 Persist and Consume Committed Events'),('P62','6.2 Redact and Append Audit Entries'),('P63','6.3 Resolve Recipients and Maintain Inbox'),('P64','6.4 Authorize and Serve Audit History')],
}
internal_packets={
 'VERIFIED_ACCESS_CHANGE':'validated account/role/membership mutation, authorized actor, expected revision',
 'VALID_SETUP':'authorized setup operation, proposed records, mapping and validation context',
 'VALID_REFERENCE':'validated reference IDs and effective-dated records, workflow version',
 'DRAFT_CONTEXT':'authorized request, owned group and plan/version, catalog snapshot, price policy, existing review comments and requested operation',
 'CALCULATED_DRAFT':'validated version items, four quarter quantities, decimal quarter amounts, annual item and plan totals, validation findings, expected lock_version',
 'ATTACHMENT_MANIFEST':'version_id, validated attachment IDs, checksums, sizes and storage references; no public URLs',
 'SAVED_DRAFT':'saved version_id, lock_version, item/totals snapshot, attachment manifest, save result or submission intent',
 'REVIEW_CONTEXT':'immutable version_id/content, stage instance and assignee, current authority, allocation context, prior decisions and optional requested decision',
 'VALID_DECISION':'authorized actor, stage/version IDs, decision/comment, expected stage revision and permitted next state',
 'REPORT_SOURCE':'authorized report request, exact version IDs and approval evidence, item-quarter rows, group mappings and requested output format',
 'AGGREGATED_REPORT':'grouped quantities/amounts, source version-item-quarter lineage, coverage warnings and reproducible filter/selection snapshot',
 'COMMITTED_EVENT':'unique committed event payload with domain outcome, safe audit fields and recipient rule; rolled-back mutations never emitted as successes',
 'AUDIT_QUERY_EVENT':'audit-view actor, filters/scope, timestamp and result count; no duplication of raw sensitive payload',
 'REVIEW_ACCESS':'verified actor_id, assigned review instance/stage, permitted department/global scope, allowed read/decision operations or denial; authorization required before content/file retrieval',
}
packets.update(internal_packets)

def target(parent,fid,s,t):
    num=int(fid[1:])
    if parent=='P1':
        if num in (1,2,5): return 'P11'
        if num==3:return 'P12'
        return 'P13'
    if parent=='P2':
        if num in (7,9):return 'P21'
        if num==10:return 'P22'
        return 'P23'
    if parent=='P3':
        if num in (12,14,15,16,17,21):return 'P31'
        if num in (13,19,20):return 'P33'
        if num==18:return 'P34'
        if num==62:return 'P36'
        return 'P35'
    if parent=='P4':
        if num in (24,27,30,33,35):return 'P42'
        if num in (40,41,63):return 'P43'
        return 'P41'
    if parent=='P5':
        if num in (42,43,45,46,47,48):return 'P51'
        return 'P53'
    if parent=='P6':
        if num in (51,52,55):return 'P63'
        if num in (53,54,56):return 'P64'
        if num==57:return 'P62'
        return 'P61'

internal={
 'P1':[('P11','P12','Authenticated administrator context','AUTH_RESULT'),('P11','P13','Validated session outcome','AUTH_RESULT'),('P12','P13','Authorized access mutation','VERIFIED_ACCESS_CHANGE'),('P13','P11','Persisted session result','AUTH_RESULT')],
 'P2':[('P21','P22','Authorized reference-data proposal','VALID_SETUP'),('P22','P23','Validated reference changes','VALID_REFERENCE')],
 'P3':[('P31','P32','Authorized draft context','DRAFT_CONTEXT'),('P32','P34','Validated quarterly values and totals','CALCULATED_DRAFT'),('P32','P31','Field validation errors','DRAFT_RESULT'),('P31','P33','Authorized attachment context','DRAFT_CONTEXT'),('P33','P34','Validated attachment manifest','ATTACHMENT_MANIFEST'),('P33','P31','Attachment result or authorized bytes','DRAFT_RESULT'),('P34','P31','Saved draft or validation result','DRAFT_RESULT'),('P34','P35','Saved version and submission intent','SAVED_DRAFT'),('P35','P34','Frozen submission snapshot to persist','SUBMISSION'),('P35','P31','Submission receipt or validation errors','DRAFT_RESULT'),('P34','P36','Draft/revision change event','DOMAIN_EVENT'),('P33','P36','Attachment access/change event','DOMAIN_EVENT'),('P35','P36','Submission event','DOMAIN_EVENT')],
 'P4':[('P41','P42','Version, workflow and authority context','REVIEW_CONTEXT'),('P42','P43','Validated decision','VALID_DECISION'),('P43','P41','Updated stage and decision receipt','REVIEW_PACKET'),('P41','P43','Initial review instance and stage assignment','REVIEW_WRITE'),('P42','P41','Decision validation result','REVIEW_PACKET'),('P41','P42','Packet access request','REVIEW_QUERY'),('P42','P41','Authorized reviewer scope or denial','REVIEW_ACCESS')],
 'P5':[('P51','P52','Selected version-item-quarter records','REPORT_SOURCE'),('P52','P53','Aggregates, source lineage and warnings','AGGREGATED_REPORT')],
 'P6':[('P61','P62','Committed event for audit','COMMITTED_EVENT'),('P61','P63','Committed event for recipient resolution','COMMITTED_EVENT'),('P63','P61','Inbox query and acknowledgement','INBOX_QUERY'),('P61','P63','Recipient-owned stored messages','INBOX_RESULT'),('P63','P61','New messages and read-state updates','OUTBOX_WRITE'),('P63','P64','Verified audit-reader authority','ACCESS_RECORDS'),('P64','P62','Audit-read trace','AUDIT_QUERY_EVENT')],
}

all_internal=[]
for parent,subs in subprocesses.items():
    graph=[]
    for fid,s,t,label,packet in flows:
        if parent not in (s,t):continue
        replacement=target(parent,fid,s,t)
        graph.append((fid,replacement if s==parent else s,replacement if t==parent else t,label,packet))
    for idx,(s,t,label,packet) in enumerate(internal[parent],1):
        edge=(f'{parent[1:]}.{idx:02}',s,t,label,packet)
        graph.append(edge);all_internal.append(edge)
    extra={k:('usecase',label.replace(' ', '\n', 1)) for k,label in subs}
    name=f'0{int(parent[1:])+1}_level2_{parent.lower()}'
    diagram(name,f'PPMP - Level 2 decomposition of {parent[1:]}.0',graph,extra)

register=['# PPMP data-flow register','','F identifiers match Level 1 and the corresponding Level 2 boundary exactly. Decimal IDs are internal Level 2 flows.','','| Flow | Source | Destination | Payload | Fields |','|---|---|---|---|---|']
for fid,s,t,label,packet in flows+all_internal:
    register.append(f'| {fid} | {s} | {t} | {label} (`{packet}`) | {packets[packet]} |')
(OUT/'FLOW_REGISTER.md').write_text('\n'.join(register)+'\n',encoding='utf-8')

# Structural verification, not a PlantUML rendering test.
for path in OUT.glob('*.puml'):
    text=path.read_text(encoding='utf-8')
    assert text.count('@startuml')==1 and text.count('@enduml')==1,path
    declared=set(re.findall(r'^(?:rectangle|usecase|database) ".*" as (\w+)$',text,re.M))
    for src,dst in re.findall(r'^(\w+) --> (\w+) :',text,re.M):
        assert src in declared and dst in declared,(path,src,dst)
    assert not re.search(r'^D\d+ --> D\d+',text,re.M),path
for parent in subprocesses:
    path=OUT/f'0{int(parent[1:])+1}_level2_{parent.lower()}.puml'
    text=path.read_text(encoding='utf-8')
    expected={fid for fid,s,t,_,_ in flows if parent in (s,t)}
    actual=set(re.findall(r': (F\d+) ',text))
    assert actual==expected,(parent,actual^expected)
assert set(re.findall(r': (F\d+) ',(OUT/'00_context.puml').read_text())) == {fid for fid,s,t,_,_ in flows if s in external or t in external}
print(f'Created and structurally checked {len(list(OUT.glob("*.puml")))} PlantUML diagrams, {len(flows)} Level 1 flows and {len(all_internal)} internal flows.')
