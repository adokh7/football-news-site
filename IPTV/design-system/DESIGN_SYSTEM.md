# IPTV Premium Sverige — Design System v1.0
**Theme:** Bold Luxury Dark · dark-first · السوق: السويد (نصوص الواجهة بالسويدية)
**الملفات:** [tokens.json](tokens.json) · [tokens.css](tokens.css)

---

## 1. لوحة الألوان

### الأساسي — Champagne Gold
الذهبي هو توقيع الفخامة. يُستخدم فقط للـ CTAs، الأسعار، وشارة "Populärast". لا يُستخدم كخلفية واسعة.
`gold-400 #F2B233` (accent) · hover `gold-300 #F6C75A` · pressed `gold-500 #E6A417`

### الثانوي — Electric Blue
للتقنية والتفاعل: روابط، focus ring، رسوم بيانية. `blue-400 #5985FF`

### المحايد — Obsidian scale
14 درجة من `#FFFFFF` إلى `#050507`. الخلفية الافتراضية `n-950 #0B0B0F` (ليست سوداء نقية — تحافظ على عمق الظلال).

### الدلالي
| | Base | Subtle bg | Text on dark |
|---|---|---|---|
| Success | `#22C55E` | `#0E2B1A` | `#4ADE80` |
| Warning | `#F59E0B` | `#2D2107` | `#FBBF24` |
| Error | `#EF4444` | `#2F1212` | `#F87171` |
| Info | `#3B82F6` | `#0F1D33` | `#60A5FA` |
| **Live** (بث مباشر) | `#FF2D55` | `#33101A` | `#FF5C7A` |

### الوضع الداكن = الافتراضي
الموقع dark-first (يعكس 4K/سينما). Light mode اختياري لصفحات الدعم فقط عبر `[data-theme="light"]`.

Surface hierarchy: `bg #0B0B0F` → `bg-elevated #141419` → `bg-card #1E1E24` → `bg-hover #2A2A32`. الفصل بين الطبقات بالإضاءة لا بالحدود.

---

## 2. سُلّم الخطوط (9 مستويات)

**Display:** Clash Display (جريء، هندسي) · **Body:** Inter · **Mono:** JetBrains Mono (بيانات M3U/Xtream)

| Level | Desktop | Mobile | Weight | LH | Tracking | الاستخدام |
|---|---|---|---|---|---|---|
| display-xl | 72 | 44 | 600 | 1.05 | −0.02em | Hero فقط |
| display | 56 | 36 | 600 | 1.08 | −0.02em | عناوين أقسام كبرى |
| h1 | 40 | 32 | 600 | 1.15 | −0.015em | عنوان الصفحة |
| h2 | 32 | 26 | 600 | 1.2 | −0.01em | أقسام |
| h3 | 24 | 20 | 600 | 1.3 | — | بطاقات/باقات |
| h4 | 20 | 18 | 500 | 1.4 | — | عناوين فرعية |
| body-lg | 18 | 18 | 400 | 1.6 | — | مقدمات |
| body | 16 | 16 | 400 | 1.6 | — | النص الأساسي |
| caption | 13 | 13 | 500 | 1.45 | +0.02em | شارات، تسميات (UPPERCASE مسموح) |

الأسعار: display بـ tabular-nums. لا نص أقل من 13px إطلاقاً.

---

## 3. نظام المسافات — شبكة 8px

Scale: `4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96, 128` (tokens `--sp-1..12`).
- Padding داخل المكوّنات: 8–24
- بين المكوّنات: 24–48
- بين الأقسام: 80 (mobile) / 128 (desktop)
- Container: max-width 1280px، gutter 16 (mobile) / 24 (tablet) / 32 (desktop)
- Grid: 4 أعمدة (mobile) / 8 (tablet) / 12 (desktop)، gap 16/24/32

---

## 4. مواصفات المكوّنات (30 مكوّناً)

الحالات القياسية لكل مكوّن تفاعلي: **default / hover / active / focus-visible / disabled / loading** — أذكر أدناه ما يخالف القياسي فقط.

### Actions
1. **Button/Primary** — grad-gold، نص `n-950` وزن 600، h:48 (lg)/40 (md)، radius `r-md`، px:24. Hover: glow-gold + translateY(-1px). Active: gold-500 بدون glow. Disabled: n-800 + n-500. Loading: spinner يستبدل النص مع ثبات العرض.
2. **Button/Secondary** — شفاف + border `border-strong`، نص أبيض. Hover: bg-hover + border ذهبي.
3. **Button/Ghost** — نص فقط، hover: bg-hover.
4. **Button/Destructive** — error base، hover أفتح 8%.
5. **IconButton** — 40×40، radius full، الحالات كـ Ghost. Tooltip إلزامي (aria-label).
6. **CopyButton** — mono text + أيقونة؛ عند النسخ: أيقونة ✓ خضراء 1.5s + toast "Kopierat!".

### Forms
7. **Input** — h:48، bg-elevated، border 1px، radius md. Focus: border blue-400 + ring. Error: border error + رسالة تحتها (لا placeholder-only). Filled/disabled/read-only.
8. **Select** — كـ Input + chevron يدور 180° عند الفتح. القائمة: bg-card، shadow-lg، خيار hover: bg-hover، selected: نقطة ذهبية.
9. **Textarea** — min-h:120، auto-grow حتى 320.
10. **Checkbox / Radio** — 20×20، checked: خلفية ذهبية + علامة داكنة. Indeterminate للـ checkbox.
11. **Toggle** — 44×24، on: مسار ذهبي. حركة spring.
12. **OTPInput** — 6 خانات 48×56 mono 24px، auto-advance، خطأ: هزة `translateX ±4px` + حدود حمراء.
13. **SearchInput** — أيقونة بحث يسار، زر مسح يظهر عند الكتابة، `⌘K` hint.

### Display
14. **PlanCard** — bg-card + grad-card، radius xl، p:32. Popular: border ذهبي 1.5px + شارة "Populärast" + scale(1.03) على desktop. Hover: ترتفع 4px + shadow-lg. حالات: default/popular/selected/current-plan.
15. **PosterCard** (VOD) — نسبة 2:3، radius lg، صورة lazy + blur-up. Hover: scale(1.05) داخل overflow-hidden + scrim + العنوان. شارة 4K ذهبية أعلى اليمين.
16. **ChannelLogoTile** — 96×64، bg-elevated، اللوقو grayscale 40% → ملوّن عند hover.
17. **Badge** — caption uppercase، radius full، px:12 h:24. Variants: gold/success/error/info/**live** (نقطة تنبض).
18. **StatCard** — رقم display + تسمية caption. عدّاد متحرك عند الدخول للـ viewport (مرة واحدة).
19. **TestimonialCard** — bg-card، اقتباس body-lg، نجوم ذهبية، اسم + جهاز المستخدم.
20. **CredentialsCard** — bg-elevated + border ذهبي، حقول mono + CopyButton لكل سطر، زر إخفاء/إظهار كلمة المرور.
21. **StepGuide item** — رقم دائري ذهبي 32px + خط رابط عمودي، صورة radius lg، حالة "تم" (✓).
22. **Table/Comparison** — sticky header عند التمرير، صف hover: bg-hover، ✓ ذهبية / — رمادية، العمود المميز بخلفية `grad-card`.
23. **Avatar** — 32/40/48، fallback حرفين على خلفية blue-700.

### Feedback
24. **Toast** — bg-card + border حسب النوع، أعلى الوسط (mobile) / أسفل اليمين (desktop)، auto-dismiss 5s + progress bar، دخول slide+fade بـ ease-spring. Variants: success/error/info. `role="status"`.
25. **Modal** — max-w:560، radius xl، overlay `rgba(5,5,7,.7)` + blur(8px)، دخول scale .96→1 fade بـ dur-base. Focus trap + إغلاق Esc/overlay. Sizes: sm/md/lg/fullscreen (mobile).
26. **Skeleton** — bg-hover + shimmer متدرج 1.6s. أشكال: نص/بوستر/بطاقة.
27. **EmptyState** — أيقونة 48 + عنوان h4 + وصف + CTA ثانوي.
28. **Alert/Banner** — subtle bg دلالي + border-inline-start 3px + أيقونة. Dismissible اختياري.

### Navigation
29. **Header** — h:72، شفاف فوق الـ hero → عند scroll>24px: `bg rgba(11,11,15,.85)` + blur(16px) + border سفلي، انتقال dur-base. حالات: transparent/solid/menu-open.
30. **Tabs** (devices/pricing) — مؤشر سفلي ذهبي ينزلق بـ ease-standard، keyboard arrows، `aria-selected`. Variant segmented (BillingToggle): خلفية bg-elevated + "knob" منزلق.

(+ MobileNav drawer، Accordion FAQ بـ chevron دوّار وفتح height بـ ease-standard، Breadcrumb — تتبع نفس القواعد.)

---

## 5. أنماط التخطيط — Breakpoints

| Token | العرض | الأعمدة | ملاحظات |
|---|---|---|---|
| base | <640 | 4 | mobile-first، CTAs بعرض كامل، carousels قابلة للسحب |
| sm | ≥640 | 4 | |
| md | ≥768 | 8 | PlanCards عمودان |
| lg | ≥1024 | 12 | التخطيط الكامل، sidebars |
| xl | ≥1280 | 12 | container يثبت على 1280 |
| 2xl | ≥1536 | 12 | مسافات أوسع فقط |
| **tv** | ≥1920 | 12 | خط +10%، focus states ضخمة (تصفح TV بالريموت)، أهداف تفاعل ≥64px |

قواعد: أهداف اللمس ≥44×44 دائماً · المحتوى النصي max-width 68ch · صور البوستر بأبعاد ثابتة (CLS).

---

## 6. إرشادات الأنيميشن

**الفلسفة:** فخامة = قلّة وحسم. حركة واحدة معبّرة أفضل من عشر مبهرجة.

- **Durations:** instant 100ms (hover) · fast 160ms (toggles) · base 240ms (modals, tabs) · slow 400ms (accordions) · cinematic 700ms (hero فقط).
- **Easings:** standard `cubic-bezier(.2,0,0,1)` للأغلب · spring `(.34,1.56,.64,1)` للتأكيدات الصغيرة فقط (toggle, toast) · enter/exit للظهور/الاختفاء.
- **قواعد صارمة:** حرّك `transform` و`opacity` فقط (لا width/height/top — باستثناء accordion بـ grid-template-rows) · لا أنيميشن أثناء scroll يعيق القراءة · scroll-reveal: fade+rise 16px، مرة واحدة، stagger 60ms بحد أقصى 5 عناصر · شارة LIVE: نبض opacity 2s لا نهائي (العنصر الوحيد المسموح له بالتكرار).
- **`prefers-reduced-motion`:** كل شيء يتوقف (مطبّق globally في tokens.css).

---

## 7. متطلبات WCAG AA

- **تباين:** نص عادي ≥4.5:1، كبير ≥3:1. متحقق منه: `n-50` على `n-950` = 17.8:1 ✓ · `n-300` على `n-950` = 9.2:1 ✓ · `n-950` على `gold-400` = 9.6:1 ✓ (لهذا نص الزر داكن لا أبيض) · `blue-400` على `n-950` = 6.1:1 ✓. **ممنوع:** نص ذهبي على bg-card للنصوص الصغيرة (gold-400/n-850 = 7.9:1 ✓ مقبول، لكن gold-600 على داكن ✗).
- **Focus:** `:focus-visible` ring أزرق 2px + offset 2px على كل عنصر تفاعلي — الأزرق مقصود ليتمايز عن الذهبي الزخرفي.
- **لوحة المفاتيح:** كل شيء قابل للوصول Tab/أسهم، focus trap في Modals، skip-link "Hoppa till innehåll".
- **لا لون وحده:** حالات الخطأ = لون + أيقونة + نص. شارة LIVE = نقطة + كلمة.
- **ARIA:** toasts `role="status"`، أخطاء الفورم `aria-describedby` + `aria-invalid`، accordion `aria-expanded`، الأسعار بنص حقيقي لا صور.
- **أهداف اللمس ≥44px** و**نص ≥13px** (مذكورة أعلاه كقواعد نظام).

---

## 8. وصف جاهز لـ Figma

**بنية الملف:**
```
📁 IPTV Premium — Design System
├── Page: 🎨 Foundations
│   ├── Color styles: brand/gold/50–900, brand/blue/…, neutral/…, semantic/…, dark/surface/…
│   ├── Text styles: display-xl … caption (desktop + mobile variants = 18 style)
│   ├── Effects: shadow/sm|md|lg, glow/gold, glow/live, blur/header
│   └── Layout grids: 4col-16gap (mobile), 8col-24 (tablet), 12col-32/1280 (desktop)
├── Page: 🧩 Components  (كل مكوّن = Component set بـ variants)
│   ├── Button: variant(primary|secondary|ghost|destructive) × size(md|lg) × state(default|hover|active|focus|disabled|loading)
│   ├── Input: state(default|focus|filled|error|disabled) × type(text|select|search|otp)
│   ├── PlanCard: variant(default|popular|selected) × billing(monthly|yearly)
│   ├── PosterCard: state(default|hover) × badge(none|4k|live)
│   ├── Badge, Toast, Modal, Tabs, Toggle, … (القائمة الكاملة أعلاه)
│   └── كل الـ variants مربوطة بـ Variables (انظر أدناه)
├── Page: 📐 Templates — Home / Pricing / Free-trial / Tutorial / Ticket (desktop + 390px mobile)
└── Page: 📱 TV — نسخة 1920 مع focus states للريموت
```
**Figma Variables:** استورد `tokens.json` عبر plugin "Tokens Studio" → collections: `color` (mode: dark/light)، `spacing`، `radius`. اربط كل fill/gap/radius بالـ variable لا بقيمة يدوية.
**Auto-layout إلزامي** لكل مكوّن، padding من سلّم الـ 8px فقط.
**التسمية:** `category/component/variant` (مثل `action/button/primary`).

---

## نصوص UI مرجعية (Svenska)
CTAs: **"Starta gratis provperiod"** · "Se alla paket" · "Kom igång på 2 minuter" · "Kopiera" / "Kopierat!" · "Populärast" · "Skapa supportärende" · Trust: "99,9 % drifttid · Svenska kanaler i 4K · Support dygnet runt".
