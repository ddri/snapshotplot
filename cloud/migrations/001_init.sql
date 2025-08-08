-- Minimal schema for SnapshotPlot cloud
create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null,
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists collections (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists snapshots (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  collection_id uuid references collections(id) on delete set null,
  title text,
  author text,
  description text,
  tags text[] not null default '{}',
  plot_url text,
  code_url text,
  repo_owner text,
  repo_name text,
  commit_sha text,
  branch text,
  pr_number int,
  status text not null default 'pending',
  created_at timestamptz not null default now()
);

-- Basic RLS (example; adjust to your auth model)
alter table projects enable row level security;
alter table collections enable row level security;
alter table snapshots enable row level security;

-- Allow owner to see their projects
create policy if not exists project_owner_access on projects
  for all
  using (auth.uid() = owner_id)
  with check (auth.uid() = owner_id);

-- Collections and snapshots inherit via project_id
create policy if not exists collections_project_access on collections
  for all
  using (exists (select 1 from projects p where p.id = collections.project_id and p.owner_id = auth.uid()))
  with check (exists (select 1 from projects p where p.id = collections.project_id and p.owner_id = auth.uid()));

create policy if not exists snapshots_project_access on snapshots
  for all
  using (exists (select 1 from projects p where p.id = snapshots.project_id and p.owner_id = auth.uid()))
  with check (exists (select 1 from projects p where p.id = snapshots.project_id and p.owner_id = auth.uid())); 