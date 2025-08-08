# Supabase Client (server-side)

Use `@supabase/supabase-js` with the service role key on the server only.

```ts
// cloud/app/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

export function createServiceClient() {
  const url = process.env.SUPABASE_URL!
  const key = process.env.SUPABASE_SERVICE_ROLE!
  if (!url || !key) throw new Error('Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE')
  return createClient(url, key, { auth: { persistSession: false } })
}
```

Insert pending snapshot and return IDs:
```ts
import { createServiceClient } from '@/lib/supabase'

export async function insertPendingSnapshot(input: {
  project_id: string
  collection?: string
  title?: string
  author?: string
  description?: string
  tags?: string[]
  repo_owner?: string
  repo_name?: string
  commit_sha?: string
  branch?: string
  pr_number?: number
}) {
  const supabase = createServiceClient()
  // Optional: resolve collection_id by name
  let collection_id: string | null = null
  if (input.collection) {
    const { data: col } = await supabase
      .from('collections')
      .select('id')
      .eq('project_id', input.project_id)
      .eq('name', input.collection)
      .maybeSingle()
    collection_id = col?.id ?? null
  }
  const { data, error } = await supabase
    .from('snapshots')
    .insert({
      project_id: input.project_id,
      collection_id,
      title: input.title,
      author: input.author,
      description: input.description,
      tags: input.tags ?? [],
      repo_owner: input.repo_owner,
      repo_name: input.repo_name,
      commit_sha: input.commit_sha,
      branch: input.branch,
      pr_number: input.pr_number,
      status: 'pending',
    })
    .select('id')
    .single()
  if (error) throw error
  return data!.id as string
}
```

Create signed upload URLs (option A) or return proxy URLs (option B):
```ts
import { createServiceClient } from '@/lib/supabase'

export async function createSignedUploadUrls(args: {
  project_id: string
  snapshot_id: string
  needPlot: boolean
}) {
  const supabase = createServiceClient()
  const prefix = `${args.project_id}/${args.snapshot_id}`

  const urls: Record<string, string> = {}
  // Supabase Storage Signed URL (PUT not supported) — use upload via server route instead.
  // Option B: return proxy URLs to your own upload route (recommended):
  // `/api/snapshots/upload-artifact?project_id=...&snapshot_id=...&artifact=code&token=...`
  return urls
}
```

Proxy upload handler example (server streams to Storage):
```ts
import { NextRequest, NextResponse } from 'next/server'
import { createServiceClient } from '@/lib/supabase'

export async function PUT(req: NextRequest) {
  const url = new URL(req.url)
  const project_id = url.searchParams.get('project_id')!
  const snapshot_id = url.searchParams.get('snapshot_id')!
  const artifact = url.searchParams.get('artifact')! // 'code' | 'plot'
  const contentType = req.headers.get('content-type') || 'application/octet-stream'

  const body = await req.arrayBuffer()
  const supabase = createServiceClient()
  const bucket = artifact === 'code' ? (process.env.BUCKET_CODE || 'code') : (process.env.BUCKET_PLOTS || 'plots')
  const key = `${project_id}/${snapshot_id}/${artifact === 'code' ? 'code.py' : 'plot.png'}`
  const { data, error } = await supabase.storage.from(bucket).upload(key, new Uint8Array(body), { contentType, upsert: true })
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })

  const { data: pub } = supabase.storage.from(bucket).getPublicUrl(key)
  const field = artifact === 'code' ? 'code_url' : 'plot_url'
  await supabase.from('snapshots').update({ [field]: pub.publicUrl }).eq('id', snapshot_id)

  return NextResponse.json({ ok: true, url: pub.publicUrl })
}
```

Finalize snapshot:
```ts
import { createServiceClient } from '@/lib/supabase'

export async function finalizeSnapshot(project_id: string, snapshot_id: string) {
  const supabase = createServiceClient()
  const { error } = await supabase
    .from('snapshots')
    .update({ status: 'complete' })
    .eq('id', snapshot_id)
    .eq('project_id', project_id)
  if (error) throw error
}
``` 