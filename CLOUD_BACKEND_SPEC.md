# Cloud Backend API Spec

This document defines the minimal API the cloud platform should implement to work with the `snapshotplot` publisher and CI workflow.

## Authentication
- All requests authenticate with `Authorization: Bearer <TOKEN>`
- CI uses a service-scoped token (e.g., Supabase service role or function-scoped secret)
- Users may publish via user JWT (optional)

## Endpoints

### POST /api/snapshots/publish
Request signed upload URLs (or perform allocation) and create a pending snapshot record.

Request body (JSON):
```json
{
  "project_id": "proj_123",
  "collection": "experiments",
  "title": "My Plot",
  "author": "Alice",
  "description": "...",
  "tags": ["ml", "demo"],
  "repo_owner": "org",
  "repo_name": "repo",
  "commit_sha": "abc123",
  "branch": "main",
  "pr_number": 42,
  "artifacts": { "plot": true, "code": true }
}
```

Response (JSON):
```json
{
  "snapshot_id": "snap_abc",
  "upload_urls": {
    "code": "https://.../upload/code/snap_abc?token=...",
    "plot": "https://.../upload/plot/snap_abc?token=..."
  },
  "expires_at": "2025-08-08T12:00:00Z"
}
```
Notes:
- The returned URLs must accept `PUT` with the raw file body and `Content-Type` header.
- The backend should stream the upload to object storage and tie artifacts to `snapshot_id`.

### POST /api/snapshots/finalize
Mark a snapshot as complete and ready for indexing.

Request body (JSON):
```json
{
  "project_id": "proj_123",
  "snapshot_id": "snap_abc"
}
```

Response (JSON):
```json
{ "status": "ok" }
```

## Storage layout (recommendation)
- Buckets: `plots`, `code`
- Object keys: `project_id/snapshot_id/plot.png`, `project_id/snapshot_id/code.py`
- Public URLs stored with snapshot record (or served via signed delivery)

## Database schema (minimal)
- `projects(id uuid pk, owner_id uuid, name text, created_at timestamptz)`
- `collections(id uuid pk, project_id uuid fk, name text, created_at)`
- `snapshots(id uuid pk, project_id uuid fk, collection_id uuid fk null, title text, author text, description text, tags text[] default '{}',
  plot_url text, code_url text, repo_owner text, repo_name text, commit_sha text, branch text, pr_number int, created_at timestamptz)`

## Security
- Enforce RLS by `project_id` and membership
- Validate that `project_id` in request is accessible by token principal
- Limit upload URL validity (short TTL, single-use tokens)

## Idempotency
- Allow client to safely retry `publish` (e.g., by returning existing `snapshot_id` for same `(project_id, commit_sha, title)` if desired)

## Error handling
- 401/403 for auth failures
- 400 for validation errors (missing project/collection)
- 5xx for transient storage/db errors

## Optional enhancements
- Support multipart direct upload at `/api/snapshots/publish` (metadata + files) as a simpler alternative to signed upload URLs
- Emit webhook/event for new snapshot to power live updates in the UI
- Attach CI metadata (workflow run id, job url) for traceability 