<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class CatalogItem extends Model {
    protected $guarded = [];
    protected function casts(): array { return ['available'=>'boolean','unit_cost_cents'=>'integer']; }
}
