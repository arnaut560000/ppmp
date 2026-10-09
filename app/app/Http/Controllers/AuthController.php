<?php
namespace App\Http\Controllers;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\{Auth,RateLimiter};
use Illuminate\Validation\ValidationException;
class AuthController extends Controller {
    public function create() { return view('auth.login'); }
    public function store(Request $request) {
        $data=$request->validate(['email'=>['required','email','max:255'],'password'=>['required','string','max:1024']]);
        $key='login:'.hash('sha256',strtolower($data['email']).'|'.$request->ip());
        if(RateLimiter::tooManyAttempts($key,5)) throw ValidationException::withMessages(['email'=>'Too many attempts. Try again in '.RateLimiter::availableIn($key).' seconds.']);
        if(!Auth::attempt($data)) {
            RateLimiter::hit($key,60);
            throw ValidationException::withMessages(['email'=>'The email or password is incorrect.']);
        }
        RateLimiter::clear($key); $request->session()->regenerate();
        return redirect()->intended(route('dashboard'));
    }
    public function destroy(Request $request) {
        Auth::logout(); $request->session()->invalidate(); $request->session()->regenerateToken();
        return redirect()->route('login');
    }
}
