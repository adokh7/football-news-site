#!/usr/bin/env python3
"""
update_nav_v2.py — Adds Ligue 1 and Serie A to the primary nav and fixes footer links
across all HTML files in the workspace.
"""
import os, re

DIR = '/Users/adnan/Desktop/flash'

INACTIVE = 'class="text-sm text-slate-400 hover:text-amber-400 transition-colors font-medium"'
ACTIVE   = 'class="text-sm text-amber-400 font-semibold border-b border-amber-400 pb-0.5"'

L1_INACTIVE  = f'<a href="ligue-1.html" {INACTIVE}>Ligue 1</a>'
SA_INACTIVE  = f'<a href="serie-a.html" {INACTIVE}>Serie A</a>'

# --- footer fixes ---
FOOTER_L1_OLD = f'<a href="#" class="text-xs text-slate-500 hover:text-amber-400 transition-colors">Ligue 1</a>'
FOOTER_L1_NEW = f'<a href="ligue-1.html" class="text-xs text-slate-500 hover:text-amber-400 transition-colors">Ligue 1</a>'
FOOTER_SA_OLD = f'<a href="#" class="text-xs text-slate-500 hover:text-amber-400 transition-colors">Serie A</a>'
FOOTER_SA_NEW = f'<a href="serie-a.html" class="text-xs text-slate-500 hover:text-amber-400 transition-colors">Serie A</a>'

updated = []
skipped = []

for fname in sorted(os.listdir(DIR)):
    if not fname.endswith('.html'):
        continue
    path = os.path.join(DIR, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # ── NAV ─────────────────────────────────────────────────────
    has_ligue1_nav = 'href="ligue-1.html"' in content and '>Ligue 1<' in content
    has_seriea_nav = 'href="serie-a.html"' in content and '>Serie A<' in content

    if not has_seriea_nav:
        if has_ligue1_nav:
            # Just add Serie A after Ligue 1 (handles both active and inactive Ligue 1)
            content = re.sub(
                r'(<a href="ligue-1\.html"[^>]*>Ligue 1</a>)',
                r'\1\n        ' + SA_INACTIVE,
                content, count=1
            )
        else:
            # Add both Ligue 1 + Serie A after Bundesliga link
            content = re.sub(
                r'(<a href="bundesliga\.html"[^>]*>Bundesliga</a>)',
                r'\1\n        ' + L1_INACTIVE + '\n        ' + SA_INACTIVE,
                content, count=1
            )

    # ── FOOTER ──────────────────────────────────────────────────
    content = content.replace(FOOTER_L1_OLD, FOOTER_L1_NEW)
    content = content.replace(FOOTER_SA_OLD, FOOTER_SA_NEW)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        updated.append(fname)
    else:
        skipped.append(fname)

print(f"\n✅ Updated ({len(updated)} files):")
for f in updated: print(f"   {f}")
print(f"\n⏭  Skipped / already up-to-date ({len(skipped)} files):")
for f in skipped: print(f"   {f}")
