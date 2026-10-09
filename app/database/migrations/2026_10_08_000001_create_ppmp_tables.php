<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
return new class extends Migration {
    public function up(): void {
        Schema::create('departments', function (Blueprint $t) {
            $t->id(); $t->string('name'); $t->string('code')->unique(); $t->timestamps();
        });
        Schema::table('users', fn(Blueprint $t) => $t->foreignId('department_id')->nullable()->constrained()->restrictOnDelete());
        Schema::create('catalog_items', function (Blueprint $t) {
            $t->id(); $t->string('source_key')->unique(); $t->text('description'); $t->string('category');
            $t->string('unit')->nullable(); $t->unsignedBigInteger('unit_cost_cents')->nullable();
            $t->boolean('available')->default(false); $t->string('issue')->nullable(); $t->timestamps();
        });
        Schema::create('drafts', function (Blueprint $t) {
            $t->id(); $t->foreignId('department_id')->constrained()->restrictOnDelete();
            $t->foreignId('created_by')->constrained('users')->restrictOnDelete();
            $t->unsignedSmallInteger('year'); $t->timestamps(); $t->unique(['department_id','year']);
        });
        Schema::create('draft_lines', function (Blueprint $t) {
            $t->id(); $t->foreignId('draft_id')->constrained()->cascadeOnDelete();
            $t->foreignId('catalog_item_id')->constrained()->restrictOnDelete();
            $t->text('description'); $t->string('category'); $t->string('unit'); $t->unsignedBigInteger('unit_cost_cents');
            foreach (range(1,4) as $q) $t->unsignedBigInteger('q'.$q.'_milli')->nullable();
            $t->text('remarks')->nullable(); $t->unsignedInteger('revision')->default(1); $t->timestamps();
            $t->unique(['draft_id','catalog_item_id']);
        });
    }
    public function down(): void {
        Schema::dropIfExists('draft_lines'); Schema::dropIfExists('drafts'); Schema::dropIfExists('catalog_items');
        Schema::table('users', fn(Blueprint $t) => $t->dropConstrainedForeignId('department_id'));
        Schema::dropIfExists('departments');
    }
};
