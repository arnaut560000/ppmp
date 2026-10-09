<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\{HasMany,BelongsTo};
class Draft extends Model {
    protected $guarded = [];
    public function lines(): HasMany { return $this->hasMany(DraftLine::class); }
    public function department(): BelongsTo { return $this->belongsTo(Department::class); }
}
