<?php

namespace Database\Seeders;

use App\Models\{User,Department,CatalogItem,Draft};
use Illuminate\Support\Facades\DB;
// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        if (!app()->environment('local','testing')) throw new \RuntimeException('Demo seeding is only available in local or testing environments.');
        $password=config('ppmp.demo_password');
        if (!$password) throw new \RuntimeException('Set PPMP_DEMO_PASSWORD before seeding sample accounts.');
        $source=json_decode(file_get_contents(database_path('data/catalog.json')),true,512,JSON_THROW_ON_ERROR);
        DB::transaction(function () use($source,$password) {
            foreach(array_chunk($source,100) as $chunk) {
                $rows=[];
                foreach($chunk as $item) {
                    $cents=$item['unit_cost_numeric'] === null ? null : (int)bcmul(bcadd($item['unit_cost_numeric'],'0.005',4),'100',0);
                    $issue=[];
                    if(!$item['unit'] || in_array($item['unit'],['0','PIEXE'])) $issue[]='Unit needs review';
                    if($cents===null || $cents<0 || $cents>10000000000) $issue[]='Price needs review';
                    $rows[]=['source_key'=>$item['source_key'],'description'=>$item['description'],'category'=>$item['expense_object'],
                        'unit'=>$item['unit']?:null,'unit_cost_cents'=>$cents!==null && $cents>=0 ? $cents : null,
                        'available'=>!$issue,'issue'=>$issue?implode('; ',$issue):null,'created_at'=>now(),'updated_at'=>now()];
                }
                CatalogItem::insertOrIgnore($rows);
            }
            foreach ([['DEMO-MAYOR',"Mayor's Office (Demo)",'mayor@ppmp.test','Mayor Office Preparer'],['DEMO-BUDGET','Budget Office (Demo)','budget@ppmp.test','Budget Office Preparer']] as [$code,$name,$email,$person]) {
                $dept=Department::firstOrCreate(['code'=>$code],['name'=>$name]);
                $user=User::firstOrNew(['email'=>$email]);
                if(!$user->exists) { $user->name=$person; $user->password=$password; $user->department_id=$dept->id; $user->save(); }
                $draft=Draft::firstOrCreate(['department_id'=>$dept->id,'year'=>2027],['created_by'=>$user->id]);
                if($draft->wasRecentlyCreated) {
                    $item=CatalogItem::where('source_key','Sheet1:9')->firstOrFail();
                    $draft->lines()->create(['catalog_item_id'=>$item->id,'description'=>$item->description,'category'=>$item->category,
                        'unit'=>$item->unit,'unit_cost_cents'=>$item->unit_cost_cents,'q1_milli'=>2000,'q2_milli'=>1000,'q3_milli'=>0,'q4_milli'=>1000,'remarks'=>'Sample quantities for local testing.']);
                }
            }
        });
    }
}
