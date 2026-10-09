<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>@yield('title', 'PPMP Workspace')</title><link rel="stylesheet" href="{{ asset('ppmp.css') }}"><script src="{{ asset('ppmp.js') }}" defer></script></head>
<body>
@auth
<aside class="sidebar"><a class="brand" href="{{ route('dashboard') }}"><span class="brand-mark">P</span><span>PPMP<span class="brand-sub">DEPARTMENT WORKSPACE</span></span></a><div class="nav-label">PLANNING</div><nav><a class="{{ request()->routeIs('dashboard','drafts.*') ? 'active' : '' }}" href="{{ route('dashboard') }}">◫ <span>My procurement plans</span></a><a class="{{ request()->routeIs('catalog') ? 'active' : '' }}" href="{{ route('catalog') }}">▦ <span>Item catalog</span></a></nav><div class="sidebar-bottom"><div class="avatar">{{ substr(auth()->user()->name,0,1) }}</div><strong>{{ auth()->user()->name }}</strong><small>{{ auth()->user()->department?->name ?? 'No department assigned' }}</small><form method="post" action="{{ route('logout') }}">@csrf<button class="signout">Sign out →</button></form></div></aside>
<div class="shell"><header class="topbar"><span>{{ auth()->user()->department?->name ?? 'PPMP workspace' }}</span><span class="badge amber">LOCAL TEST VERSION</span><form class="mobile-signout" method="post" action="{{ route('logout') }}">@csrf<button class="signout">Sign out</button></form></header><main>
@else
<main class="login-main">
@endauth
@if(session('status'))<div role="status" class="notice success">{{ session('status') }}</div>@endif
@if($errors->any())<div role="alert" class="notice error"><strong>Please check your entry.</strong><ul>@foreach($errors->all() as $error)<li>{{ $error }}</li>@endforeach</ul></div>@endif
@yield('content')
</main>@auth</div>@endauth
</body></html>
