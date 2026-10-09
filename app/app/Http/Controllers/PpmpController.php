<?php
namespace App\Http\Controllers;
use App\Models\{Draft,DraftLine,CatalogItem};
use Illuminate\Http\Request;
use Illuminate\Support\Facades\{Gate,DB};
use Illuminate\Validation\ValidationException;
class PpmpController extends Controller {
    public function dashboard(Request $request) {
        $drafts=Draft::where('department_id',$request->user()->department_id)->with('lines')->orderByDesc('year')->get();
        return view('dashboard',compact('drafts'));
    }
    public function create(Request $request) {
        abort_unless($request->user()->department_id,403);
        $data=$request->validate(['year'=>['required','integer','between:2026,2040']]);
        $draft=Draft::firstOrCreate(['department_id'=>$request->user()->department_id,'year'=>$data['year']],['created_by'=>$request->user()->id]);
        return redirect()->route('drafts.show',$draft)->with('status','Your department draft is ready.');
    }
    public function show(Request $request,Draft $draft) {
        Gate::authorize('view',$draft);
        $data=$request->validate(['q'=>['nullable','string','max:120']]);
        $draft->load(['lines','department']);
        $items=CatalogItem::where('available',true)->when($data['q']??null,fn($query,$term)=>$query->where('description','like','%'.$term.'%'))->orderBy('id')->paginate(8)->withQueryString();
        return view('drafts.show',compact('draft','items'));
    }
    public function catalog(Request $request) {
        $data=$request->validate(['q'=>['nullable','string','max:120'],'category'=>['nullable','string','max:255']]);
        $items=CatalogItem::query()->when($data['q']??null,fn($query,$q)=>$query->where('description','like','%'.$q.'%'))->when($data['category']??null,fn($query,$cat)=>$query->where('category',$cat))->orderBy('id')->paginate(25)->withQueryString();
        $categories=CatalogItem::select('category')->distinct()->orderBy('category')->pluck('category');
        return view('catalog',compact('items','categories'));
    }
    private function quantities(Request $request): array {
        $rules=['remarks'=>['nullable','string','max:1000']];
        foreach(range(1,4) as $q) $rules['q'.$q]=['nullable','regex:/^\d{1,5}(\.\d{1,3})?$/'];
        $data=$request->validate($rules); $values=['remarks'=>$data['remarks']??null];
        foreach(range(1,4) as $q) {
            $input=$data['q'.$q]??null;
            if($input===null) { $values['q'.$q.'_milli']=null; continue; }
            $parts=explode('.',(string)$input);
            $values['q'.$q.'_milli']=((int)$parts[0])*1000+(int)str_pad($parts[1]??'',3,'0');
        }
        return $values;
    }
    public function add(Request $request,Draft $draft) {
        Gate::authorize('update',$draft);
        $data=$request->validate(['catalog_item_id'=>['required','integer','exists:catalog_items,id']]);
        $values=$this->quantities($request); $item=CatalogItem::findOrFail($data['catalog_item_id']);
        if(!$item->available) throw ValidationException::withMessages(['catalog_item_id'=>'This item needs catalog review before use.']);
        $line=$draft->lines()->firstOrCreate(['catalog_item_id'=>$item->id],array_merge($values,[
            'description'=>$item->description,'category'=>$item->category,'unit'=>$item->unit,'unit_cost_cents'=>$item->unit_cost_cents,
        ]));
        if(!$line->wasRecentlyCreated) throw ValidationException::withMessages(['catalog_item_id'=>'This item is already in your draft. Edit its quantities below.']);
        $draft->touch();
        return redirect()->route('drafts.show',$draft)->with('status','Item added. Quantities and amounts have been saved.');
    }
    public function update(Request $request,Draft $draft,DraftLine $line) {
        Gate::authorize('update',$draft); abort_unless($line->draft_id===$draft->id,404);
        $request->validate(['revision'=>['required','integer','min:1']]); $values=$this->quantities($request);
        DB::transaction(function() use($draft,$line,$request,$values) {
            $changed=DraftLine::whereKey($line->id)->where('revision',$request->integer('revision'))->update(array_merge($values,['revision'=>DB::raw('revision + 1'),'updated_at'=>now()]));
            if(!$changed) throw ValidationException::withMessages(['revision'=>'This item changed in another tab. Reload the draft before editing again.']);
            $draft->touch();
        });
        return redirect()->route('drafts.show',$draft)->with('status','Item quantities saved.');
    }
    public function remove(Request $request,Draft $draft,DraftLine $line) {
        Gate::authorize('update',$draft); abort_unless($line->draft_id===$draft->id,404);
        $data=$request->validate(['revision'=>['required','integer','min:1']]);
        $deleted=DraftLine::whereKey($line->id)->where('revision',$data['revision'])->delete();
        if(!$deleted) throw ValidationException::withMessages(['revision'=>'This item changed. Reload before removing it.']);
        $draft->touch();
        return redirect()->route('drafts.show',$draft)->with('status','Item removed from this draft.');
    }
}
