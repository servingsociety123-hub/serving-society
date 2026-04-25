-- ============================================================
-- SERVING SOCIETY — Supabase Database Setup
-- Run this entire file in your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/_/sql/new
-- ============================================================

-- ── 1. CONTACTS table ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.contacts (
  id          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  name        TEXT        NOT NULL,
  email       TEXT        NOT NULL,
  phone       TEXT,
  service     TEXT,
  message     TEXT
);

-- ── 2. APPOINTMENTS table ──────────────────────────────────
CREATE TABLE IF NOT EXISTS public.appointments (
  id              UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  first_name      TEXT        NOT NULL,
  last_name       TEXT        NOT NULL,
  email           TEXT        NOT NULL,
  phone           TEXT,
  contact_method  TEXT,
  services        TEXT,
  preferred_date  DATE,
  preferred_time  TIME,
  notes           TEXT
);

-- ── 3. Enable Row Level Security ───────────────────────────
ALTER TABLE public.contacts     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;

-- ── 4. RLS Policies: contacts ──────────────────────────────

-- Anyone (public) can insert a contact form submission
CREATE POLICY "Allow public insert on contacts"
  ON public.contacts
  FOR INSERT
  TO anon
  WITH CHECK (true);

-- Only authenticated users (admin) can read contacts
CREATE POLICY "Allow authenticated read on contacts"
  ON public.contacts
  FOR SELECT
  TO authenticated
  USING (true);

-- Only authenticated users can delete contacts
CREATE POLICY "Allow authenticated delete on contacts"
  ON public.contacts
  FOR DELETE
  TO authenticated
  USING (true);

-- ── 5. RLS Policies: appointments ─────────────────────────

-- Anyone (public) can insert an appointment request
CREATE POLICY "Allow public insert on appointments"
  ON public.appointments
  FOR INSERT
  TO anon
  WITH CHECK (true);

-- Only authenticated users (admin) can read appointments
CREATE POLICY "Allow authenticated read on appointments"
  ON public.appointments
  FOR SELECT
  TO authenticated
  USING (true);

-- Only authenticated users can delete appointments
CREATE POLICY "Allow authenticated delete on appointments"
  ON public.appointments
  FOR DELETE
  TO authenticated
  USING (true);

-- ── 6. Indexes for faster admin queries ────────────────────
CREATE INDEX IF NOT EXISTS contacts_created_at_idx     ON public.contacts     (created_at DESC);
CREATE INDEX IF NOT EXISTS appointments_created_at_idx ON public.appointments (created_at DESC);
CREATE INDEX IF NOT EXISTS contacts_email_idx          ON public.contacts     (email);
CREATE INDEX IF NOT EXISTS appointments_email_idx      ON public.appointments (email);

-- ── 7. Verify setup ────────────────────────────────────────
-- Run this to confirm tables exist:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
