# Supabase Keep-Alive Cron Job (Reusable Guide)

Supabase **free-tier** projects are paused after ~7 days of inactivity. This guide sets up a free GitHub Actions cron job that pings your database every 3 days so it never pauses.

Works for any website/project that has a Supabase backend — no server needed.

---

## 1. Create the workflow file

In your project repo, create `.github/workflows/keep_alive.yml`:

```yaml
name: Keep Supabase Active

on:
  schedule:
    - cron: '0 0 */3 * *'   # every 3 days at 00:00 UTC
  workflow_dispatch:          # lets you trigger it manually from the Actions tab

jobs:
  ping_supabase:
    runs-on: ubuntu-latest
    steps:
      - name: Send API Request
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        run: |
          curl -sf -o /dev/null -w "HTTP %{http_code}\n" \
            "$SUPABASE_URL/rest/v1/TABLE_NAME?select=id&limit=1" \
            -H "apikey: $SUPABASE_ANON_KEY" \
            -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

**Replace `TABLE_NAME`** with any real table in your project (e.g. `contacts`).

> ⚠️ **Important — learned the hard way:** do NOT ping the bare `/rest/v1/` root.
> It returns **401 UNAUTHORIZED_INVALID_API_KEY_TYPE** even with a valid anon key.
> You must query an actual table.

> The `-f` flag makes curl exit non-zero on HTTP errors, so a failing ping shows
> as a red ❌ in the Actions tab instead of silently "succeeding".

## 2. Get your Supabase credentials

Supabase Dashboard → your project → **Settings → API**:

- **Project URL** — e.g. `https://abcdefgh.supabase.co`
- **anon / public key** — the long JWT starting with `eyJ...`

## 3. Add the secrets to GitHub

**Option A — web UI:** repo → Settings → Secrets and variables → Actions → *New repository secret*:

| Name | Value |
|---|---|
| `SUPABASE_URL` | your project URL |
| `SUPABASE_ANON_KEY` | your anon key |

**Option B — gh CLI (faster):**

```bash
gh secret set SUPABASE_URL --body "https://YOUR_PROJECT.supabase.co"
gh secret set SUPABASE_ANON_KEY --body "eyJ...your-anon-key..."
```

## 4. Push and test

```bash
git add .github/workflows/keep_alive.yml
git commit -m "Add Supabase keep-alive workflow"
git push
```

Then trigger a test run immediately (don't wait 3 days):

```bash
gh workflow run keep_alive.yml
sleep 15
gh run list --workflow=keep_alive.yml --limit 1
```

Or via web: repo → **Actions** tab → "Keep Supabase Active" → **Run workflow**.

Verify the log shows `HTTP 200`:

```bash
gh run view --log | grep "HTTP"
```

## 5. Done

- Runs automatically every 3 days — nothing to maintain.
- If Supabase ever rejects the ping, the run fails visibly in the Actions tab.
- The anon key is safe to use here (it's the same public key your website ships to browsers), but keeping it in secrets avoids hardcoding.

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| `HTTP/2 401` + `UNAUTHORIZED_INVALID_API_KEY_TYPE` | You're pinging `/rest/v1/` root — point it at a real table instead |
| `401` on a table endpoint | Wrong/missing secret — re-check `SUPABASE_ANON_KEY` value |
| `ERR_NAME_NOT_RESOLVED` / DNS failure | Project is already paused — restore it manually in the Supabase dashboard first |
| Run never appears | Workflow file must be on the default branch; cron also needs repo activity (GitHub disables schedules on repos untouched for 60 days — the workflow_dispatch trigger lets you re-enable) |
| `404` on table | Table name typo, or table is in a non-`public` schema |
