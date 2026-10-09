@echo off
cd /d "%~dp0app"
echo Open http://127.0.0.1:8000 in your browser.
echo Keep this window open while testing. Press Ctrl+C to stop.
php artisan serve --host=127.0.0.1 --port=8000
pause
