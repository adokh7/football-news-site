# QA Specification Review — IPTV Premium Sverige
**النطاق:** مراجعة الوثائق العشر (architecture, design-system, content, figma prompts) قبل البناء.
**الترميز:** ✅ مغطى · ⚠️ فجوة تحتاج إصلاحاً · ❌ غائب كلياً · الخطورة: P0 (يمنع الإطلاق) / P1 (قبل الإطلاق) / P2 (بعده)

**الحكم العام: المواصفة ناضجة (85%) — لكن وجدت فجوتين ❌ كبيرتين (Analytics غائب كلياً، CSP غير معرّف) و11 ⚠️ يجب إغلاقها قبل البناء.**

---

## 1. Performance — Core Web Vitals ✅ (مع 3 ⚠️)

| بند | حالة |
|---|---|
| Budgets رقمية معلنة (LCP≤2s، INP≤200ms، CLS≤0.05، JS≤170KB) | ✅ ARCHITECTURE §8 |
| srcset/AVIF/blur-up/lazy/facade | ✅ RESPONSIVE + MOTION |
| skeletons بأبعاد ثابتة (CLS) | ✅ |
| **⚠️ P1 — PlanCard الشعبية `scale(1.03)`** | إن طُبّقت كـ layout scale عند التحميل ستحرّك الجيران → CLS. **الإصلاح:** scale بـ transform منذ الـ SSR الأول (لا حالة "قبل/بعد")، واحجز المساحة. |
| **⚠️ P1 — خط Clash Display** | لا مواصفة subset/preload له. عنوان hero هو الـ LCP element — خط متأخر = FOUT على أهم عنصر. **الإصلاح:** `next/font` self-host + subset لاتيني/سويدي + preload للـ display weight الواحد المستخدم. |
| **⚠️ P2 — count-up + parallax على أجهزة ضعيفة** | لا معيار قياس محدد. **الإصلاح:** إضافة بند "يقاس على Moto G4 throttled 4x" لبروتوكول الاختبار، وتعطيل الـ parallax تحت `navigator.hardwareConcurrency < 4`. |
| **⚠️ P2 — ميزانية third-party غير معرّفة** | حين يُضاف analytics/chat لاحقاً سينفجر الـ 170KB بصمت. **الإصلاح:** بند صريح: third-party ≤ 30KB إجمالاً، تحميل بعد onLoad. |

## 2. Accessibility — WCAG 2.2 AA ✅ (مع 3 ⚠️)

| بند | حالة |
|---|---|
| تباين محسوب بالأرقام لكل الأزواج | ✅ DESIGN_SYSTEM §7 |
| focus-visible + keyboard + focus trap + skip link | ✅ |
| reduced-motion شامل | ✅ tokens.css |
| touch targets ≥44px + لا لون وحده + ARIA للفورم | ✅ |
| **⚠️ P1 — WCAG 2.2 الجديدة تحديداً:** المواصفة كُتبت بروح 2.1. البنود الجديدة في 2.2 غير مذكورة: **2.4.11 Focus Not Obscured** (الهيدر اللاصق + bottom tab bar قد يحجبان العنصر المركَّز عند التنقل بالكيبورد — يلزم `scroll-padding-top: 80px`)، **3.3.8 Accessible Authentication** (OTP يجب أن يقبل paste ولا يمنع اللصق — غير منصوص)، **2.5.7 Dragging Movements** (swipe-down لإغلاق المودال يحتاج بديل زر ✕ — موجود ضمنياً، يجب نصّه). |
| **⚠️ P1 — الكاروسيلات** | لا مواصفة ARIA لها (أهم نمط في الموقع). **الإصلاح:** `role="region"` + `aria-roledescription="carousel"` + أزرار prev/next مخفية بصرياً على الموبايل لمستخدمي الكيبورد، والبوسترات المقصوصة (peek 2.4) يجب أن تبقى focusable. |
| **⚠️ P2 — الرسوم البيانية (UsageViz)** | recharts بلا نص بديل. **الإصلاح:** جدول بيانات مخفي `sr-only` مرافق لكل chart. |

## 3. SEO ✅ (مع 2 ⚠️)

| بند | حالة |
|---|---|
| خريطة كلمات سويدية لكل صفحة، JSON-LD (Product/FAQ/HowTo/Breadcrumb)، sitemap ديناميكي، robots، canonical، SSG/ISR | ✅ ARCHITECTURE §9 |
| **⚠️ P1 — hreflang يتيم:** المواصفة القديمة تذكر ar/en والذاكرة الحالية سويدي. | **الإصلاح:** v1 لغة واحدة `sv-SE` — احذف بنود hreflang من ARCHITECTURE §9 حتى تُضاف لغة ثانية فعلياً (hreflang لصفحات غير موجودة = ضرر). حدّث أيضاً بنية `name: Json {ar,en}` في Plan/Tutorial → `{sv}` أو حقل نصي. |
| **⚠️ P2 — صفحات الفلاتر القابلة للفهرسة** | FRONTEND_LOGIC يجعل كل URL فلترة قابلاً للفهرسة → انفجار crawl budget وduplicate content. **الإصلاح:** فهرسة فئات مختارة فقط (genre, quality) بـ canonical، والباقي `noindex,follow` + حظر التركيبات >2 فلاتر في robots. |
| ملاحظة تدقيق نصوص: COPY_SV يحتوي خطأ إملائياً في برومبت Figma 4 ("Ma zolde du fast?" → "Blev du fast?") — يصحح قبل التوليد. | ⚠️ P2 |

## 4. Security ⚠️ (فجوة ❌ واحدة كبيرة)

| بند | حالة |
|---|---|
| session httpOnly، لا creds في localStorage، webhook signatures + idempotency، step-up re-auth، rate limiting، enumeration protection، `?next=` validation، تشفير كلمات الـ Panel | ✅ DATA_INTEGRATION §3 — ممتاز |
| **❌ P0 — CSP وsecurity headers غير معرّفة إطلاقاً.** | لا توجد مواصفة لـ Content-Security-Policy أو باقي الرؤوس. موقع يعرض بيانات M3U ويستقبل مدفوعات بلا CSP = ثغرة مفتوحة. **الإصلاح المطلوب (next.config headers):** `CSP` بـ nonce للـ scripts + `frame-src` لـ Stripe فقط + `connect-src` self+Stripe؛ `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`؛ `X-Content-Type-Options: nosniff`؛ `Referrer-Policy: strict-origin-when-cross-origin`؛ `Permissions-Policy` تعطيل camera/mic/geolocation. |
| **⚠️ P1 — Input sanitization في التذاكر:** المرفقات (screenshots) بلا مواصفة: نوع/حجم/فحص. **الإصلاح:** MIME whitelist (png/jpg/webp)، ≤5MB، إعادة ترميز الصورة server-side (تقتل أي payload)، تخزين خارج الـ public path بروابط موقّعة. نص رسائل التذاكر: escape افتراضي (React) + منع الروابط تتحول HTML في ردود الـ staff. |
| **⚠️ P1 — CSRF:** الاعتماد على SameSite=Lax وحده غير منصوص كقرار واعٍ. **الإصلاح:** توثيقه + origin check في كل mutation route handler. |

## 5. Browser Compatibility ⚠️ (لم تُذكر في أي وثيقة كمصفوفة)

| مخاطرة | تفصيل |
|---|---|
| **⚠️ P1 — View Transitions API** | مستخدمة لانتقال البطاقة→checkout والبوستر→مودال. **غير مدعومة في Firefox وSafari < 18.** المواصفة لا تذكر fallback. **الإصلاح:** feature-detect → fallback إلى fade عادي 240ms (المنطق موجود، يجب نصّه). |
| **⚠️ P1 — backdrop-filter (الهيدر المموّه)** | Safari يتطلب `-webkit-` prefix وأداؤه متقلب على iOS القديمة. **الإصلاح:** `@supports` fallback إلى خلفية صلبة rgba(11,11,15,.95). |
| ⚠️ P2 — `scroll-snap` + momentum على iOS Safari: سلوك الـ peek carousel يختبر فعلياً (physics مختلفة). | |
| ⚠️ P2 — AVIF: مدعوم حديثاً في Edge/Safari — `<picture>` مع WebP fallback (مذكور ضمنياً في next/image ✅ لكن ينص). | |
| **الإصلاح الشامل:** إضافة مصفوفة دعم رسمية للوثائق: Chrome/Edge آخر إصدارين، Safari 16.4+، Firefox آخر إصدارين، **Samsung Internet** (جمهور Smart TV يستخدمه!) + Tizen/webOS TV browsers للـ tv breakpoint — smoke test فقط. |

## 6. Mobile Optimization ✅ (مع 2 ⚠️)

| بند | حالة |
|---|---|
| touch ≥44px، thumb zone للـ CTAs، bottom tabs، drawer filters، peek carousels، viewport priorities | ✅ RESPONSIVE_SPEC شامل |
| **⚠️ P1 — viewport meta وsafe-area غير منصوصين:** iPhone بـ notch: bottom tab bar للداشبورد سيتصادم مع home indicator. **الإصلاح:** `viewport-fit=cover` + `padding-bottom: env(safe-area-inset-bottom)` على الـ tab bar والـ CTAs اللاصقة. |
| **⚠️ P2 — keyboard overlap:** فورم الـ trial: فتح الكيبورد فوق OTP inputs قد يخفي زر Submit. **الإصلاح:** `scrollIntoView` عند focus + اختبار على viewport 375×667 مع كيبورد مفتوح. |
| ملاحظة: input font-size يجب ≥16px على iOS (منع auto-zoom) — الـ body 16px يغطيها ✅ لكن caption 13px داخل أي input سيكسرها — ينص. | ⚠️ P2 |

## 7. Analytics Integration ❌ (الفجوة الأكبر — غائب كلياً)

**❌ P0 للأعمال:** موقع هدفه المعلن CONVERSION عبر 10 وثائق — **ولا وثيقة واحدة تعرّف الأحداث أو الأهداف أو القمع.** لا يمكن تحسين ما لا يُقاس. المطلوب (أضفته كمواصفة مصغرة هنا لتُعتمد):

### Event taxonomy (الأساس)
| Event | Params | يقيس |
|---|---|---|
| `trial_started` | device_type, source | بدء الفورم |
| `trial_step_completed` | step (1/2/3) | تسرب الخطوات |
| `trial_activated` | device_type | **الهدف الأول** |
| `plan_selected` | plan_id, duration, devices, price | الحاسبة → checkout |
| `calculator_interacted` | duration, devices | تفاعل التسعير |
| `checkout_started` / `payment_submitted` / `purchase` | value, currency, payment_method | **الهدف الثاني** (purchase = server-side من الـ webhook، ليس client — الحقيقة من Stripe) |
| `tutorial_viewed` / `tutorial_completed` | device | فعالية الأدلة |
| `ticket_created` | category, is_customer | حمل الدعم |
| `credentials_copied` | field | لحظة التفعيل الحقيقية |
| `renewal_clicked` / `renewal_completed` | days_before_expiry | |

### Funnels الثلاثة الحاكمة
1. **Trial:** landing → trial_started → step2 → step3 → trial_activated → (7d) purchase
2. **Direct purchase:** pricing_view → calculator_interacted → plan_selected → checkout_started → purchase
3. **Renewal:** expiry_email_clicked → renewal_clicked → renewal_completed

### قرارات تنفيذ
- **الأداة:** Plausible (خفيف <1KB، GDPR-friendly بلا cookie banner) للسلوك + **أحداث server-side** للإيراد (webhook → Stripe metadata). GA4 اختياري لاحقاً — يُحمّل consent-gated فقط.
- **GDPR (سوق سويدي = صرامة):** Plausible بلا consent مطلوب؛ أي أداة cookies تتطلب CMP. IP anonymization إلزامي. يُضاف بند لسياسة الخصوصية.
- **UTM discipline:** كل الإعلانات بـ utm موحدة؛ `source` تُلتقط في trial_started (موجودة أصلاً كحقل مقترح في Trial model — يُفعّل).

---

## ملخص تنفيذي — ما يجب إغلاقه قبل كتابة أول سطر كود

| # | خطورة | البند | وثيقة التصحيح |
|---|---|---|---|
| 1 | **P0** | مواصفة CSP + security headers كاملة | DATA_INTEGRATION §3 |
| 2 | **P0** | اعتماد مواصفة الـ Analytics أعلاه (أحداث + funnels + Plausible + server-side purchase) | وثيقة جديدة أو §7 هنا |
| 3 | P1 | fallbacks المتصفحات: View Transitions، backdrop-filter + مصفوفة دعم رسمية (تشمل Samsung Internet) | MOTION + RESPONSIVE |
| 4 | P1 | WCAG 2.2: OTP paste، focus-not-obscured، بديل الـ drag، ARIA الكاروسيلات | DESIGN_SYSTEM §7 |
| 5 | P1 | حسم اللغة: حذف ar/en وhreflang → sv-SE فقط (توحيد الوثائق مع قرار السويد) | ARCHITECTURE |
| 6 | P1 | safe-area insets + keyboard overlap للفورمات | RESPONSIVE_SPEC |
| 7 | P1 | مرفقات التذاكر: whitelist + re-encode + signed URLs؛ CSRF origin-check منصوص | DATA_INTEGRATION |
| 8 | P1 | خط العناوين: subset + preload (LCP)؛ scale البطاقة الشعبية بلا CLS | ARCHITECTURE §8 |
| 9 | P2 | فهرسة الفلاتر الانتقائية، sr-only للرسوم، بروتوكول قياس أداء بجهاز مرجعي، تصحيح "Ma zolde" | متفرقة |

**بروتوكول القبول قبل الإطلاق:** Lighthouse CI في الـ pipeline (فشل build تحت 95/100) · axe-core آلي + تدقيق يدوي بكيبورد وVoiceOver على القمع الكامل · اختبار حقيقي على iPhone SE وSamsung Internet وSafari 16.4 · penetration smoke على الرؤوس والـ rate limits · التحقق من وصول أحداث القمع الثلاثة كاملة قبل أول كرونة إعلانات.
