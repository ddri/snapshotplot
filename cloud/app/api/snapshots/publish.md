# API: POST /api/snapshots/publish

- Validate `Authorization: Bearer <token>`
- Read JSON per `CLOUD_BACKEND_SPEC.md`
- Insert row into `snapshots` with status=pending
- Generate signed upload URLs (or proxy URLs) for `code` and optional `plot`
- Return `{ snapshot_id, upload_urls }`

Supabase hints:
- Use `@supabase/supabase-js` with service role on the server.
- For signed upload URLs, you can generate short-lived storage signed URLs or expose a server PUT route that streams to storage. 