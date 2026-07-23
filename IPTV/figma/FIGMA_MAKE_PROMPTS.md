# Figma Make Prompts — IPTV Premium Sverige
5 برومبتات جاهزة للصق (بالإنجليزية — Figma Make يفهمها أفضل). كل واحد مكتفٍ ذاتياً: يحمل البراند كاملاً لأن Make لا يذكر السياق بين الجلسات.

**Shared brand block** (مضمّن داخل كل برومبت):
> Dark luxury brand: background #0B0B0F, elevated surfaces #141419 / cards #1E1E24, champagne-gold accent #F2B233 (CTAs & prices ONLY, never large fills), electric-blue #5985FF for links/focus, live-red #FF2D55. Fonts: Clash Display (headings, semibold, tight tracking) + Inter (body). Radius 10–24px, 8px spacing grid, subtle gold glow on primary buttons. Mood: bold, premium, cinematic — like Apple TV meets a sports bar. All UI copy in Swedish.

---

## Prompt 1 — Homepage (Landing)

```
Build a high-converting dark landing page for a premium Swedish IPTV subscription service. The goal: visitors immediately trust the service and click "Starta gratis provperiod".

BRAND: Dark luxury. Background #0B0B0F, cards #1E1E24, champagne-gold accent #F2B233 used ONLY for primary CTAs, prices and badges. Electric-blue #5985FF for links and focus rings. Headings in Clash Display (semibold, tight letter-spacing), body in Inter. 8px spacing grid, border radius 10–24px, primary buttons get a soft gold glow (0 0 24px rgba(242,178,51,.35)). Mood: bold, cinematic, premium — Apple TV meets live sports. All text in Swedish.

SECTIONS (top to bottom):
1. Announcement bar: "🔥 Sommarkampanj: 45 % rabatt på årsabonnemang — begränsad tid"
2. Header (72px): logo left, nav "Paket & priser · Kanaler · Guider · Support", gold button "Prova gratis". Transparent over hero, becomes blurred dark (rgba(11,11,15,.85) + backdrop blur) after scrolling 24px.
3. Hero: H1 "Säg upp kabeln. Behåll allt." (72px desktop / 44px mobile), subline "Över 20 000 kanaler och 50 000 filmer i äkta 4K — utan bindningstid, utan lagg, utan krångel.", gold primary CTA "Starta gratis provperiod →" + ghost secondary "Se paket & priser", micro-trust line under CTAs: "Igång på 2 minuter · Inget kort krävs · 99,9 % drifttid". Background: dark gradient with a blurred collage of movie posters fading into black at the bottom.
4. Stats strip: 4 numbers with count-up animation on scroll into view — "12 000+ aktiva kunder", "99,9 % drifttid", "20 000+ kanaler", "< 15 min svarstid".
5. Features: section title "Därför byter tusentals svenskar varje månad", 3 cards ("Stabilitet du kan lita på", "Allt innehåll. Ett abonnemang.", "Fungerar på alla dina skärmar") — each card lifts 4px with stronger shadow on hover.
6. VOD carousel: horizontally scrollable row of 2:3 movie poster cards with gold "4K" badges; posters scale to 1.05 inside clipped corners on hover with a dark gradient overlay revealing the title.
7. Pricing teaser: 3 plan cards, middle one highlighted with gold 1.5px border + "Populärast" badge and slightly scaled up (1.03).
8. Testimonials: 3 review cards with 5 gold stars, Swedish names and devices (Johan L., Göteborg — Samsung Smart TV etc.).
9. FAQ accordion: 8 questions, chevron rotates 180° and panel expands smoothly (240ms ease).
10. Final CTA section: H2 "Redo att se skillnaden själv?" + gold button "Ja, ge mig min gratis provperiod →".
11. Footer: 3 link columns (Tjänsten / Hjälp / Företaget), trust row "🔒 Säker betalning · 🇸🇪 Svensk support dygnet runt · ⚡ 99,9 % drifttid", copyright.

INTERACTIONS: buttons lift 1px + glow on hover; sections fade-and-rise 16px once on scroll into view (stagger 60ms); reduced-motion friendly. 
RESPONSIVE: mobile-first 390px (full-width CTAs, carousel becomes swipeable, nav collapses to hamburger drawer), tablet 768px (2-column features), desktop 1280px max-width container with 12-column grid.
```

---

## Prompt 2 — Pricing page with live calculator

```
Build a dark premium pricing page for a Swedish IPTV service where users configure duration + device count and see the price update instantly, then proceed to checkout.

BRAND: [نفس بلوك البراند أعلاه — الصق الفقرة المشتركة]

SECTIONS:
1. Compact header (same as site: dark, logo, nav, gold CTA).
2. Hero: H1 "Ett pris. Allt du vill se." + subline "Välj din period och börja titta inom minuter — full återbetalning inom 7 dagar om du ångrar dig."
3. INTERACTIVE PRICING CALCULATOR (the centerpiece):
   - Segmented toggle: "1 mån · 3 mån · 6 mån · 12 mån" with a sliding gold knob (240ms ease) and a "Spara 45 %" badge that animates in on the 12-month option.
   - Device stepper: "Antal enheter" with − / + buttons, range 1–5.
   - Large price display in Clash Display with tabular numbers: e.g. "249 kr/mån", strikethrough compare-at price above it, total below in muted gray ("Totalt 2 988 kr faktureras årligen"). Price animates with a quick count-up when settings change.
   - Gold CTA "Välj detta paket →".
4. Three plan cards below (Bas / Premium / Familj): middle card gold-bordered with "Populärast" badge, scaled 1.03, hover lifts all cards 4px. Each lists: "Allt innehåll ingår · Upp till 4K · X samtidiga enheter · Support dygnet runt · Aktiveras direkt".
5. Feature comparison table: sticky header row on scroll, gold checkmarks vs gray dashes, the Premium column has a subtle gold gradient background.
6. Trust section: "💳 Kort, Swish eller krypto · 🔒 Krypterad betalning · ↩ 7 dagars öppet köp" + one testimonial: "Vi sparar över 5 000 kr om året. Enda ångern är att vi inte bytte tidigare." — Familjen Eriksson, Uppsala ★★★★★
7. Payment-focused FAQ accordion (8 items: betalsätt, automatisk förnyelse, familjerabatt, återbetalning...).
8. Footer (standard 3-column dark footer with trust row).

INTERACTIONS: toggle knob slides; price counts up/down on change; disabled device options show tooltip "Uppgradera för fler enheter"; comparison table rows highlight on hover.
RESPONSIVE: mobile 390px — calculator stacks vertically and stays above the fold, plan cards become a swipeable horizontal snap carousel, table scrolls horizontally with frozen first column; desktop 1280px — calculator and 3 cards side by side.
```

---

## Prompt 3 — Free Trial flow (multi-step form + success)

```
Build a dark, focused conversion page for a free 24-hour IPTV trial in Sweden, with a 3-step form and a success state that shows generated login credentials. Zero distractions — this page exists only to capture trials.

BRAND: [بلوك البراند المشترك]

LAYOUT: split screen on desktop — left 55% = the form card, right 45% = value proposition panel. Mobile: value prop collapses to a compact strip above the form.

SECTIONS:
1. Minimal header: logo + one link "Har du redan ett konto? Logga in".
2. Left — MULTI-STEP FORM in an elevated card (#1E1E24, radius 24px):
   - Step indicator: 3 dots with connecting line, active dot gold, completed dots show checkmarks.
   - Step 1 "Dina uppgifter": inputs "Ditt namn", "E-postadress" (48px height, #141419 bg, blue focus ring), button "Fortsätt →".
   - Step 2 "Din enhet": a grid of 6 selectable device tiles with icons (Smart TV, Android TV, Apple TV, Mobil, Dator, MAG-box) — selected tile gets gold border + subtle glow.
   - Step 3 "Bekräfta din e-post": 6 individual OTP boxes (48×56px, monospace, auto-advance look), "Skicka igen" link with a 60s countdown, error state = red borders + small shake.
   - Submit: "Aktivera min provperiod" (gold, full width). Loading state: spinner replaces label, button width stays fixed.
   - Under form (small gray text): "Dina uppgifter skickas inom 2 minuter. Ingen spam — vi lovar."
3. Right panel: H1 "Se allt. Betala ingenting. Idag.", subline "24 timmar full tillgång till hela utbudet i 4K — inget kort, ingen bindning, inga ursäkter.", 3 numbered steps ("1. Fyll i formuläret / 2. Få dina uppgifter direkt / 3. Börja titta"), stat "9 av 10 som testar stannar kvar", one testimonial from Micke R., Västerås.
4. SUCCESS STATE (design as a separate screen): confetti-subtle header "Klart! Dina uppgifter är på väg 🎉", a CREDENTIALS CARD with gold border containing monospace rows (M3U URL, Användarnamn, Lösenord) each with a copy icon button that flips to a green check + toast "Kopierat!", then a big gold button "Så installerar du på [Samsung Smart TV] →" (device from step 2), and a countdown chip "Din provperiod: 23:59:12 kvar".
5. Slim footer: trust row only.

INTERACTIONS: steps slide horizontally (240ms); invalid fields show inline red text under the field; OTP boxes fill with a subtle pop; copy buttons animate to checkmark for 1.5s.
RESPONSIVE: mobile 390px single column (form first), desktop 1280px split screen. Form card max-width 480px.
```

---

## Prompt 4 — Tutorials hub + device guide

```
Build two connected dark pages for a Swedish IPTV service: (A) a tutorials hub where users pick their device, and (B) a step-by-step installation guide template. Goal: a user goes from "how do I install this?" to watching in 5 minutes.

BRAND: [بلوك البراند المشترك]

PAGE A — HUB (/guider):
1. Standard dark header.
2. Hero: H1 "Igång på fem minuter. Garanterat." + subline "Välj din enhet och följ vår steg-för-steg-guide med bilder — skriven för människor, inte tekniker."
3. Device grid: 6 large tiles (Samsung/LG Smart TV, Android TV & Fire Stick, Apple TV & iOS, Android-mobil, Windows & Mac, MAG & Enigma) — each tile: device icon, name, "5 min" duration chip, and an estimated difficulty dot. Hover: tile lifts 4px, icon shifts from 40% grayscale to full color, gold arrow appears.
4. Three reassurance cards: "Guider för varje enhet", "Kopiera och klistra in", "Fastnat? Vi tar över." with body copy.
5. Social proof strip: quote "Lättare än att installera Netflix" + "Genomsnittlig installationstid: 4 minuter och 30 sekunder."
6. Footer.

PAGE B — GUIDE TEMPLATE (/guider/samsung-smart-tv):
1. Breadcrumb "Guider / Samsung Smart TV" + horizontal device tabs to switch guides (active tab has sliding gold underline).
2. Progress overview: "6 steg · cirka 5 minuter".
3. STEP GUIDE: vertical timeline — each step has a gold circled number (32px) connected by a vertical line, a title, short instruction text, and a screenshot placeholder (16:9, radius 16px). Steps with credentials show a monospace code block with a copy button. Completed steps show green checkmarks (interactive: clicking a step number marks it done).
4. Video section: a video thumbnail with a large gold play button (facade — does not autoload).
5. App download row: 2 store badge buttons + QR code card "Skanna med mobilen".
6. Troubleshooting callout (amber/warning style): "Bilden fryser? 90 % löses på två minuter →" linking to FAQ.
7. Bottom CTA card: "Ma zolde du fast? Vi tar över." → dark card with gold button "Skapa supportärende" + note "Svar inom 15 minuter, dygnet runt."
8. Footer.

INTERACTIONS: tabs slide; steps check off on click with a small spring animation; copy buttons flip to checkmarks; sticky mini table-of-contents on desktop right side highlighting the current step while scrolling.
RESPONSIVE: mobile 390px — device grid 2 columns, timeline full width, TOC hidden; tablet 768px — grid 3 columns; desktop 1280px — guide content 720px column + sticky TOC rail.
```

---

## Prompt 5 — User dashboard (Mitt konto)

```
Build a dark premium account dashboard for a Swedish IPTV subscriber to manage their subscription, devices, credentials and support tickets. Goal: renewal in one click and zero confusion.

BRAND: [بلوك البراند المشترك]

LAYOUT: left sidebar navigation (icons + labels: Översikt, Mitt abonnemang, Enheter, Guider, Mina ärenden, Logga ut) — collapses to bottom tab bar on mobile. Main area on #0B0B0F with widget cards on #1E1E24.

WIDGETS (Översikt screen):
1. SUBSCRIPTION CARD (hero widget, spans 2 columns): plan name "Premium — 12 månader", status badge "Aktiv" (green dot), a circular progress ring showing time remaining with "23 dagar kvar" in Clash Display, renewal date, and a gold button "Förnya nu — behåll ditt pris". Design 3 states as variants: Active (green), Expiring soon (amber banner "Ditt abonnemang går ut om 5 dagar" + pulsing gold CTA), Expired (grayed content + prominent gold reactivation CTA).
2. CREDENTIALS CARD: gold-bordered, monospace rows for M3U URL / Användarnamn / Lösenord (password masked with an eye toggle), copy icon per row flipping to green check, small ghost button "Generera nytt lösenord" that opens a confirm modal warning "Alla dina enheter behöver logga in på nytt".
3. DEVICE MANAGER: list of connected devices (icon, name "Vardagsrums-TV", type, last active "för 2 tim sedan"), inline rename on click, red trash icon with confirm modal, "+ Lägg till enhet" button; when at plan limit show an upsell row "Behöver du fler enheter? Uppgradera till Familj →". Empty state: "Lägg till din första enhet" with a friendly illustration.
4. USAGE VIZ: bar chart "Tittartid per dag" (7 bars, gold gradient fill, tooltip on hover) + a small donut "Mest sedda kategorier" (Sport 45%, Film 30%, Serier 25%) with a legend. Empty state text: "Din statistik dyker upp efter första veckan 📊".
5. APP DOWNLOADS: compact row of 4 app cards with platform icons and "Ladda ner" ghost buttons — the user's registered device type is listed first with a "Din enhet" chip.
6. TICKETS WIDGET: last 3 support tickets (id, subject, status badge OPEN/RESOLVED, relative time), unread reply indicator (blue dot), link "Visa alla ärenden →" and gold button "Nytt ärende". Empty state: "Inga ärenden ännu — och det är goda nyheter."

INTERACTIONS: widgets fade in with 60ms stagger on load; every card has skeleton loading variants (design them!); hover on list rows = #2A2A32 background; all destructive actions use confirm modals; toasts bottom-right ("Kopierat!", "Enhet borttagen").
RESPONSIVE: mobile 390px — single column, sidebar becomes bottom tab bar, subscription card first; tablet 768px — 2-column widget grid; desktop 1280px — sidebar 240px + 2-column main grid, subscription card spans full width.
```

---

## نصائح تشغيل في Figma Make
1. **برومبت واحد لكل جلسة** — لا تطلب الصفحات الخمس دفعة واحدة.
2. الصق **بلوك البراند كاملاً** مكان `[بلوك البراند المشترك]` في البرومبتات 2–5 قبل اللصق.
3. بعد أول نتيجة، حسّن بطلبات قصيرة: "make the gold glow subtler"، "increase hero size on mobile" — لا تعيد البرومبت كاملاً.
4. اطلب الحالات كـ variants صراحةً إن أغفلها ("show the expired state of the subscription card").
5. صدّر الـ tokens من [tokens.json](../design-system/tokens.json) إلى Figma Variables بعد التوليد لتوحيد الألوان.
```
