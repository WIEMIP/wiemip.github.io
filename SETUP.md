# WIEMIP site — setup

Static site for **https://wiemip.github.io**. Three parts:

| Page                       | What it does                                             |
| -------------------------- | ------------------------------------------------------- |
| `/`                        | Welcome page.                                            |
| `/hub`                     | Redirects to the data hub at `http://13.58.168.60`.     |
| `/submit`                  | GitHub-login-gated form; writes to a Supabase table.    |

The welcome page and hub redirect work with **zero configuration**. The submit
page needs a Supabase project (steps below).

---

## 1. Turn on GitHub Pages

1. Push this repo to `WIEMIP/wiemip.github.io` (already the `origin` remote).
2. GitHub → repo **Settings → Pages**.
3. **Source:** *Deploy from a branch*. **Branch:** `main`, folder `/ (root)`. Save.
4. Wait ~1 minute; the site goes live at `https://wiemip.github.io`.

Because the repo is named `wiemip.github.io`, it publishes at the root domain —
no extra config needed. `.nojekyll` is included so files are served as-is.

---

## 2. Point `/hub` wherever you want

Edit **`hub/index.html`** — change the two `http://13.58.168.60` occurrences
(the `<meta http-equiv="refresh">` URL and the button `href`).

> **Security note:** `13.58.168.60` is plain **HTTP**, so traffic to the hub is
> **not encrypted**. The redirect itself is fine (browsers allow HTTPS→HTTP
> top-level navigation), but if the hub server can serve **HTTPS** — or you can
> put a domain + TLS cert in front of it — prefer that.

---

## 3. Make `/submit` work (Supabase + GitHub OAuth)

The form is gated by **GitHub login**, handled by **Supabase Auth** (Supabase
speaks GitHub OAuth natively — you don't write any server code). Submissions go
into a Supabase table.

### 3a. Create a Supabase project
1. Sign up at <https://supabase.com> → **New project**.
2. Copy from **Project Settings → API**:
   - **Project URL** → `SUPABASE_URL`
   - **anon / public** key → `SUPABASE_ANON_KEY`

> These two are **safe to publish**. The anon key is meant for browsers; access
> is controlled by Row Level Security (step 3d), not by keeping the key secret.
> **Never** put the `service_role` key on the site.

### 3b. Create a GitHub OAuth app
1. GitHub → **Settings → Developer settings → OAuth Apps → New OAuth App**
   (use the WIEMIP org: *Org Settings → Developer settings* if you want it
   owned by the org).
2. **Homepage URL:** `https://wiemip.github.io`
3. **Authorization callback URL:**
   `https://YOUR-PROJECT-REF.supabase.co/auth/v1/callback`
4. Create it, then **generate a client secret**. Keep the **Client ID** and
   **Client secret** for the next step.

### 3c. Enable GitHub in Supabase
1. Supabase → **Authentication → Providers → GitHub** → enable.
2. Paste the GitHub **Client ID** and **Client secret**. Save.
3. Supabase → **Authentication → URL Configuration**:
   - **Site URL:** `https://wiemip.github.io`
   - **Redirect URLs:** add `https://wiemip.github.io/submit/`
     (and `http://localhost:*` if you test locally).

### 3d. Create the table + lock it down with RLS
Supabase → **SQL Editor** → run:

```sql
create table if not exists public.model_submissions (
  id            uuid primary key default gen_random_uuid(),
  created_at    timestamptz not null default now(),
  user_id       uuid not null references auth.users (id),
  github_login  text,
  model_name    text not null,
  model_version text,
  institution   text not null,
  contact_email text not null,
  model_type     text,
  description    text not null,
  key_references text,   -- "references" is a reserved word in SQL; renamed
  notes          text
);

-- Row Level Security: default-deny. Nothing is readable/writable until a
-- policy explicitly allows it. This is what makes the public anon key safe.
alter table public.model_submissions enable row level security;

-- Logged-in users may insert, and only as themselves.
create policy "authenticated can insert own rows"
  on public.model_submissions for insert
  to authenticated
  with check (auth.uid() = user_id);

-- No SELECT/UPDATE/DELETE policy for anon/authenticated => the public site
-- cannot read, edit, or delete submissions. You read them in the Supabase
-- dashboard (Table editor) or via the service_role key on a trusted machine.
```

**Optional — restrict who can submit to specific GitHub users.** Two layers:

1. *Client convenience gate:* set `ALLOWED_GITHUB_USERS` in `assets/config.js`,
   e.g. `["alice", "bob"]`. Non-listed users see an "access denied" panel.
2. *Real enforcement (recommended)* — enforce it in the database too, since the
   client list is only a UI hint:

```sql
create policy "only approved github users can insert"
  on public.model_submissions for insert
  to authenticated
  with check (
    auth.uid() = user_id
    and lower(coalesce(auth.jwt() -> 'user_metadata' ->> 'user_name', ''))
        in ('alice', 'bob')   -- lowercase GitHub usernames
  );
```
(If you add this DB policy, drop the broader "authenticated can insert own
rows" policy so it doesn't override the allowlist.)

### 3e. Plug in the keys
Edit **`assets/config.js`**:

```js
window.WIEMIP_CONFIG = {
  SUPABASE_URL: "https://YOUR-PROJECT-REF.supabase.co",
  SUPABASE_ANON_KEY: "eyJhbGciOi...your anon key...",
  TABLE: "model_submissions",
  ALLOWED_GITHUB_USERS: [],   // or ["alice","bob"]
};
```

Commit + push. Visit `https://wiemip.github.io/submit`, sign in with GitHub,
submit — the row appears in Supabase → **Table editor → model_submissions**.

---

## Security summary

- **No secrets in the repo.** Only the Supabase URL + anon key live client-side,
  both public by design. The `service_role` key stays off the site entirely.
- **RLS is the real lock.** Default-deny + an insert-only policy means the public
  can add submissions but cannot read, edit, or delete anything.
- **Input is length-capped** in the form and typed in the DB; consider adding a
  Supabase rate limit / captcha if you get spam.
- **The hub link is plain HTTP** — unencrypted. Upgrade to HTTPS if you can.

## Local preview

```sh
python3 -m http.server 8000   # then open http://localhost:8000
```
GitHub login won't complete against `localhost` unless you add a localhost
redirect URL in Supabase (step 3c); the welcome page and hub redirect preview fine.
