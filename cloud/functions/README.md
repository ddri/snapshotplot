# Edge Functions (placeholders)

Implement the following functions in your Supabase project (Deno runtime):

- `snapshots-publish` (POST):
  - Validate auth (Bearer token)
  - Parse JSON body per CLOUD_BACKEND_SPEC.md
  - Insert a pending snapshot row
  - Generate signed upload URLs (or function URLs) for `code` and optional `plot`
  - Return `{ snapshot_id, upload_urls }`

- `upload-artifact` (PUT):
  - Receive raw body, content-type
  - Validate query params: `project_id`, `snapshot_id`, `artifact`, `token`
  - Stream to Supabase Storage bucket by artifact type
  - Update snapshot row with object URL

- `snapshots-finalize` (POST):
  - Validate auth
  - Mark snapshot as `complete`
  - Optionally emit event/webhook for UI updates

Use the spec and SQL in this folder as a guide. Deploy with `supabase functions deploy ...`. 