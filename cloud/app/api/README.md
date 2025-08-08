# Next.js API Routes (docs)

Implement these routes in `cloud/app` if you choose to host the cloud app inside this repo:

- `POST /api/snapshots/publish`: see `cloud/app/api/snapshots/publish.md`
- `PUT /api/snapshots/upload-artifact`: stream uploaded code/plot to Supabase Storage and update snapshot row
- `POST /api/snapshots/finalize`: update snapshot status to `complete`

Use `@supabase/supabase-js` with the service role key, server-side only. Configure env via `cloud/app/env.example`. 