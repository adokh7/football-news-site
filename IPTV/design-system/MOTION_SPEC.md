# Motion Spec — Pricing Section & VOD/Live TV Library
**فلسفة:** فخامة = حسم وقلّة. الحركة تشرح البنية وتكافئ النية — لا تستعرض. عنصر واحد "بطل" في كل لحظة؛ كل ما عداه يدعمه بهدوء.
**مرجع الـ tokens:** [tokens.css](tokens.css) — يضيف هذا الملف tokens جديدة موسومة 🆕.

---

## 0. منحنيات وأزمنة النظام (المرجع الكامل)

### Easing curves
| Token | قيمة | متى |
|---|---|---|
| `--ease-standard` | `cubic-bezier(0.2, 0, 0, 1)` | الافتراضي — تحريك موضع/حجم، tabs، accordion |
| `--ease-enter` | `cubic-bezier(0, 0, 0.2, 1)` | عناصر تدخل الشاشة (decelerate) |
| `--ease-exit` | `cubic-bezier(0.4, 0, 1, 1)` | عناصر تغادر (accelerate — الخروج أسرع شعورياً) |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | تأكيدات صغيرة فقط: toggle knob، badge، checkmark |
| 🆕 `--spring-poster` | spring(stiffness 320, damping 28, mass 1) | hover البوسترات (Framer Motion) — حيّ بلا اهتزاز |
| 🆕 `--spring-modal` | spring(stiffness 260, damping 30) | فتح المودال/الـ detail view |

### Durations
| Token | ms | الاستخدام |
|---|---|---|
| `--dur-instant` | 100 | hover feedback، تغيّر لون |
| `--dur-fast` | 160 | toggles، chips، أيقونات |
| `--dur-base` | 240 | بطاقات، tabs، dropdowns، أغلب الانتقالات |
| `--dur-slow` | 400 | accordion، صفوف كبيرة، price count-up |
| `--dur-cinematic` | 700 | hero/backdrop فقط — مرة واحدة في الشاشة |
| 🆕 `--dur-page` | 320 | page transitions (View Transitions API) |

**قاعدة ذهبية:** الدخول بـ enter easing وبمدة أطول؛ الخروج بـ exit وبـ **70% من مدة الدخول**. لا حركة على layout properties — `transform` و`opacity` فقط (استثناء accordion: `grid-template-rows`).

---

## 1. قسم الباقات (Pricing)

### 1.1 تسلسل تحميل/دخول القسم (عند بلوغه بالسكرول، مرة واحدة)
```
t=0ms     العنوان "Ett pris. Allt du vill se."
          opacity 0→1, translateY 16→0 · 400ms · ease-enter
t=80ms    الـ BillingToggle · نفس الحركة · 300ms
t=160ms   PlanCard #1  ┐
t=220ms   PlanCard #2  ├ opacity 0→1, translateY 24→0, scale .97→1
t=280ms   PlanCard #3  ┘ 400ms · ease-enter (stagger 60ms)
t=520ms   شارة "Populärast" تنبثق: scale 0→1 · 240ms · ease-spring
          (تتأخر عمداً — آخر ما يظهر = أول ما يُلاحظ)
t=600ms   صف الثقة (💳🔒↩) opacity فقط · 240ms
```
- المجموع المحسوس: أقل من ثانية. **لا يُعاد** عند العودة بالسكرول (`once: true`).
- Trigger: `IntersectionObserver` عند 20% ظهور.

### 1.2 سلوكيات السكرول
- **لا parallax في الباقات.** الأسعار قرار مالي — أي حركة أثناء القراءة تقلل الثقة. الحركة الوحيدة: الدخول أعلاه.
- **جدول المقارنة:** الـ header يلتصق (sticky) — عند التصاقه يكتسب ظلاً سفلياً `--sh-sm` عبر transition 160ms (يوضح أنه طافٍ).
- **Mobile:** بطاقات الباقات = horizontal snap carousel (`scroll-snap-type: x mandatory`)، البطاقة الشعبية تبدأ في المنتصف، dots تحتها تتبدل بـ 160ms.

### 1.3 حالات الهوفر (desktop فقط — `@media (hover: hover)`)
| عنصر | الحركة | مدة/easing |
|---|---|---|
| PlanCard | `translateY(-4px)` + shadow `--sh-md → --sh-lg` + حدود ترتفع درجة | 240ms · standard |
| PlanCard (popular) | نفسه + glow ذهبي يشتد `opacity .35→.5` | 240ms |
| زر "Välj paket" | `translateY(-1px)` + `--sh-glow-gold` | 100ms · standard |
| زر (pressed) | `scale(.98)`، بلا glow | 100ms · exit |
| صف الجدول | خلفية `--bg-hover` | 100ms، خروج 160ms (الخروج الأبطأ يمنع الوميض بين الصفوف) |
| سعر البطاقة عند hover البطاقة | لا شيء. السعر لا يتحرك أبداً — ثقة | — |

### 1.4 تفاعل الحاسبة (click/change)
- **BillingToggle:** الـ knob ينزلق بـ 240ms · ease-spring (overshoot خفيف ~4px). النص المختار يثقل وزنه فوراً (لا transition على font-weight — snap مقصود).
- **تغيّر السعر:** count-up/down رقمي 400ms · ease-standard، بـ `tabular-nums` (لا اهتزاز عرض). تغيير جديد أثناء العد → قفزة فورية للقيمة الأخيرة ثم عدّ من هناك.
- **شارة "Spara 45 %":** عند اختيار 12 شهراً: `scale 0→1.08→1` بـ 240ms spring + وميض ذهبي واحد (`background flash` 400ms). عند مغادرة 12 شهراً: fade-out 160ms exit.
- **Device stepper:** الرقم يتبدل بـ slide-up 8px + fade، 160ms (القديم يخرج لأعلى إن زاد، لأسفل إن نقص — اتجاه = معنى).

### 1.5 انتقال الضغط → Checkout
- الضغط على "Välj paket": البطاقة المختارة `scale .98→1` (100ms)، الأخريان تخفتان `opacity .4` (160ms)، ثم **View Transition** للـ checkout: البطاقة تتحول (morph) إلى ملخص الطلب أعلى صفحة الدفع — `::view-transition` بـ 320ms · standard. المستخدم يرى اختياره "يسافر" معه = طمأنينة.

---

## 2. مكتبة VOD / Live TV

### 2.1 تسلسل التحميل
```
t=0ms     صف الفلاتر/التبويبات (Sport · Film · Serier · Live) — fade 240ms
t=60ms    الصف الأول من البوسترات: stagger 40ms لكل بوستر، بحد أقصى
          8 عناصر متحركة (الباقي يظهر فوراً) — opacity 0→1 + translateY 12→0
          300ms · ease-enter
t≥…       الصفوف تحت الطية: لا stagger — تظهر جاهزة (السرعة أهم من الاستعراض)
```
- **الصور نفسها:** blur-up (placeholder مموّه → حاد) عبر `filter: blur(12px)→0` + `scale 1.04→1`، 400ms عند اكتمال التحميل. هذا "الأنيميشن" الحقيقي للمكتبة.
- Skeletons بنفس أبعاد 2:3 — **صفر CLS**.

### 2.2 سلوكيات السكرول
| سلوك | مواصفة |
|---|---|
| **Hero backdrop parallax** (أعلى المكتبة) | الخلفية تتحرك بـ 30% من سرعة السكرول (`translateY(scrollY * 0.3)`) + scrim يشتد تدريجياً. العنصر الوحيد بـ parallax في الصفحة. GPU: `will-change: transform` |
| **صفوف الكاروسيل** | reveal بسيط عند الدخول (opacity 240ms) — لا rise لكل صف؛ التكرار يصير ضجيجاً |
| **شريط الفئات (pin)** | tabs الفئات تلتصق تحت الهيدر؛ عند الالتصاق: خلفية `rgba(11,11,15,.85)` + blur(16px)، transition 240ms |
| **Live TV — "الآن يُعرض"** | شريط progress رفيع أسفل بطاقة القناة يتقدم real-time (width عبر `transform: scaleX` — لا width animation) |
| **Infinite scroll** | الدفعة الجديدة تظهر بـ fade 240ms جماعي (بلا stagger) + spinner صغير يسبقها |

### 2.3 حالات الهوفر
| عنصر | الحركة | مدة/easing |
|---|---|---|
| **PosterCard** | الصورة `scale 1→1.05` داخل قصّ زوايا ثابت + scrim يصعد + العنوان/السنة يظهران `translateY 8→0` | scale: `--spring-poster` · scrim/نص: 240ms enter، **بتأخير 60ms** (اللمسة الآبلية: البطاقة تستجيب فوراً، المعلومة تلحق) |
| PosterCard (خروج) | كل شيء يرتد | 160ms · exit — الخروج أسرع دائماً |
| شارة 4K | لا تتحرك (ثابتة فوق كل الحالات) | — |
| **ChannelTile** (Live) | اللوقو grayscale 40%→0 + `scale 1.03` | 160ms · standard |
| ChannelTile (live الآن) | نقطة LIVE تنبض `opacity .5↔1` كل 2s — **العنصر الوحيد المسموح بحركة لانهائية** | 2s · ease-in-out |
| أسهم الكاروسيل | تظهر عند hover الصف كله: opacity + `translateX ∓4→0` | 160ms |
| زر "Titta nu" (داخل hover البوستر) | يدخل مع الـ scrim؛ hover عليه: glow ذهبي | 100ms |

### 2.4 انتقالات الضغط
- **فتح تفاصيل عنوان (modal/detail):**
  1. الضغط: البوستر `scale .97` — 100ms (إقرار فوري باللمس).
  2. **Shared-element transition:** البوستر يطير من موقعه في الشبكة إلى موقعه في المودال (View Transitions API / Framer `layoutId`) — 320ms · `--spring-modal`.
  3. الـ overlay `rgba(5,5,7,.7)` + blur(8px) يدخل بالتوازي — 240ms.
  4. محتوى المودال (عنوان، وصف، أزرار) stagger 40ms بعد استقرار البوستر.
  - إغلاق: عكس المسار بـ 240ms (70% قاعدة) — البوستر يعود لمكانه في الشبكة.
- **تبديل تبويب فئة (Sport→Film):** المؤشر الذهبي ينزلق 240ms standard؛ المحتوى القديم fade-out 120ms ثم الجديد fade-in 160ms مع translateY 8px (اتجاه الانزلاق = اتجاه التبويب).
- **Page transition (مكتبة → صفحة قناة):** View Transition 320ms — الـ hero backdrop يتقاطع (cross-fade) والبقية fade عادي.

### 2.5 دعم الإيماءات (touch)
| إيماءة | سلوك | مواصفة |
|---|---|---|
| **Swipe أفقي** على الكاروسيلات | native scroll + `scroll-snap-align: start`، momentum النظام | لا JS hijacking — أداء iOS مثالي |
| **Swipe لأسفل** على المودال المفتوح | يتبع الإصبع 1:1؛ إفلات > 120px أو velocity > 0.5 → إغلاق (240ms exit)، وإلا يرتد (spring) | overlay opacity يتناسب مع مسافة السحب |
| **Pull-to-refresh** (مكتبة Live) | مسافة السحب بمقاومة `d^0.8`، مؤشر دائري يمتلئ؛ عتبة 72px → refresh + haptic خفيف (حيث يتوفر) | الارتداد spring(300, 26) |
| **Pinch على البوستر** (تكبير معاينة) | scale يتبع الإصبعين حتى 1.6 كحد؛ الإفلات يرجع spring — لمسة إمتاع لا وظيفة | اختياري v2 |
| **Long-press على بوستر** | context sheet من الأسفل (شاهد لاحقاً/معلومات) — slide-up 240ms enter + haptic | يلغي الـ hover غير المتاح على touch |
| **Tap على touch** (بديل hover) | tap أول = كشف الـ scrim والعنوان؛ tap ثانٍ = فتح | نمط iOS القياسي |

---

## 3. قواعد عرضية (تلزم القسمين)
1. **`prefers-reduced-motion`:** كل ما سبق يتحول لـ opacity فقط 0.01ms (مطبّق globally). الـ parallax يثبت، count-up يقفز للقيمة، المودال يظهر بلا طيران.
2. **ميزانية التزامن:** لا أكثر من **8 عناصر** تتحرك في اللحظة نفسها؛ stagger يتوقف بعد العنصر 8.
3. **الأداء:** `transform/opacity` فقط + `will-change` يُضاف قبل الحركة ويُزال بعدها (لا يُترك دائماً). هدف ثابت: 60fps، قياس بـ DevTools Performance على جهاز متوسط.
4. **TV breakpoint (≥1920):** لا hover — استبداله بـ **focus scale 1.06 + حلقة ذهبية 3px** بـ 160ms (تنقّل ريموت)؛ الانتقال بين العناصر snap لا smooth.
5. **الاختبار الحسّي:** أي حركة تلاحظها في الزيارة الخامسة يجب أن تكون وظيفية — وإلا تُحذف.

---

## ملحق: Framer Motion presets جاهزة
```ts
export const springs = {
  poster: { type: "spring", stiffness: 320, damping: 28, mass: 1 },
  modal:  { type: "spring", stiffness: 260, damping: 30 },
  badge:  { type: "spring", stiffness: 400, damping: 22 },   // overshoot واضح
};
export const enter   = { duration: 0.4,  ease: [0, 0, 0.2, 1] };
export const exit    = { duration: 0.16, ease: [0.4, 0, 1, 1] };
export const standard= { duration: 0.24, ease: [0.2, 0, 0, 1] };

export const staggerGrid = {           // شبكة البوسترات
  animate: { transition: { staggerChildren: 0.04, delayChildren: 0.06 } },
};
export const cardReveal = {
  initial: { opacity: 0, y: 24, scale: 0.97 },
  animate: { opacity: 1, y: 0, scale: 1, transition: enter },
};
```
