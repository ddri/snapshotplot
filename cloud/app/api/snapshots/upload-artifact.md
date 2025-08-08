# API: PUT /api/snapshots/upload-artifact

Example implementation (Next.js Route Handler):

```ts
import { NextRequest, NextResponse } from 'next/server'
import { createServiceClient } from '@/lib/supabase'

export async function PUT(req: NextRequest) {
  try {
    // Optional bearer auth for extra protection
    const auth = req.headers.get('authorization') || ''
    if (!auth.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const url = new URL(req.url)
    const project_id = url.searchParams.get('project_id')
    const snapshot_id = url.searchParams.get('snapshot_id')
    const artifact = url.searchParams.get('artifact') // 'code' | 'plot'
    const token = url.searchParams.get('token') // validate if you issue one

    if (!project_id || !snapshot_id || !artifact) {
      return NextResponse.json({ error: 'Missing params' }, { status: 400 })
    }

    const contentType = req.headers.get('content-type') || 'application/octet-stream'
    const body = await req.arrayBuffer()

    const supabase = createServiceClient()
    const bucket = artifact === 'code' ? (process.env.BUCKET_CODE || 'code') : (process.env.BUCKET_PLOTS || 'plots')
    const key = `${project_id}/${snapshot_id}/${artifact === 'code' ? 'code.py' : 'plot.png'}`

    const { error: upErr } = await supabase.storage.from(bucket).upload(
      key,
      new Uint8Array(body),
      { contentType, upsert: true },
    )
    if (upErr) return NextResponse.json({ error: upErr.message }, { status: 500 })

    const { data: pub } = supabase.storage.from(bucket).getPublicUrl(key)
    const field = artifact === 'code' ? 'code_url' : 'plot_url'

    const { error: dbErr } = await supabase
      .from('snapshots')
      .update({ [field]: pub.publicUrl })
      .eq('id', snapshot_id)
      .eq('project_id', project_id)

    if (dbErr) return NextResponse.json({ error: dbErr.message }, { status: 500 })

    return NextResponse.json({ ok: true, url: pub.publicUrl })
  } catch (e: any) {
    return NextResponse.json({ error: String(e) }, { status: 500 })
  }
}
``` 