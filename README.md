# wiemip.github.io

Static site for the WIEMIP project, served at **https://wiemip.github.io**.

- **`/`** — welcome page (`index.html`)
- **`/hub`** — redirects to the data hub (`hub/index.html`)
- **`/submit`** — GitHub-login-gated model-info form backed by Supabase (`submit/index.html`)

Shared styling lives in `assets/styles.css`; the one place you paste credentials
is `assets/config.js`.

👉 **Setup & security details: [SETUP.md](SETUP.md)** — how to enable GitHub
Pages, change the hub link, and wire up Supabase + GitHub OAuth for `/submit`.

The welcome page and hub redirect work as-is. `/submit` shows a "not configured
yet" notice until you add your Supabase keys.
