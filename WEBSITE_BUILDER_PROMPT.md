# One-Prompt Website Builder

Copy everything below the line into Claude (or any capable AI coding agent), fill in the **YOUR DETAILS** section, and it will build a complete multi-page business website with Supabase-backed forms — the same architecture as the Serving Society site.

---

# PROMPT — BUILD MY BUSINESS WEBSITE

Build a complete, production-ready static business website using **plain HTML, CSS, and vanilla JavaScript** (no frameworks, no build step) with a **Supabase** backend for form submissions. Follow every requirement below exactly.

## YOUR DETAILS (fill this in)

```
Business name:        [e.g. Serving Society]
Industry/type:        [e.g. NDIS disability support provider]
Tagline:              [one sentence describing the business]
Locations served:     [e.g. Geelong and Melbourne]
Services (list 5-12): [one per line — each becomes its own page]
  - Service 1
  - Service 2
  - ...
Phone:                [e.g. +61 400 000 000]
Email:                [e.g. info@business.com.au]
ABN / reg number:     [if applicable]
Brand colours:        [primary, accent — e.g. deep purple #6B2D7B, lime #C5D34B]
Tone:                 [e.g. warm, professional, compassionate]
Logo file:            [path or "generate a placeholder"]
Domain (if known):    [e.g. business.com.au — used in sitemap]
Supabase URL:         [https://xxxx.supabase.co — or "I'll add later"]
Supabase anon key:    [eyJ... — or "I'll add later"]
Extra notes:          [anything specific — testimonials, certifications, acknowledgements, etc.]
```

## SITE STRUCTURE (build all of these)

```
/
├── index.html                  Home: hero, services grid, about teaser,
│                               testimonials carousel, stats counters,
│                               contact form section, footer
├── about.html                  About: story, mission, values
├── appointment.html            Appointment booking form
├── services/
│   └── <one-page-per-service>.html   (kebab-case filenames)
├── admin.html                  Admin dashboard: view contact + appointment
│                               submissions from Supabase (with archive toggle)
├── login.html                  Simple Supabase-auth gate for admin.html
├── style.css                   ONE shared stylesheet, CSS variables for colours
├── script.js                   ONE shared script (see JS requirements)
├── supabase-config.js          Just sets window.SUPABASE_URL / SUPABASE_ANON_KEY
├── supabase-setup.sql          Full DB schema to paste into Supabase SQL editor
├── sitemap.xml                 All pages, for Google Search Console
└── .github/workflows/keep_alive.yml   Supabase keep-alive cron (see below)
```

## DESIGN REQUIREMENTS

- Modern, polished, professional. Google Fonts (one display font + one body font).
- Sticky navbar that gains a shadow on scroll; mobile hamburger menu; services dropdown.
- Hero section with gradient/brand-colour background, badge pill, big headline with accent-underlined keywords, two CTA buttons, "scroll to explore" indicator, subtle animated particle canvas.
- Scroll-reveal animations via IntersectionObserver (staggered for siblings).
- Animated number counters for stats.
- Auto-rotating testimonial carousel with dots.
- Each service page: hero image, description, benefits list, CTA to appointment page.
- Footer on every page: logo, blurb, services links, quick links, contact info, copyright + ABN.
- Fully responsive (mobile-first breakpoints).
- Accessible: semantic HTML, labels on all inputs, alt text, aria attributes on toggles.

## FORMS + SUPABASE (critical requirements)

1. **Contact form** (on index.html) → inserts into `contacts` table: name, phone, email, service, message.
2. **Appointment form** (appointment.html) → inserts into `appointments` table: first_name, last_name, email, phone, contact_method, services (checkbox list of all services, joined as text), preferred_date, preferred_time, notes.
3. Load Supabase via CDN: `<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2" defer></script>` after `supabase-config.js`.
4. Initialize the client inside `window.addEventListener('load', ...)` and store as `window._supabase`.
5. Forms must use JS submit handlers with `e.preventDefault()`, inline validation (highlight empty required fields), a disabled "Sending…" button state, an inline success message (no alert for success), and inline error feedback on failure.
6. `supabase-setup.sql` must create both tables with UUID primary keys, `created_at TIMESTAMPTZ DEFAULT NOW()`, an `archived BOOLEAN DEFAULT FALSE` column, enable RLS with policies: anonymous INSERT allowed, SELECT/UPDATE only for authenticated users.

## ⚠️ KNOWN PITFALLS — AVOID THESE BUGS

These bugs occurred in the original build. Do not repeat them:

1. **Guard every page-specific DOM element in the shared script.js.** Every block that touches an element (particle canvas container, navbar, carousel, forms, etc.) MUST null-check first (`if (!el) return;`). An unguarded `appendChild` on a missing element crashes the whole script and silently kills form handlers further down the file — the form then does a default GET submit and data is lost.
2. **Use distinct input IDs across pages** (e.g. `apptEmail` not `email` on the appointment page) since style/script are shared.
3. **Keep-alive workflow must ping a real table** (`/rest/v1/contacts?select=id&limit=1`), NOT the bare `/rest/v1/` root — the root returns 401 even with a valid anon key.
4. Add `novalidate` to forms (JS handles validation) but keep `required` attributes for the JS to find.

## KEEP-ALIVE CRON (prevents free-tier pausing)

Create `.github/workflows/keep_alive.yml`:

```yaml
name: Keep Supabase Active
on:
  schedule:
    - cron: '0 0 */3 * *'
  workflow_dispatch:
jobs:
  ping_supabase:
    runs-on: ubuntu-latest
    steps:
      - name: Send API Request
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        run: |
          curl -sf -o /dev/null -w "HTTP %{http_code}\n" \
            "$SUPABASE_URL/rest/v1/contacts?select=id&limit=1" \
            -H "apikey: $SUPABASE_ANON_KEY" \
            -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

Remind me at the end to: add `SUPABASE_URL` and `SUPABASE_ANON_KEY` as GitHub repository secrets (`gh secret set ...`), run `supabase-setup.sql` in the Supabase SQL editor, and trigger the workflow once manually to test.

## SEO

- Unique `<title>` and meta description per page.
- Open Graph tags on every page.
- `sitemap.xml` listing all pages with the domain above.
- Descriptive alt text on all images.

## VERIFICATION (do this before finishing)

1. Serve the site locally and load every page — zero console errors on EVERY page (this catches the unguarded-DOM crash).
2. Fill and submit BOTH forms in the browser and confirm rows actually appear in Supabase (query the REST API to verify) — do not just confirm the success message shows.
3. Confirm mobile layout at 380px width.
4. List anything that still needs manual setup (secrets, SQL, DNS) as a final checklist.

# END OF PROMPT
