# Govolsgo — Prioritized Action Plan

## 🔴 Critical — this week (blocks/duplicates indexing)

1. **Fix non-www → www redirect in production.**
   `https://govolsgo.com/` currently returns 200, not 301. Verify in Vercel → Project → Settings → Domains that **both** `govolsgo.com` and `www.govolsgo.com` are attached to the SAME project that serves your `vercel.json`. If the apex is on a different project, move it or set the redirect there. Verify:
   ```bash
   curl -sILo /dev/null -w '%{http_code} -> %{redirect_url}\n' https://govolsgo.com/premier-league
   ```
   Expect `301 -> https://www.govolsgo.com/premier-league`.

2. **Add `robots.txt`** at repo root:
   ```
   User-agent: *
   Allow: /
   Sitemap: https://www.govolsgo.com/sitemap.xml
   ```

## 🟠 High — within 1 week

3. **Normalize URLs to extensionless.** Update the 3 `.html` canonicals (`france-morocco-live`, `infantino-balogun-scandal`, `usa-belgium-recap`), the 67 internal `.html` hrefs, and the **news sitemap** `<loc>` entries to clean paths. Keep it consistent with the main sitemap and `cleanUrls:true`.

4. **Add NewsArticle schema to all ~24 article pages** missing it (`headline`, `datePublished`, `dateModified`, `author`, `publisher`, `image`).

5. **Add `og:image` to homepage + 17 pages** currently missing it.

6. **Consolidate duplicate pairs** (301 weaker → stronger):
   - argentina-cape-verde ↔ cape-verde-argentina-upset
   - ronaldo-world-cup-ends ↔ ronaldo-world-cup-passenger

## 🟡 Medium — within 1 month

7. **noindex or delete scaffold pages:** `category-template.html`, `article.html`.
8. **Shorten 3 over-length titles** (<60 chars): france-morocco-live, cape-verde-argentina-upset, argentina-cape-verde.
9. **Compress oversized heroes** (usa-belgium-recap 684 KB, arteta-tactics 611 KB → <150 KB); add `fetchpriority="high"` + `width`/`height` to LCP images.
10. **Add security headers** via `vercel.json` `headers`: `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`.

## 🟢 Low — backlog

11. Add `twitter:card` to 5 legal pages (about, contact, cookies, privacy, terms).
12. Decide on multilingual (EN + AR) rollout → add hreflang when live.
