# API: POST /api/snapshots/finalize

Example implementation:

```ts
import { NextRequest, NextResponse } from 'next/server'
import { createServiceClient } from '@/lib/supabase'

export async function POST(req: NextRequest) {
  try {
    const auth = req.headers.get('authorization') || ''
    if (!auth.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    const body = await req.json()
    const { project_id, snapshot_id } = body || {}
    if (!project_id || !snapshot_id) {
      return NextResponse.json({ error: 'Missing project_id/snapshot_id' }, { status: 400 })
    }
    const supabase = createServiceClient()
    const { error } = await supabase
      .from('snapshots')
      .update({ status: 'complete' })
      .eq('id', snapshot_id)
      .eq('project_id', project_id)
    if (error) return NextResponse.json({ error: error.message }, { status: 500 })
    return NextResponse.json({ status: 'ok' })
  } catch (e: any) {
    return NextResponse.json({ error: String(e) }, { status: 500 })
  }
}
``` 