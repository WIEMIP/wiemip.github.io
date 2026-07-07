/* ---------------------------------------------------------------------------
   WIEMIP client configuration.

   This file is PUBLIC (GitHub Pages serves it to anyone). Only put values here
   that are safe to expose:

   - SUPABASE_URL and SUPABASE_ANON_KEY are designed to be public. Security is
     enforced by Row Level Security (RLS) policies in Supabase, NOT by hiding
     the key. See SETUP.md.
   - NEVER put the Supabase `service_role` key (or any secret) in this file.

   Fill in the two values below after creating your Supabase project.
   Until you do, /submit shows a friendly "not configured yet" notice.
   --------------------------------------------------------------------------- */

window.WIEMIP_CONFIG = {
  SUPABASE_URL: "https://YOUR-PROJECT-REF.supabase.co",
  SUPABASE_ANON_KEY: "YOUR-SUPABASE-ANON-PUBLIC-KEY",

  // Table that submissions are written to (created in SETUP.md).
  TABLE: "model_submissions",

  // Optional: restrict who may submit to specific GitHub usernames.
  // Leave as [] to allow any signed-in GitHub user. This is a convenience
  // gate only — the real enforcement lives in your Supabase RLS policy.
  ALLOWED_GITHUB_USERS: [],
};
