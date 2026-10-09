<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
class DraftLine extends Model {
    protected $guarded = [];
    public function draft(): BelongsTo { return $this->belongsTo(Draft::class); }
    public function amount(int $quarter): ?int {
        $qty = $this->{'q'.$quarter.'_milli'};
        return $qty === null ? null : intdiv((int)$qty * (int)$this->unit_cost_cents + 500,1000);
    }
    public function quantity(int $quarter): string {
        $value = $this->{'q'.$quarter.'_milli'};
        return $value === null ? '' : rtrim(rtrim(number_format($value/1000,3,'.',''),'0'),'.');
    }
    public function knownTotal(): int { return array_sum(array_map(fn($q) => $this->amount($q) ?? 0,range(1,4))); }
    public function complete(): bool { return collect(range(1,4))->every(fn($q) => $this->{'q'.$q.'_milli'} !== null); }
}
