<?php
namespace Tests\Feature;
use App\Models\{User,Department,CatalogItem,Draft,DraftLine};
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class PpmpTest extends TestCase {
    use RefreshDatabase;
    private function account(string $code): User {
        $dept=Department::create(['name'=>$code,'code'=>$code]);
        return User::factory()->create(['department_id'=>$dept->id]);
    }
    private function draft(User $user): Draft {
        return Draft::create(['department_id'=>$user->department_id,'created_by'=>$user->id,'year'=>2027]);
    }
    private function item(array $overrides=[]): CatalogItem {
        return CatalogItem::create(array_merge(['source_key'=>'Sheet1:9','description'=>'ACETATE','category'=>'Office supplies','unit'=>'roll','unit_cost_cents'=>149300,'available'=>true],$overrides));
    }
    private function line(Draft $draft,CatalogItem $item): DraftLine {
        return $draft->lines()->create(['catalog_item_id'=>$item->id,'description'=>$item->description,'category'=>$item->category,'unit'=>$item->unit,'unit_cost_cents'=>$item->unit_cost_cents]);
    }
    public function test_guests_must_login_and_valid_login_can_logout(): void {
        $user=$this->account('A');
        $this->get('/dashboard')->assertRedirect('/login');
        $this->get('/catalog')->assertRedirect('/login');
        $this->post('/login',['email'=>$user->email,'password'=>'incorrect'])->assertSessionHasErrors('email');
        $this->assertGuest();
        $this->post('/login',['email'=>$user->email,'password'=>'password'])->assertRedirect('/catalog');
        $this->assertAuthenticatedAs($user);
        $this->post('/logout')->assertRedirect('/login'); $this->assertGuest();
    }
    public function test_login_is_rate_limited(): void {
        foreach(range(1,6) as $attempt) $response=$this->post('/login',['email'=>'nobody@example.test','password'=>'wrong']);
        $response->assertSessionHasErrors('email');
        $this->assertStringContainsString('Too many attempts',session('errors')->first('email'));
    }
    public function test_department_isolation_on_read_add_update_and_delete(): void {
        $a=$this->account('A');$b=$this->account('B');$draft=$this->draft($b);$item=$this->item();$line=$this->line($draft,$item);
        $this->actingAs($a)->get('/drafts/'.$draft->id)->assertForbidden();
        $this->post('/drafts/'.$draft->id.'/lines',['catalog_item_id'=>$item->id])->assertForbidden();
        $this->put('/drafts/'.$draft->id.'/lines/'.$line->id,['revision'=>1,'q1'=>'99'])->assertForbidden();
        $this->delete('/drafts/'.$draft->id.'/lines/'.$line->id,['revision'=>1])->assertForbidden();
        $this->get('/dashboard')->assertOk()->assertDontSee('/drafts/'.$draft->id.'"',false);
        $this->assertDatabaseHas('draft_lines',['id'=>$line->id,'q1_milli'=>null]);
    }
    public function test_new_draft_cannot_spoof_department_and_is_unique_per_year(): void {
        $a=$this->account('A');$b=$this->account('B');
        foreach(range(1,2) as $n) $this->actingAs($a)->post('/drafts',['year'=>2027,'department_id'=>$b->department_id])->assertRedirect();
        $this->assertDatabaseCount('drafts',1);$this->assertDatabaseHas('drafts',['department_id'=>$a->department_id]);
    }
    public function test_quantities_save_reopen_and_ignore_client_price(): void {
        $user=$this->account('A');$draft=$this->draft($user);$item=$this->item();
        $this->actingAs($user)->post('/drafts/'.$draft->id.'/lines',['catalog_item_id'=>$item->id,'q1'=>'2','q2'=>'0','q3'=>'1.250','q4'=>'','unit_cost_cents'=>1])->assertRedirect();
        $line=$draft->lines()->firstOrFail();
        $this->assertSame(298600,$line->amount(1));$this->assertSame(0,$line->amount(2));$this->assertSame(186625,$line->amount(3));$this->assertNull($line->amount(4));
        $this->assertFalse($line->complete());$this->assertEquals(149300,$line->unit_cost_cents);
        $this->get('/drafts/'.$draft->id)->assertOk()->assertSee('ACETATE')->assertSee('2,986.00')->assertSee('1,866.25');
    }
    public function test_rounding_and_price_snapshot_are_preserved(): void {
        $user=$this->account('A');$draft=$this->draft($user);$item=$this->item(['unit_cost_cents'=>1]);$line=$this->line($draft,$item);
        $item->update(['unit_cost_cents'=>99999]);
        $this->actingAs($user)->put('/drafts/'.$draft->id.'/lines/'.$line->id,['revision'=>1,'q1'=>'0.500','q2'=>'0','q3'=>'0','q4'=>'0'])->assertRedirect();
        $line->refresh();$this->assertSame(1,$line->amount(1));$this->assertTrue($line->complete());$this->assertEquals(1,$line->unit_cost_cents);
    }
    public function test_invalid_quantities_and_unavailable_catalog_items_are_rejected(): void {
        $user=$this->account('A');$draft=$this->draft($user);$item=$this->item();
        foreach(['-1','1.2345','100000','1e3'] as $invalid) $this->actingAs($user)->post('/drafts/'.$draft->id.'/lines',['catalog_item_id'=>$item->id,'q1'=>$invalid])->assertSessionHasErrors('q1');
        $item->update(['available'=>false]);
        $this->post('/drafts/'.$draft->id.'/lines',['catalog_item_id'=>$item->id])->assertSessionHasErrors('catalog_item_id');
        $this->assertDatabaseCount('draft_lines',0);
    }
    public function test_stale_edits_and_removals_do_not_overwrite_saved_changes(): void {
        $user=$this->account('A');$draft=$this->draft($user);$line=$this->line($draft,$this->item());$url='/drafts/'.$draft->id.'/lines/'.$line->id;
        $this->actingAs($user)->put($url,['revision'=>1,'q1'=>'5'])->assertRedirect();
        $this->put($url,['revision'=>1,'q1'=>'99'])->assertSessionHasErrors('revision');
        $this->delete($url,['revision'=>1])->assertSessionHasErrors('revision');
        $this->assertDatabaseHas('draft_lines',['id'=>$line->id,'q1_milli'=>5000,'revision'=>2]);
        $this->delete($url,['revision'=>2])->assertRedirect();$this->assertDatabaseMissing('draft_lines',['id'=>$line->id]);
    }
    public function test_line_cannot_be_addressed_under_another_draft(): void {
        $a=$this->account('A');$b=$this->account('B');$draft=$this->draft($a);$other=$this->draft($b);$line=$this->line($other,$this->item());
        $this->actingAs($a)->put('/drafts/'.$draft->id.'/lines/'.$line->id,['revision'=>1,'q1'=>'5'])->assertNotFound();
        $this->delete('/drafts/'.$draft->id.'/lines/'.$line->id,['revision'=>1])->assertNotFound();
    }
    public function test_duplicate_item_does_not_replace_existing_quantities(): void {
        $user=$this->account('A');$draft=$this->draft($user);$item=$this->item();
        $this->actingAs($user)->post('/drafts/'.$draft->id.'/lines',['catalog_item_id'=>$item->id,'q1'=>'2'])->assertRedirect();
        $this->post('/drafts/'.$draft->id.'/lines',['catalog_item_id'=>$item->id,'q1'=>'99'])->assertSessionHasErrors('catalog_item_id');
        $this->assertDatabaseCount('draft_lines',1);$this->assertDatabaseHas('draft_lines',['q1_milli'=>2000]);
    }
    public function test_catalog_search_and_dashboard_render(): void {
        $user=$this->account('A');$this->item();
        $this->actingAs($user)->get('/dashboard')->assertOk()->assertSee('My procurement plans');
        $this->get('/catalog?q=ACETATE')->assertOk()->assertSee('ACETATE');
        $this->get('/catalog?q=doesnotexist')->assertOk()->assertSee('No matching items');
    }
}
