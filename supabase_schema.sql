-- ============================================================
-- RAG CHATBOT — SUPABASE SCHEMA
-- Run this entire file in your Supabase SQL Editor
-- Dashboard → SQL Editor → New Query → paste → Run
-- ============================================================

-- Step 1: Enable the pgvector extension (allows storing embeddings)
create extension if not exists vector;

-- ============================================================
-- TABLE: documents
-- Tracks every uploaded PDF/TXT file
-- ============================================================
create table if not exists documents (
  id           uuid primary key default gen_random_uuid(),
  name         text not null,
  total_chunks integer not null default 0,
  created_at   timestamp with time zone default now()
);

-- ============================================================
-- TABLE: chunks
-- Stores text chunks + their vector embeddings
-- embedding dimension:
--   768  if using Gemini text-embedding-004
--   384  if using local sentence-transformers (all-MiniLM-L6-v2)
-- Change the number below to match your embedding model!
-- ============================================================
create table if not exists chunks (
  id           uuid primary key default gen_random_uuid(),
  document_id  uuid references documents(id) on delete cascade,
  content      text not null,
  source       text not null,
  page_number  integer,
  chunk_index  integer,
  embedding    vector(384),   -- Change to 768 if using Gemini embeddings
  created_at   timestamp with time zone default now()
);

-- Index for fast similarity search (uses HNSW algorithm)
create index if not exists chunks_embedding_idx
  on chunks using hnsw (embedding vector_cosine_ops);

-- ============================================================
-- TABLE: messages
-- Stores all chat history per session
-- ============================================================
create table if not exists messages (
  id          uuid primary key default gen_random_uuid(),
  session_id  text not null,
  role        text not null check (role in ('user', 'assistant')),
  content     text not null,
  sources     jsonb default '[]',
  created_at  timestamp with time zone default now()
);

-- Index for fast session lookups
create index if not exists messages_session_idx on messages(session_id);

-- ============================================================
-- FUNCTION: match_chunks
-- Called by the Python retriever to do similarity search
-- Returns top-k chunks ordered by cosine similarity
-- ============================================================
create or replace function match_chunks (
  query_embedding vector(384),   -- Change to 768 if using Gemini embeddings
  match_count     int default 5,
  match_threshold float default 0.3
)
returns table (
  id          uuid,
  content     text,
  source      text,
  page_number integer,
  chunk_index integer,
  similarity  float
)
language sql stable
as $$
  select
    chunks.id,
    chunks.content,
    chunks.source,
    chunks.page_number,
    chunks.chunk_index,
    1 - (chunks.embedding <=> query_embedding) as similarity
  from chunks
  where 1 - (chunks.embedding <=> query_embedding) > match_threshold
  order by chunks.embedding <=> query_embedding
  limit match_count;
$$;

-- ============================================================
-- Row Level Security (optional but good practice)
-- Allows public read for this demo. In production, add auth.
-- ============================================================
alter table documents enable row level security;
alter table chunks    enable row level security;
alter table messages  enable row level security;

create policy "Allow all for service role" on documents for all using (true);
create policy "Allow all for service role" on chunks    for all using (true);
create policy "Allow all for service role" on messages  for all using (true);

-- ============================================================
-- Done! Your database is ready.
-- ============================================================
select 'Schema created successfully! pgvector is ready.' as status;
