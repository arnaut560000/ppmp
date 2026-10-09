<?php

use App\Http\Controllers\{AuthController,PpmpController};
use Illuminate\Support\Facades\Route;
Route::redirect('/','/dashboard');
Route::middleware('guest')->group(function () {
    Route::get('/login',[AuthController::class,'create'])->name('login');
    Route::post('/login',[AuthController::class,'store'])->middleware('throttle:20,1');
});
Route::middleware('auth')->group(function () {
    Route::post('/logout',[AuthController::class,'destroy'])->name('logout');
    Route::get('/dashboard',[PpmpController::class,'dashboard'])->name('dashboard');
    Route::get('/catalog',[PpmpController::class,'catalog'])->name('catalog');
    Route::post('/drafts',[PpmpController::class,'create'])->name('drafts.store');
    Route::get('/drafts/{draft}',[PpmpController::class,'show'])->name('drafts.show');
    Route::post('/drafts/{draft}/lines',[PpmpController::class,'add'])->name('lines.store');
    Route::put('/drafts/{draft}/lines/{line}',[PpmpController::class,'update'])->name('lines.update');
    Route::delete('/drafts/{draft}/lines/{line}',[PpmpController::class,'remove'])->name('lines.destroy');
});
