# IPTV Subscriptions Platform — Architecture Document
**Role:** Principal Architect · **Target launch:** MVP في 6–8 أسابيع
**الجمهور:** عشاق الرياضة، محبو الأفلام/المسلسلات، العائلات (جودة 4K، ترفيه منزلي)

---

## 1. Site Map (هيكلة الصفحات)

```
/                          الرئيسية (Hero + Sports/Movies/Family value props)
├── /pricing               الباقات والأسعار (ديناميكي من CMS/DB)
├── /free-trial            طلب تجربة مجانية (أوتوماتيكي)
│   └── /free-trial/success   تأكيد + بيانات التفعيل
├── /channels              دليل القنوات (فلترة: رياضة/أفلام/أطفال/دول)
├── /movies                مكتبة VOD (عرض تسويقي — أفلام/مسلسلات)
├── /tutorials             دليل التشغيل
│   ├── /tutorials/smart-tv        (Samsung/LG)
│   ├── /tutorials/android-tv      (+ Firestick)
│   ├── /tutorials/apple-tv-ios
│   ├── /tutorials/android-mobile
│   ├── /tutorials/windows-mac
│   └── /tutorials/mag-enigma
├── /support               مركز الدعم 24/7
│   ├── /support/new           فتح تذكرة
│   ├── /support/ticket/[id]   متابعة تذكرة + محادثة
│   └── /support/faq           أسئلة شائعة (Schema FAQ)
├── /checkout/[planId]     الدفع
│   └── /checkout/success
├── /account               لوحة المشترك
│   ├── /account/subscription   حالة الاشتراك + التجديد
│   ├── /account/devices        الأجهزة المفعّلة
│   └── /account/tickets        تذاكري
├── /blog                  محتوى SEO (أدلة، مقارنات، "أفضل IPTV 4K")
│   └── /blog/[slug]
├── /about  /contact  /refund-policy  /terms  /privacy
└── /login  /register  /forgot-password
```

---

## 2. User Flows (3 رحلات)

### Flow 1 — تجربة مجانية أوتوماتيكية (أهم قمع تحويل)
```
زائر من إعلان/بحث → Landing (/free-trial)
→ نموذج قصير: الاسم، البريد/واتساب، نوع الجهاز
→ التحقق (OTP بريد أو رابط واتساب) + rate-limit + fingerprint لمنع التكرار
→ API يولّد حساب trial تلقائياً من Panel (M3U / Xtream codes، مدة 24 ساعة)
→ صفحة النجاح: بيانات الاتصال + زر "شغّلها على جهازك" → tutorial مطابق لجهازه
→ بريد/واتساب أوتوماتيكي + تذكير قبل انتهاء التجربة بـ 4 ساعات مع عرض خصم
→ CTA للترقية → /pricing
```

### Flow 2 — شراء اشتراك
```
/pricing → مقارنة الباقات (شهري/6 أشهر/سنوي، عدد الأجهزة، 4K)
→ اختيار باقة → /checkout/[planId]
→ إنشاء حساب (أو تسجيل دخول) → دفع (Stripe / crypto / محلي)
→ Webhook يؤكد الدفع → تفعيل أوتوماتيكي من الـ Panel
→ /checkout/success: بيانات M3U/Xtream + روابط tutorials
→ بريد تأكيد + إضافة للوحة /account
```

### Flow 3 — دعم فني (مشترك عنده تقطيع في مباراة)
```
/support → بحث في FAQ (اقتراحات فورية أثناء الكتابة)
→ لم يجد الحل → /support/new
→ نموذج: نوع المشكلة (تقطيع/تسجيل دخول/دفع)، الجهاز، الأولوية
→ إن كان مسجلاً: ربط تلقائي بالاشتراك؛ تصنيف تلقائي + SLA (عاجل: 15 دقيقة)
→ إشعار للفريق (Telegram/Slack) → رد في /support/ticket/[id] (محادثة real-time)
→ إغلاق + تقييم CSAT
```

---

## 3. Data Models

```prisma
model User {
  id            String   @id @default(cuid())
  email         String   @unique
  phone         String?          // WhatsApp
  passwordHash  String?
  role          Role     @default(CUSTOMER)   // CUSTOMER | AGENT | ADMIN
  subscriptions Subscription[]
  tickets       Ticket[]
  trials        Trial[]
  createdAt     DateTime @default(now())
}

model Plan {                      // جدول الأسعار الديناميكي
  id            String  @id
  name          Json              // { ar, en }
  durationDays  Int
  price         Decimal
  compareAtPrice Decimal?         // للخصومات
  maxDevices    Int
  features      Json              // ["4K", "VOD", "EPG", ...]
  isPopular     Boolean @default(false)
  isActive      Boolean @default(true)
  sortOrder     Int
}

model Subscription {
  id           String   @id @default(cuid())
  userId       String
  planId       String
  status       SubStatus // PENDING | ACTIVE | EXPIRED | CANCELLED
  panelLineId  String?   // معرف الخط في IPTV panel
  m3uUrl       String?
  xtreamUser   String?
  xtreamPass   String?   // encrypted
  startsAt     DateTime
  expiresAt    DateTime
  payments     Payment[]
}

model Trial {
  id           String   @id @default(cuid())
  email        String
  phone        String?
  deviceType   String
  fingerprint  String    // منع تكرار التجربة
  ipHash       String
  status       TrialStatus // PENDING | ACTIVE | EXPIRED | CONVERTED
  panelLineId  String?
  expiresAt    DateTime
  @@index([fingerprint, ipHash])
}

model Payment {
  id             String @id @default(cuid())
  subscriptionId String
  provider       String   // stripe | crypto | manual
  amount         Decimal
  currency       String
  status         String   // pending | paid | failed | refunded
  externalId     String?
}

model Ticket {
  id        String   @id @default(cuid())
  userId    String?
  email     String
  subject   String
  category  TicketCategory // STREAMING | LOGIN | BILLING | DEVICE | OTHER
  priority  Priority       // LOW | NORMAL | URGENT
  status    TicketStatus   // OPEN | IN_PROGRESS | WAITING | RESOLVED | CLOSED
  messages  TicketMessage[]
  csatScore Int?
  createdAt DateTime @default(now())
}

model TicketMessage {
  id        String @id @default(cuid())
  ticketId  String
  authorId  String?     // null = زائر
  isStaff   Boolean
  body      String
  attachments Json?
  createdAt DateTime @default(now())
}

model Tutorial {                 // CMS-driven
  id        String @id
  slug      String @unique
  device    String              // smart-tv, android-tv, ...
  title     Json                // { ar, en }
  steps     Json                // MDX/blocks مع صور
  appLinks  Json?
  updatedAt DateTime
}

model Channel {                  // دليل القنوات للعرض/SEO
  id       String @id
  name     String
  category String   // sports | movies | kids | news
  country  String
  quality  String   // SD | HD | FHD | 4K
  logoUrl  String
}
```

---

## 4. API Requirements

| Method | Endpoint | الوظيفة | ملاحظات |
|---|---|---|---|
| POST | `/api/trial` | إنشاء تجربة أوتوماتيكية | rate-limit 3/IP/يوم، fingerprint check، يستدعي Panel API |
| GET | `/api/trial/[id]/status` | حالة التجربة | polling للنجاح |
| GET | `/api/plans` | الباقات النشطة | cached (ISR/Edge, 60s) |
| POST | `/api/checkout` | إنشاء جلسة دفع | Stripe Checkout / بديل |
| POST | `/api/webhooks/stripe` | تأكيد الدفع → تفعيل الخط | idempotent، توقيع موقّع |
| POST | `/api/panel/provision` | (داخلي) إنشاء خط في IPTV panel | queue + retry (Xtream/XUI API) |
| GET | `/api/channels?category=&q=` | بحث/فلترة القنوات | edge-cached |
| POST | `/api/tickets` | فتح تذكرة | يعمل للزوار والمسجلين |
| GET/POST | `/api/tickets/[id]/messages` | محادثة التذكرة | SSE أو Pusher للـ real-time |
| POST | `/api/auth/*` | تسجيل/دخول/OTP | NextAuth / Lucia |
| GET | `/api/account/subscription` | حالة الاشتراك + بيانات الاتصال | |
| POST | `/api/notify` | (داخلي) بريد + واتساب | Resend + WhatsApp Cloud API |
| CRON | `/api/cron/expiry-reminders` | تذكير انتهاء التجربة/الاشتراك | Vercel Cron |

**تكاملات خارجية:** IPTV Panel (Xtream UI/XUI.one API) · Stripe (+بوابة كريبتو اختيارية) · Resend (بريد) · WhatsApp Cloud API · Telegram Bot (تنبيهات الفريق) · Upstash Redis (rate-limit + queue).

---

## 5. Component Inventory (34 عنصراً)

**Layout (5):** `Header` (شفاف→صلب عند التمرير) · `MobileNav` (drawer) · `Footer` · `LangSwitcher` (ar/en + RTL) · `AnnouncementBar` (عروض)

**Marketing (9):** `Hero` (فيديو/صورة 4K) · `TrustBadges` (uptime, أجهزة, دول) · `CategoryShowcase` (رياضة/أفلام/عائلة tabs) · `ChannelLogoMarquee` · `VODCarousel` (بوسترات lazy) · `StatsStrip` · `TestimonialSlider` · `FAQAccordion` · `CTASection`

**Pricing (4):** `PricingTable` (ديناميكي) · `PlanCard` (badge "الأكثر طلباً") · `BillingToggle` (شهري/سنوي مع نسبة التوفير) · `FeatureComparisonTable`

**Trial & Checkout (6):** `TrialForm` (multi-step) · `DeviceSelector` (أيقونات الأجهزة) · `OTPInput` · `CredentialsCard` (نسخ M3U/Xtream بضغطة) · `CheckoutSummary` · `PaymentMethodPicker`

**Tutorials (4):** `TutorialCard` · `StepGuide` (خطوات مرقمة + صور) · `DeviceTabs` · `VideoEmbed` (facade — لا يحمّل YouTube إلا عند الضغط)

**Support (4):** `TicketForm` · `TicketThread` (محادثة) · `TicketStatusBadge` · `SearchSuggest` (بحث FAQ فوري)

**Shared/UI (6+):** `Button` · `Input/Select/Textarea` · `Modal` · `Toast` · `Skeleton` · `Badge` · `CopyButton` · `EmptyState`

---

## 6. Page Templates (Wireframes)

### الرئيسية `/`
```
┌──────────────────────────────────────┐
│ AnnouncementBar (خصم 40%)            │
│ Header: Logo | Nav | [تجربة مجانية]  │
├──────────────────────────────────────┤
│ HERO: عنوان + "20,000 قناة 4K"      │
│ [ابدأ التجربة المجانية] [الباقات]    │
│ خلفية: كولاج بوسترات (blur-up)       │
├──────────────────────────────────────┤
│ TrustBadges: 99.9% uptime | كل جهاز │
│ CategoryShowcase: رياضة⚽|أفلام🎬|عائلة│
│ VODCarousel (بوسترات lazy)           │
│ PricingTable (مختصر، 3 باقات)        │
│ TutorialTeaser (شبكة أجهزة)          │
│ Testimonials → FAQ → CTA أخير        │
│ Footer                               │
└──────────────────────────────────────┘
```

### `/pricing`
```
│ H1 + BillingToggle (شهري/6أشهر/سنوي) │
│ [PlanCard][PlanCard★popular][PlanCard]│
│ FeatureComparisonTable (sticky header)│
│ ضمان استرداد + FAQ الدفع → CTA        │
```

### `/free-trial`
```
│ يسار: TrialForm (3 خطوات:            │
│  بياناتك → جهازك → OTP)              │
│ يمين: ماذا ستحصل (24h، 4K، VOD)      │
│ Success: CredentialsCard + زر        │
│ "شغّلها على [جهازك]" → tutorial       │
```

### `/tutorials/[device]`
```
│ Breadcrumb + DeviceTabs              │
│ StepGuide: 1..N (صورة + شرح + نسخ)  │
│ VideoEmbed (facade) → روابط التطبيقات│
│ "ما زالت المشكلة؟" → /support/new    │
```

### `/support/ticket/[id]`
```
│ Header: #ID + StatusBadge + SLA timer│
│ TicketThread (رسائل، مرفقات)         │
│ Composer + إغلاق/تقييم               │
```

---

## 7. Tech Stack Recommendation

| الطبقة | الاختيار | لماذا |
|---|---|---|
| Framework | **Next.js 15 (App Router) على Vercel** | RSC + ISR + Edge = سرعة VOD library وSEO ممتاز |
| Language | TypeScript | |
| Styling | Tailwind CSS + shadcn/ui | RTL جاهز عبر logical properties |
| DB | **PostgreSQL (Neon)** + Prisma | serverless-friendly |
| Cache/Queue | Upstash Redis | rate-limit التجارب + طوابير الـ provisioning |
| Auth | Auth.js v5 (email OTP + credentials) | |
| Payments | Stripe + (NOWPayments للكريبتو اختياري) | |
| Email/WA | Resend + WhatsApp Cloud API | أوتوماتيكية التجربة والتذكير |
| Realtime (تذاكر) | Pusher أو SSE | |
| CMS (tutorials/blog) | MDX في الريبو أو Payload CMS | |
| Images | `next/image` + Vercel Image Optimization (AVIF/WebP) | بوسترات VOD |
| Analytics | Vercel Analytics + Speed Insights | مراقبة الـ budgets |
| i18n | next-intl (ar افتراضي RTL + en) | |

---

## 8. Performance Budgets

| المقياس | الهدف (موبايل، 4G) |
|---|---|
| LCP | ≤ 2.0s (hero image priority + AVIF) |
| INP | ≤ 200ms |
| CLS | ≤ 0.05 (أبعاد ثابتة للبوسترات) |
| TTFB | ≤ 300ms (Edge/ISR) |
| JS الأولي (home) | ≤ 170KB gz (RSC، لا سلايدر ثقيل) |
| صورة البوستر | ≤ 25KB (AVIF 2x) |
| إجمالي الصفحة الأولى | ≤ 1MB |
| Lighthouse | ≥ 95 Performance / 100 SEO |

**تكتيكات VOD library:** RSC + streaming، `loading="lazy"` بعد أول صفين، `content-visibility: auto` للكاروسيلات، blur placeholders، virtualization عند القوائم الطويلة، YouTube facade في tutorials، خطوط عربية self-hosted بـ `font-display: swap` + subset.

---

## 9. SEO Structure

**استهداف الكلمات:**
| الصفحة | الكلمات |
|---|---|
| `/` | اشتراك IPTV، IPTV 4K، أفضل سيرفر IPTV |
| `/pricing` | أسعار اشتراك IPTV، اشتراك IPTV سنوي |
| `/channels` | قنوات bein IPTV، قنوات رياضية 4K |
| `/tutorials/*` | تشغيل IPTV على سامسونج/أندرويد… (long-tail قوي) |
| `/blog/*` | مقارنات، "أفضل تطبيق IPTV 2026" |

**تقني:**
- Metadata API لكل صفحة: title ≤60 حرف بنمط `اشتراك IPTV 4K | {Brand}` + canonical + OG.
- `hreflang` ar/en، HTML `dir="rtl" lang="ar"`.
- **Structured Data (JSON-LD):** `Product`+`Offer`+`AggregateRating` في pricing · `FAQPage` · `HowTo` في tutorials · `Organization` · `BreadcrumbList`.
- `sitemap.xml` مولّد ديناميكياً + `robots.txt` (حجب /account, /checkout, /api).
- Internal linking: كل tutorial ↔ pricing ↔ free-trial؛ blog يغذي الصفحات التجارية.
- كل صفحات التسويق SSG/ISR (لا CSR) لضمان الفهرسة، وCore Web Vitals ضمن الأخضر (عامل ترتيب).

---

## خارطة تنفيذ مقترحة
1. **أسبوع 1–2:** Scaffold + التصميم + الرئيسية وpricing (ديناميكي).
2. **أسبوع 3–4:** Free-trial pipeline (Panel API + OTP + أوتوماتيكية البريد/واتساب).
3. **أسبوع 5:** Checkout + Webhooks + لوحة الحساب.
4. **أسبوع 6:** Tutorials CMS + نظام التذاكر + real-time.
5. **أسبوع 7–8:** SEO/JSON-LD، تحسين الأداء لتحقيق الـ budgets، QA على TV browsers.
