# Testing the PPMP application

The first testable Laravel release is in `app/`. It uses Laravel 12.69.3, the installed PHP 8.2.12, Blade views, local CSS/JavaScript and a SQLite database. No Node build, MySQL setup or external CDN is needed to run this release.

## Open the site

Visit http://127.0.0.1:8000 on this computer.

| Test department | Email |
|---|---|
| Mayor's Office (Demo) | mayor@ppmp.test |
| Budget Office (Demo) | budget@ppmp.test |

Both accounts initially use the password you set as `PPMP_DEMO_PASSWORD` in your local `app/.env` before seeding. Existing accounts keep their current password when seeding again. Local credentials are not included in the repository.

These are local demonstration accounts. They do not establish official department ownership or real employees' access. Do not expose this seeded application on a public server.

## If the site is not running

Double-click `start-ppmp.cmd` in the project folder and keep its terminal open while testing. Alternatively, open PowerShell:

```powershell
Set-Location 'C:\Users\arnaut\OneDrive\Desktop\PPMP\app'
php artisan serve --host=127.0.0.1 --port=8000
```

If port 8000 is already in use, first open the URL: the application may already be running. Do not start another instance unnecessarily. To run a separate instance use `--port=8001` and browse to that port. The server started during development runs in a hidden background PHP process; its process ID is in `app/storage/server.pid` and its output is in `app/storage/logs/server-*.log`. Rebooting the computer may stop it; the startup command above restarts it. Stop a foreground Artisan server with Ctrl+C.

## Manual walkthrough

1. Sign in as `mayor@ppmp.test` and open the FY 2027 sample draft.
2. The ACETATE sample uses a unit price of PHP 1,493.00. Q1=2, Q2=1, Q3=0, Q4=1 gives PHP 5,972.00 annually.
3. Change Q1 to 3. The live preview should show PHP 4,479.00 for Q1 and PHP 7,465.00 for the annual amount. Click **Save quantities**, then reload to check persistence. The dashboard updates after saving.
4. Search the catalog in the draft editor and add another item. It starts with blank quantities. Fill Q1-Q4, optionally add remarks, and save. A blank quarter is missing input; entering zero explicitly records no demand.
5. Open **Item catalog**, search by description and filter by expenditure category. Entries marked **Needs review** cannot be added. Repeated descriptions remain separate source rows.
6. Sign out, then sign in as `budget@ppmp.test`. You should see only the Budget Office sample draft, not the Mayor's Office changes.
7. While signed in as Budget, manually visit the Mayor draft URL copied in step 1. Expect **403 Forbidden**. Unauthorized add/update/remove requests are also covered by automated tests.
8. Open the same item in two tabs. Save a change in tab A; then try saving the older form in tab B. It should report that the item changed instead of overwriting tab A's saved values.
9. Remove a test line with **Remove item** and confirm. Only that draft line is removed; the shared catalog item remains.

The catalog is a test copy of the FY 2027 source catalog, with known data-quality exceptions disabled. Draft prices are copied from this reference catalog when a line is added and remain fixed on that line. Other selectable years use the same pilot reference prices; year-specific price management is not implemented. Do not use these drafts as official plans.

## Automated checks

```powershell
Set-Location 'C:\Users\arnaut\OneDrive\Desktop\PPMP\app'
php vendor\phpunit\phpunit\phpunit --colors=never
```

The suite uses an in-memory SQLite database and does not erase the demo database. Last verified result: **13 tests, 79 assertions passed**. Tests cover login/logout, rate limiting, department isolation on read/write/delete, spoofed ownership, duplicate annual drafts, quantity calculations, zero versus missing quantities, price snapshots, rounding, invalid inputs, disabled catalog items, concurrent-edit protection, mismatched line URLs, duplicate item handling and page rendering.

Browser verification also confirmed login, draft editing, server-calculated totals and saving. This is an initial functional release, not a completed production audit.

## Persistence and setup

Saved data is in `app/database/database.sqlite`. Keep this file to retain your drafts. Do not run `migrate:fresh` on a database whose data you want to keep. Runtime logs, session data, credentials and the SQLite database are not source artifacts to publish.

On a new development copy: run `composer install`, copy `.env.example` to `.env`, set `APP_ENV=local`, `APP_URL=http://127.0.0.1:8000`, `DB_CONNECTION=sqlite` and `PPMP_DEMO_PASSWORD` to a local test password; create an empty `database/database.sqlite` if absent; run `php artisan key:generate`, `php artisan migrate`, and `php artisan db:seed`. Seeding is permitted only in local/testing environments and does not reset existing accounts or drafts. Existing accounts retain their password on reseeding. Set `APP_DEBUG=false` for a user-facing test instance.

## Scope of this release

Implemented: individual demo logins, server-enforced department ownership, searchable shared catalog, one annual draft per department/year, add/edit/remove draft lines, quarterly amounts, draft totals, blank-input visibility, price snapshots and stale-edit checks. Mobile and desktop views are supported. All mutation forms use Laravel CSRF protection; login uses session regeneration and logout invalidation, following the [Laravel authentication documentation](https://laravel.com/docs/12.x/authentication). Per-draft permissions use [Laravel Policies](https://laravel.com/docs/12.x/authorization).

Not implemented yet: department/user administration screens, multiple memberships, reporting-group ownership, annual price administration, attachments, submission/revision workflow, approvals, consolidated exports, audit history, notifications, password-reset email and production deployment. The two demo departments are explicit test fixtures; the other workbook reporting groups have not been assigned invented owners.

Laravel 12 is used to match the existing PHP 8.2 installation. Before production, plan a supported PHP/Laravel upgrade and confirm business workflow, real ownership, backup strategy and hosting. The published Laravel 12 security-support end date is 24 February 2027: https://laravel.com/docs/13.x/releases.
