# Frontend Logic Architecture — IPTV Premium Sverige
**Stack assumptions:** Next.js 15 App Router · TypeScript · Zustand (client state) · TanStack Query (server state) · react-hook-form + zod · XState-style state machines (مطبّقة كـ `useReducer` typed unions)

**مبدأ عام:** كل تدفق حرج = state machine صريحة (لا booleans متناثرة). Server state عبر TanStack Query حصراً؛ Zustand فقط للـ UI state العابر.

---

## 1. Checkout Wizard — نموذج متعدد الخطوات
`/checkout` — تحقق بريد → باقة → دفع → تفعيل + توليد M3U

### State machine
```
IDLE
 └─ START ──────────────► STEP_EMAIL
STEP_EMAIL
 ├─ SUBMIT_EMAIL ───────► EMAIL_SENDING ── ok ──► STEP_OTP
 │                                        └ err ─► STEP_EMAIL (error=rate_limit|invalid|network)
STEP_OTP
 ├─ SUBMIT_OTP ─────────► OTP_VERIFYING ── ok ──► STEP_PLAN
 │                                        └ err ─► STEP_OTP (attempts++, ≥5 → OTP_LOCKED 10min)
 ├─ RESEND (cooldown 60s) ► EMAIL_SENDING
 └─ CHANGE_EMAIL ───────► STEP_EMAIL
STEP_PLAN
 ├─ SELECT_PLAN(planId, duration, devices) ► STEP_PAYMENT
 └─ BACK ───────────────► STEP_OTP (skipped — email verified persists)
STEP_PAYMENT
 ├─ PAY ────────────────► PAYMENT_PENDING (redirect Stripe/Swish)
 └─ BACK ───────────────► STEP_PLAN
PAYMENT_PENDING  (المستخدم عاد من بوابة الدفع)
 ├─ webhook confirmed ──► PROVISIONING
 ├─ payment failed ─────► STEP_PAYMENT (error=declined|cancelled)
 └─ timeout 120s ───────► PAYMENT_UNKNOWN (رسالة: تحقق من بريدك / support CTA)
PROVISIONING  (polling GET /api/orders/[id] كل 2s، max 45s)
 ├─ status=active ──────► SUCCESS (m3uUrl, xtreamCreds)
 ├─ status=failed ──────► PROVISION_FAILED (retry CTA → PROVISIONING، auto-ticket بعد فشلين)
 └─ timeout ────────────► PROVISION_DELAYED ("يُفعّل خلال دقائق، سنراسلك" — الطلب مدفوع)
SUCCESS  → عرض CredentialsCard + tutorial link
```

### Data flow
```tsx
<CheckoutWizard>                        // يملك الـ machine (useReducer + context)
 ├── <StepIndicator current={step}/>    // props: step, steps[]
 ├── <EmailStep onSubmit={email}/>      // POST /api/auth/otp/send
 ├── <OTPStep onVerify={code}/>         // POST /api/auth/otp/verify → session cookie
 ├── <PlanStep>                         // GET /api/plans (useQuery, staleTime 60s)
 │    └── <PricingCalculator .../>      // (المكوّن 2 — مضمّن هنا)
 ├── <PaymentStep>                      // POST /api/checkout → { redirectUrl }
 ├── <ProvisioningStep orderId/>        // useQuery refetchInterval:2000, enabled: pending
 └── <SuccessStep creds/>               // <CredentialsCard/> + <CopyButton/>
```
- **Persistence:** الـ context (step + email + planId) يُخزن في `sessionStorage` — العودة من Stripe redirect تستعيد الحالة. `orderId` في query param كمصدر حقيقة.
- **Events up, data down:** كل Step يستقبل `data` + `dispatch` فقط؛ لا API calls خارج الـ hooks المخصصة (`useSendOtp`, `useCreateCheckout`…).

### Error handling
| خطأ | معالجة |
|---|---|
| OTP خاطئ | inline error + هزة، عداد محاولات ظاهر (`3 av 5 försök`) |
| Rate limit (بريد) | رسالة + cooldown timer مرئي، الزر disabled |
| فشل دفع | العودة لـ STEP_PAYMENT مع سبب مترجم (declined/insufficient) — لا تفريغ الاختيارات |
| فشل provisioning | **الدفع تم** — لا نُظهر "فشل" مخيف؛ "التفعيل يأخذ وقتاً أطول من المعتاد" + فتح تذكرة تلقائي |
| Network | retry تلقائي (React Query retry:2) ثم زر "Försök igen" |

### Loading / Empty
- كل انتقال async: زر بـ spinner **مع ثبات العرض**، الخطوة الحالية تبقى تفاعلية للتعديل.
- PROVISIONING: شاشة progress بمراحل نصية ("Bekräftar betalning ✓ → Skapar ditt konto… → Genererar M3U…") — تقلل القلق.
- PlanStep بلا باقات (خطأ API): EmptyState + retry.

### Edge cases
- **رجوع المتصفح:** الـ machine مربوطة بـ `?step=` في URL (shallow) — back يعمل طبيعياً، لكن لا يمكن القفز أمام خطوة غير مكتملة (guard في reducer).
- **بريد مسجل مسبقاً:** OTP verify يرجع `existingUser:true` → دمج بجلسة دخول بدل إنشاء حساب.
- **دفعة مكررة (double-click):** idempotency key = `orderId` يُنشأ مرة عند دخول STEP_PAYMENT.
- **Webhook وصل قبل عودة المستخدم:** polling يجد `active` فوراً → قفزة مباشرة لـ SUCCESS.
- **تبويبان مفتوحان:** `BroadcastChannel` يزامن SUCCESS بين التبويبات.
- **انتهاء صلاحية OTP أثناء الكتابة:** خطأ `expired` → زر resend بارز بدل رسالة فشل عامة.

---

## 2. Dynamic Pricing Calculator
حساب فوري: المدة (1/3/6/12 شهر) × عدد الأجهزة (1–5)

### State machine (بسيطة — derived state أكثر منها machine)
```
LOADING_PLANS ── ok ──► READY(duration=12, devices=2)   // defaults الأعلى تحويلاً
              └ err ──► ERROR (retry)
READY
 ├─ SET_DURATION(d) ──► READY'   (إعادة حساب synchronous)
 ├─ SET_DEVICES(n) ───► READY'
 └─ SELECT ───────────► emits onSelect(quote)
```

### Data flow
```tsx
<PricingCalculator onSelect={quote => ...}>
 ├── <DurationToggle value onChange/>      // segmented: 1|3|6|12 mån
 ├── <DeviceStepper value onChange/>       // 1–5 + "− / +"
 ├── <PriceDisplay quote/>                 // السعر الكبير + /mån + التوفير
 └── <SavingsBadge/>                       // "Spara 45 %" — يتحرك عند التغيير
```
- **التسعير قاعدة بيانات لا hard-code:** `GET /api/plans` يرجع مصفوفة `{durationMonths, basePrice, perExtraDevice, discountPct}`. الحساب **client-side pure function**:
```ts
quote = (base + perExtraDevice * (devices - 1)) * months * (1 - discountPct)
// دالة نقية مُختبرة unit-test، نفسها تعمل server-side للتحقق النهائي
```
- **⚠️ السعر النهائي يُعاد حسابه في السيرفر عند checkout** — الحاسبة عرض فقط؛ العميل يرسل `(planId, duration, devices)` لا السعر.

### Errors / Loading / Empty
- LOADING: skeleton بنفس أبعاد الحاسبة (لا CLS).
- فشل التحميل: أسعار fallback ثابتة من الـ build (آخر ISR snapshot) + شارة "priser uppdateras…" — الحاسبة لا تختفي أبداً (صفحة تحويل حرجة).
- تغيّر السعر بين العرض والدفع (admin عدّل): السيرفر يرفض بـ `PRICE_CHANGED` → toast + إعادة تحميل الأسعار، الاختيارات محفوظة.

### Edge cases
- تحريك سريع متكرر للـ toggle: الحساب synchronous فلا debounce مطلوب؛ **الأنيميشن** (count-up للسعر) يُقاطَع ويقفز للقيمة الأخيرة.
- `devices > maxDevices` لباقة معينة: الخيار يُعطّل مع tooltip، لا يُخفى.
- عملة: SEK ثابتة، تنسيق `Intl.NumberFormat('sv-SE')` — "449 kr" وليس "kr449".
- URL sync: `?months=12&devices=2` — مشاركة الرابط تستعيد الاختيار (وتفيد إعلانات بسعر محدد).

---

## 3. Faceted Search — VOD + القنوات
`/filmer`, `/kanaler` — فلاتر + ترتيب + pagination

### State machine
```
INIT (قراءة URL params) ──► FETCHING
FETCHING ── ok(>0) ──► RESULTS
         ├─ ok(0) ───► EMPTY (اقتراحات: امسح الفلاتر / كلمات قريبة)
         └─ err ─────► ERROR (retry، آخر نتائج ناجحة تبقى معروضة باهتة)
RESULTS / EMPTY / ERROR
 ├─ SET_QUERY(q)   ── debounce 250ms ──► FETCHING (page=1)
 ├─ TOGGLE_FACET(f)──────────────────► FETCHING (page=1)
 ├─ SET_SORT(s) ──────────────────────► FETCHING (page=1)
 ├─ SET_PAGE(p) ──────────────────────► FETCHING (append إن infinite)
 └─ CLEAR_ALL ────────────────────────► FETCHING (defaults)
```

### Data flow
```tsx
<SearchPage>                          // Server Component: أول صفحة SSR من searchParams (SEO!)
 └── <SearchProvider initialData>     // client — nuqs لمزامنة URL ↔ state
      ├── <SearchInput/>              // debounced، ⌘K focus
      ├── <FacetSidebar facets/>      // genre, year, quality(4K/HD), language, country
      │    └── <FacetGroup/>          // checkboxes + عدّاد نتائج لكل خيار (من الـ API)
      ├── <ActiveFilterChips/>        // chips قابلة للإزالة + "Rensa alla"
      ├── <SortSelect/>               // relevans | nyast | a-ö | betyg
      ├── <ResultsGrid items/>        // PosterCard / ChannelTile، virtualized بعد 100 عنصر
      └── <Paginator/> أو infinite scroll (IntersectionObserver)
```
- **API:** `GET /api/search?q=&type=vod|channel&genre[]=&quality[]=&sort=&page=` → `{ items, total, facetCounts }`. `useQuery` بـ `placeholderData: keepPreviousData` (النتائج القديمة تبقى أثناء الجلب — لا وميض).
- **URL = مصدر الحقيقة الوحيد** للفلاتر (nuqs). زر back/forward وrefresh ومشاركة الرابط تعمل مجاناً، وصفحات الفلاتر الشائعة قابلة للفهرسة (SEO).

### Errors / Loading / Empty
- أول تحميل: skeleton grid 12 بطاقة بأبعاد البوستر الثابتة.
- جلب تالٍ: النتائج السابقة بـ `opacity:.5` + progress bar رفيع أعلى الشبكة (لا layout shift).
- EMPTY: "Inga träffar för ’{q}’" + أزرار: إزالة آخر فلتر (الأرجح سبباً)، مسح الكل، وأشهر 6 عناوين كـ fallback.
- ERROR: toast غير مقاطِع + النتائج الأخيرة تبقى + retry.

### Edge cases
- **Race conditions:** React Query يلغي الطلبات المتقادمة تلقائياً (`AbortSignal`) — كتابة سريعة لا تعرض نتائج قديمة.
- فلتر بلا نتائج متبقية (count=0): يبقى ظاهراً معطّلاً — إخفاؤه يسبب قفز الواجهة.
- استعلام بحروف سويدية (å/ä/ö): normalization في السيرفر (`smorgas` يطابق `smörgås`).
- صفحة عميقة عبر URL مباشرة (`page=40` وما عادت موجودة): السيرفر يرجع آخر صفحة صالحة + canonical.
- infinite scroll + back: حفظ scroll position عبر `sessionStorage` (key = URL).
- XSS في `q`: يُعرض دائماً كنص (React default) ويُرسل encoded.

---

## 4. User Dashboard — `/konto`
إدارة الاشتراك، التجديد، الأجهزة، تحميل التطبيقات، viz للاستخدام

### State machine (per-widget، ليس صفحة واحدة)
```
الصفحة: AUTH_CHECK ── no session ──► redirect /logga-in?next=/konto
                    └ ok ─────────► HYDRATED (كل widget مستقل)

SubscriptionCard:  LOADING → ACTIVE | EXPIRING(<7d) | EXPIRED | PENDING_PAYMENT
  ACTIVE ── RENEW ──► RenewFlow (checkout مصغّر: خطة → دفع → confirm)
  EXPIRING: banner + CTA بارز "Förnya nu — behåll ditt pris"
  EXPIRED: كل الـ widgets الأخرى تتحول read-only + upsell

DeviceManager (CRUD):
  LIST ── ADD ────► (تحقق limit) ok → optimistic add → POST /api/devices
       │                         limit → MODAL_UPSELL (ترقية الباقة)
       ├─ RENAME ─► inline edit → PATCH (optimistic, rollback on err)
       └─ REMOVE ─► CONFIRM_MODAL → DELETE → invalidate
```

### Data flow
```tsx
<DashboardLayout>                    // Server Component: session + prefetch أساسي
 ├── <SubscriptionCard/>             // GET /api/account/subscription
 │    ├── <StatusBadge/> <ExpiryCountdown/>   // "23 dagar kvar" + progress ring
 │    └── <RenewButton/> → <RenewModal/>      // POST /api/checkout (mode:renew)
 ├── <CredentialsCard/>              // M3U/Xtream + <CopyButton/> + regenerate
 ├── <DeviceManager/>                // GET/POST/PATCH/DELETE /api/devices
 ├── <UsageViz/>                     // GET /api/account/usage → recharts
 │    // مشاهدة أسبوعية (bar) + أكثر الفئات (donut) — lazy loaded (dynamic import)
 ├── <AppDownloads/>                 // static + منطق: يُبرز تطبيق جهاز المستخدم أولاً
 └── <TicketsWidget/>                // آخر 3 تذاكر + unread badge
```
- **Mutations:** كلها TanStack `useMutation` مع optimistic updates + `onError` rollback + `invalidateQueries(['account'])`.
- **Regenerate password (Xtream):** تأكيد modal بتحذير "كل أجهزتك ستحتاج إعادة إدخال" → POST → عرض الجديد مرة واحدة.

### Errors / Loading / Empty
- كل widget له skeleton مستقل — فشل واحد لا يسقط الصفحة (error boundary لكل widget + retry داخلي).
- UsageViz بلا بيانات (مشترك جديد): empty state إيجابي "Din statistik dyker upp efter första veckan 📊".
- DeviceManager فارغ: CTA "Lägg till din första enhet" + رابط الدليل.
- فشل mutation: toast خطأ + rollback مرئي (العنصر يعود) — أبداً حالة UI كاذبة.

### Edge cases
- **اشتراك انتهى أثناء الجلسة المفتوحة:** polling خفيف (refetchInterval 60s على subscription فقط) يقلب الحالة لـ EXPIRED live.
- تجديد أثناء PENDING_PAYMENT سابق: زر التجديد معطّل + رابط "أكمل الدفع السابق".
- حذف الجهاز الحالي الذي يشاهد منه: تحذير خاص في الـ confirm.
- session انتهت وسط mutation: 401 → interceptor يعيد التوجيه مع `?next=` وحفظ الـ intent في sessionStorage لإعادته بعد الدخول.
- countdown عبر timezones: العدّ من `expiresAt` UTC، العرض بـ `Intl` Stockholm.

---

## 5. Auth Flow — login / signup / reset

### State machine
```
LOGIN
 ├─ SUBMIT(email, pass) ► AUTHENTICATING ── ok ──► redirect(next ?? /konto)
 │                                         ├ invalid ──► LOGIN (error، عداد → captcha بعد 3)
 │                                         ├ unverified ► VERIFY_PROMPT (resend OTP)
 │                                         └ locked ───► LOCKED (رسالة + reset CTA)
 └─ "Glömt lösenord?" ──► RESET_REQUEST

SIGNUP
 ├─ SUBMIT ► CREATING ── ok ──► VERIFY_EMAIL (OTP — نفس مكوّن الـ wizard)
 │                     ├ email_taken ► SIGNUP (error + "Logga in i stället?" link)
 │                     └ weak_pass ──► SIGNUP (zod client-side يمنع أصلاً)
 VERIFY_EMAIL ── ok ──► ONBOARDING (اختيار الجهاز → توجيه للدليل) ──► /konto

RESET_REQUEST ── SUBMIT(email) ► SENT (نفس الرسالة سواء وُجد البريد أم لا — no enumeration)
RESET_CONFIRM (/aterstall?token=)
 ├─ token valid ──► NEW_PASSWORD ── SUBMIT ──► ok → LOGIN (toast "Klart! Logga in")
 └─ token invalid/expired ──► TOKEN_ERROR ("länken har gått ut" + resend)
```

### Data flow
```tsx
<AuthCard mode="login|signup|reset">      // صفحة واحدة، تبديل بلا reload (URL يتغير)
 ├── <AuthForm/>          // react-hook-form + zodResolver — validation onBlur ثم onChange
 ├── <PasswordInput/>     // إظهار/إخفاء + strength meter (signup فقط، zxcvbn lazy)
 ├── <OTPInput/>          // مُعاد استخدامه من الـ wizard
 └── <SocialAuth/>        // Google OAuth (اختياري v2)
```
APIs: `POST /api/auth/{login,register,otp/verify,reset/request,reset/confirm}` — Auth.js session cookie (httpOnly). لا tokens في localStorage.

### Errors / Loading / Empty
- أخطاء الحقول: inline تحت الحقل، تختفي عند التصحيح. خطأ عام (credentials): فوق الزر، **لا يحدد** أيهما خاطئ (بريد/كلمة).
- AUTHENTICATING: زر spinner + الفورم disabled — لكن قابل للإلغاء بعد 10s (timeout → خطأ شبكة).
- Caps Lock مفعّل في حقل كلمة المرور: تلميح غير مقاطِع.

### Edge cases
- **Enumeration protection:** reset وsignup لا يكشفان وجود البريد (رسائل عامة، توقيت متساوٍ).
- rate limiting: 5 محاولات login → captcha (Turnstile)، 10 → lock مؤقت 15 دقيقة.
- token reset مستخدم مرتين: invalid فوراً (single-use).
- مستخدم مسجل يفتح /logga-in: redirect صامت لـ /konto.
- `?next=` validation: paths داخلية فقط (منع open redirect).
- autofill iOS/1Password: أسماء حقول قياسية + `autocomplete="current-password|new-password|one-time-code"`.
- مستخدم أنشأ حساباً عبر trial (passwordless): login بكلمة مرور يرجع `use_otp` → تحويل تلقائي لتدفق OTP.

---

## هيكل React الكلي

```
src/
├── app/                              # App Router
│   ├── (marketing)/                  # SSG/ISR — layout داكن كامل
│   │   ├── page.tsx                  # Home
│   │   ├── priser/  gratis-test/  guider/[device]/  kanaler/  filmer/
│   ├── (auth)/logga-in/  registrera/  aterstall/
│   ├── (app)/konto/...               # protected (middleware session check)
│   ├── checkout/[planId]/
│   └── api/...                       # route handlers
├── components/
│   ├── ui/                           # design system primitives (Button, Input, Modal…)
│   ├── checkout/                     # CheckoutWizard + steps + machine.ts
│   ├── pricing/                      # PricingCalculator + quote.ts (pure, unit-tested)
│   ├── search/                       # SearchProvider, FacetSidebar, ResultsGrid
│   ├── dashboard/                    # widgets (كل واحد بـ error boundary)
│   └── auth/
├── hooks/                            # useSendOtp, useCheckout, useDevices…
│   └── (كل API call = hook واحد — لا fetch داخل components)
├── lib/
│   ├── api-client.ts                 # fetch wrapper: errors typed, 401 interceptor
│   ├── machines/                     # reducers + typed events لكل flow
│   └── validation/                   # zod schemas مشتركة client/server
├── stores/                           # Zustand: ui.ts (modals, toasts) فقط
└── messages/sv.json                  # كل نصوص COPY_SV — لا strings في الكود
```

**قواعد معمارية ملزمة:**
1. Server Components افتراضياً؛ `"use client"` فقط عند الحاجة (forms, machines).
2. كل تدفق async حرج له union type للحالة — ممنوع `isLoading && isError` combos.
3. أي سعر أو صلاحية تُحسب في السيرفر نهائياً؛ الـ client عرض فقط.
4. كل mutation: optimistic + rollback + invalidate — بلا استثناء.
5. الـ URL هو state للـ search والفلاتر والخطوات — قابل للمشاركة دائماً.
```
