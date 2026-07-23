# Govolsgo — Full SEO Audit

**Site:** https://www.govolsgo.com
**Type:** Football news publisher (breaking news, live scores, transfers, tactical analysis)
**Audit date:** 2026-07-23
**Pages analyzed:** 45 HTML pages (local source) + live production checks
**Overall SEO Health Score: 68 / 100** — solid on-page foundation undermined by two indexing-level defects.

---

## Executive Summary

Govolsgo has an unusually strong **on-page** foundation for a site this size: every page has exactly one H1, title/description lengths are almost all within best-practice ranges, every `<img>` has alt text, and category/table pages carry structured data. The score is dragged down by two **critical, site-wide** problems that affect crawling and indexing, plus schema gaps on article pages.

### Top 5 Critical / High issues
1. **`robots.txt` returns 404** — no robots file exists. Crawlers get an error where they expect crawl directives and a sitemap pointer. *(Critical)*
2. **Non-www does NOT redirect** — `https://govolsgo.com/` returns **HTTP 200** instead of 301 to www. The `vercel.json` redirect is not firing in production, so the whole site is duplicated across two hostnames. *(Critical)*
3. **Mixed `.html` vs clean URLs** — `cleanUrls` is on, yet 67 internal links, 3 page canonicals, and the entire news sitemap use `.html`. Both versions return 200 → duplicate URLs and split signals. *(High)*
4. **~24 article pages have no Article/NewsArticle schema** — only 6 NewsArticle blocks exist site-wide. Kills rich-result and AI-citation eligibility for news content. *(High)*
5. **Homepage and 17 other pages missing `og:image`** — poor social/AI link previews, lower CTR when shared. *(High)*

### Top 5 Quick Wins
- Add a `robots.txt` with a `Sitemap:` line (5 min).
- Fix the non-www→www redirect at the correct Vercel project/domain (see Technical).
- Normalize the 3 `.html` canonicals + news sitemap to clean URLs.
- Add `og:image` to the homepage.
- Compress the 2 oversized hero images (684 KB + 611 KB).

---

## 1. Technical SEO — 55/100

| Check | Status |
|---|---|
| robots.txt | ❌ **404 / missing** |
| HTTP→HTTPS | ✅ Forced by Vercel (HSTS present, `max-age=63072000`) |
| non-www→www redirect | ❌ **Returns 200, no redirect** |
| sitemap index | ✅ `/sitemap.xml` → main + news |
| Canonicals | ⚠️ Present on all pages, but 3 use `.html` |
| URL consistency | ⚠️ `cleanUrls:true` but 67 internal `.html` links |
| Security headers | ⚠️ Only HSTS. Missing `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`/CSP frame-ancestors, `Permissions-Policy` |
| Viewport meta | ✅ Present on all pages |

**Critical — non-www duplicate.** `curl https://govolsgo.com/` and `http://govolsgo.com/premier-league` both return `200` with content, not a redirect. Your committed `vercel.json` has the correct rule, so the live domain `govolsgo.com` is almost certainly attached to a **different Vercel project** than the one you deployed (`flash`), or the apex domain isn't routed through this project at all. Until this is fixed, Google sees two full copies of the site.

**Critical — robots.txt.** Requesting `/robots.txt` returns Vercel's `NOT_FOUND` page. Crawlers tolerate a 404 (treat as "allow all"), but you lose the `Sitemap:` directive and explicit AI-crawler control.

## 2. Content Quality — 78/100

- **Depth:** Good. Article/template pages run 1,300–2,100 words.
- **Duplicate/cannibalization risk (High):** two topic pairs cover the same event with separate URLs:
  - `argentina-cape-verde.html` ↔ `cape-verde-argentina-upset.html`
  - `ronaldo-world-cup-ends.html` ↔ `ronaldo-world-cup-passenger.html`
  Consolidate each pair (301 the weaker into the stronger) or differentiate intent clearly.
- **Scaffold pages indexable (Medium):** `article.html` and `category-template.html` are self-canonicalizing template artifacts. Either `noindex` them or remove them — "category-template" in the index is a bad look and dilutes crawl budget.

## 3. On-Page SEO — 85/100 (strongest area)

- ✅ Exactly **one H1 per page** across all 45 pages.
- ✅ Meta descriptions **all within 135–155 chars**.
- ✅ Titles mostly < 60 chars.
- ⚠️ **3 titles will truncate in SERPs (>60):** `france-morocco-live` (71), `cape-verde-argentina-upset` (69), `argentina-cape-verde` (62).
- ⚠️ Internal links use `.html`; switch to clean paths to match canonicals.

## 4. Schema / Structured Data — 55/100

Present: Organization, NewsMediaOrganization, CollectionPage, BreadcrumbList, ListItem, ImageObject on home/category/table pages. **Only 6 `NewsArticle` blocks exist** — roughly two dozen article pages have **no** article-level schema. Add `NewsArticle` (or `Article`) with `headline`, `datePublished`, `dateModified`, `author`, `publisher`, and `image` to every story. This is the single highest-leverage schema fix for a news site (Top Stories + AI citations).

## 5. Performance (CWV) — ~65/100 (lab estimate; no field data)

Static HTML on Vercel CDN is inherently fast, but LCP is at risk from heavy hero images:

| Image | Size |
|---|---|
| usa-belgium-recap.webp | **684 KB** |
| arteta-tactics.webp | **611 KB** |
| zdndmbl.webp | 319 KB |
| Stu-Holden.webp | 235 KB |

Target < 150 KB for above-the-fold heroes; add explicit `width`/`height` (CLS) and `fetchpriority="high"` on the LCP image, `loading="lazy"` below the fold.

## 6. Images — 70/100

- ✅ **100% alt-text coverage** — excellent.
- ⚠️ Oversized files above; already WebP (good format choice).

## 7. AI Search Readiness (GEO) — 60/100

- Missing `og:image` on homepage + 17 pages weakens AI/social previews.
- Sparse article schema limits passage-level citability.
- No `robots.txt` means no explicit allow for GPTBot/PerplexityBot/etc. (default is open, but be intentional).
- `llms.txt` absent — optional and ignored by Google; skip unless you specifically want it.

---

## Score Breakdown

| Category | Weight | Score | Weighted |
|---|---|---|---|
| Technical SEO | 22% | 55 | 12.1 |
| Content Quality | 23% | 78 | 17.9 |
| On-Page SEO | 20% | 85 | 17.0 |
| Schema | 10% | 55 | 5.5 |
| Performance | 10% | 65 | 6.5 |
| AI Readiness | 10% | 60 | 6.0 |
| Images | 5% | 70 | 3.5 |
| **Total** | | | **≈ 68** |
