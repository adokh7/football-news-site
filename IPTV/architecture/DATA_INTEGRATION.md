# Data Integration Architecture — IPTV Premium Sverige
**المصادر الأربعة:** Xtream Codes Panel API (إدارة الخطوط) · سيرفر البث (حالة/أحمال) · Postgres (المشتركون) · بوابة الدفع (Stripe + Swish)

## 0. المبدأ المعماري الحاكم

```
[Browser] ──► [Next.js API / Route Handlers] ──► [Postgres = مصدر الحقيقة التجاري]
                      │                                   ▲
                      ├──► [Redis: cache + queues + rate-limit]
                      ├──► [Panel Adapter] ──► Xtream Codes API   (الحقيقة التقنية للخطوط)
                      ├──► [Stream Monitor] ──► سيرفر البث (status probes)
                      └──◄ [Webhooks: Stripe/Swish] (موقّعة، idempotent)
```
1. **المتصفح لا يكلّم Xtream API أبداً** — كل شيء عبر Adapter داخلي (الـ panel credentials لا تغادر السيرفر).
2. **Postgres هو الحقيقة التجارية** (من دفع، ما الباقة، متى تنتهي). **الـ Panel هو الحقيقة التقنية** (الخط شغال أم لا). مزامنة أحادية الاتجاه Postgres→Panel عبر queue، مع reconciliation job دوري يكشف الانحراف.
3. كل عملية كتابة على الـ Panel تمر بـ **outbox pattern**: تُسجل في Postgres أولاً ثم تُنفذ من worker — لا خط يُنشأ بلا أثر محاسبي.

---

## 1. نماذج البيانات (Schema)

يبني على prisma models السابقة في [ARCHITECTURE.md](../ARCHITECTURE.md) — الإضافات الخاصة بالتكامل:

```prisma
model PanelAccount {                 // خط Xtream — مرآة محلية لحالة الـ Panel
  id            String   @id @default(cuid())
  subscriptionId String? @unique
  trialId       String?  @unique
  panelUserId   Int                  // id في Xtream
  username      String   @unique
  passwordEnc   String               // AES-256-GCM، مفتاح في KMS/env
  serverId      String               // أي سيرفر بث (multi-server)
  maxConnections Int
  expDate       DateTime             // كما يراها الـ Panel
  status        PanelStatus          // ACTIVE | DISABLED | EXPIRED | BANNED
  lastSyncedAt  DateTime             // آخر reconciliation
  driftDetected Boolean @default(false)
  @@index([expDate, status])
}

model StreamServer {                 // سيرفرات البث للمراقبة والتوزيع
  id           String  @id
  name         String              // "EU-North-1 (Stockholm)"
  panelBaseUrl String
  apiKeyEnc    String
  region       String
  capacity     Int                 // max خطوط
  currentLoad  Int                 // من آخر probe
  healthy      Boolean @default(true)
  lastProbeAt  DateTime
}

model ProvisionJob {                 // outbox — كل عملية panel
  id          String   @id @default(cuid())
  type        JobType              // CREATE_LINE | EXTEND | DISABLE | RESET_PASS | DELETE
  payload     Json
  status      JobStatus            // PENDING | RUNNING | DONE | FAILED | DEAD
  attempts    Int      @default(0)
  lastError   String?
  idempotencyKey String @unique    // orderId أو trialId — يمنع الخط المزدوج
  runAfter    DateTime @default(now())
  createdAt   DateTime @default(now())
  @@index([status, runAfter])
}

model WebhookEvent {                 // سجل webhooks — idempotency + تدقيق
  id         String   @id           // event id من المزوّد (stripe evt_xxx)
  provider   String                 // stripe | swish
  type       String
  payload    Json
  processed  Boolean  @default(false)
  processedAt DateTime?
  @@index([provider, processed])
}

model SyncAudit {                    // نتائج الـ reconciliation
  id        String   @id @default(cuid())
  runAt     DateTime @default(now())
  checked   Int
  drifts    Json                    // [{panelAccountId, field, db, panel}]
  resolved  Boolean
}
```

**Zod DTOs مشتركة** (client/server) في `lib/validation/` — كل response من Xtream يمر بـ schema parsing (الـ Panel APIs ترجع أشكالاً غير موثوقة؛ لا نثق بها typewise أبداً).

---

## 2. نقاط الـ API

### Public (متصفح → Next.js)
| Method | Endpoint | الوظيفة | Auth | Cache |
|---|---|---|---|---|
| GET | `/api/plans` | الباقات | — | CDN 60s + SWR |
| GET | `/api/search` | VOD/قنوات + facets | — | CDN 300s (مفتاح = query normalized) |
| POST | `/api/trial` | إنشاء تجربة | rate-limit + fingerprint | — |
| GET | `/api/orders/:id/status` | حالة التفعيل (polling) | session أو order token | no-store |
| POST | `/api/checkout` | جلسة دفع | session | — |
| GET | `/api/account/subscription` | اشتراكي + بيانات الخط | session | private 30s |
| GET/POST/PATCH/DELETE | `/api/account/devices[/:id]` | CRUD أجهزة | session | — |
| POST | `/api/account/credentials/regenerate` | كلمة سر Xtream جديدة | session + re-auth (password/OTP) | — |
| GET/POST | `/api/tickets[/:id]/messages` | تذاكر | session (أو email token للزوار) | — |
| PUT | `/api/account/renewal` | تفعيل/إيقاف التجديد التلقائي | session | — |

### Webhooks (بوابة الدفع → نحن)
| POST | `/api/webhooks/stripe` — تحقق توقيع `stripe-signature`، تسجيل في WebhookEvent، ثم ProvisionJob |
| POST | `/api/webhooks/swish` — callback موقّع، نفس المسار |
- **Idempotent إلزاماً:** `WebhookEvent.id` unique — الحدث المكرر يُتجاهل بصمت مع 200.

### Internal (worker → Panel Adapter — لا يُكشف خارجياً)
| العملية | Xtream call المقابل |
|---|---|
| `panel.createLine(user, plan, serverId)` | `POST player_api.php` create user (أو Panel admin API) |
| `panel.extendLine(id, months)` | update exp_date |
| `panel.disableLine(id)` / `enableLine` | status toggle |
| `panel.resetPassword(id)` | password update |
| `panel.getLineInfo(id)` | `player_api.php?action=user_info` |
| `panel.getServerHealth()` | server_info + connection counts |

### Admin (`/api/admin/*` — role=ADMIN)
CRUD كامل للـ plans (هذا ما يجعل الأسعار "ديناميكية")، عرض ProvisionJobs الفاشلة + إعادة تشغيل، تقارير drift، إدارة StreamServers.

---

## 3. استراتيجية التوثيق

| السياق | الآلية | لماذا |
|---|---|---|
| المستخدمون (متصفح) | **Session cookies (httpOnly, Secure, SameSite=Lax)** عبر Auth.js — ليست JWT في localStorage | XSS لا يسرق الجلسة؛ revocation فوري |
| API داخلي بين services/workers | JWT قصير العمر (5 min) موقّع HS256 بمفتاح داخلي، claim `svc` | stateless بين الـ worker والـ API |
| Xtream Panel | **API key/admin creds في env/KMS فقط** — server-side حصراً، تدوير ربع سنوي | الـ Panel لا يدعم OAuth؛ العزل هو الحماية |
| Webhooks واردة | تحقق توقيع (Stripe HMAC / Swish cert) + timestamp tolerance 5 min | منع replay |
| عمليات حساسة (regenerate password، تغيير بريد) | **step-up re-auth**: OTP أو كلمة المرور مجدداً حتى بجلسة نشطة | جلسة مسروقة ≠ سيطرة كاملة |
| Admin | نفس session + role check في middleware + 2FA (TOTP) | |
| Rate limiting | Upstash Redis sliding window: trial 3/IP/يوم، login 5/15min، search 60/min | |

**لا OAuth للمستخدمين في v1** (Google Sign-in لاحقاً كإضافة، ليس بديلاً).

---

## 4. الوقت الحقيقي

| الحاجة | الآلية | التبرير |
|---|---|---|
| حالة التفعيل بعد الدفع | **Polling 2s** (React Query refetchInterval) لمدة ≤45s | حدث واحد قصير العمر — WebSocket إسراف |
| محادثة التذاكر | **SSE** (`/api/tickets/:id/stream`) + fallback polling 10s | أحادي الاتجاه (السيرفر يدفع الردود)، يمر من الـ proxies بلا مشاكل WS |
| إشعار الفريق بتذكرة عاجلة | Telegram Bot push (server→server) | |
| حالة السيرفرات في الـ status page | Polling 30s على snapshot مُجهز في Redis (الـ probe الفعلي كل 60s cron) | المستخدمون لا يضربون سيرفر البث مباشرة أبداً |
| انتهاء الاشتراك live في الداشبورد | Polling 60s على subscription فقط | |
| **قرار صريح:** لا WebSockets في v1 | SSE + polling يغطيان كل الحالات بلا stateful infra | يوم نبني admin dashboard حي أو مشاهدة تزامنية، نعيد التقييم |

---

## 5. استراتيجية الكاش (طبقات من الخارج للداخل)

| طبقة | ماذا | TTL / invalidation |
|---|---|---|
| **CDN / Vercel Edge** | صفحات التسويق (ISR)، `/api/plans`، `/api/search`، صور البوسترات | ISR revalidate 300s؛ plans: `revalidateTag('plans')` عند تعديل admin — فوري |
| **Redis** | كتالوج VOD المعالج (من الـ Panel: get_vod_streams ~آلاف العناصر) | 15 min، مفتاح لكل فئة؛ **stale-while-revalidate**: قدّم القديم وجدّد بالخلفية |
| | server health snapshot | 60s (يكتبه الـ probe cron) |
| | نتائج search facets | 5 min |
| **React Query (memory)** | كل server state في المتصفح | staleTime حسب النوع: plans 60s، subscription 30s، search 5min |
| **localStorage** | ⚠️ **ممنوع فيه:** أي tokens أو بيانات M3U/Xtream (XSS surface) | — |
| | ✅ مسموح: تفضيلات UI (لغة، آخر فلاتر بحث، devices tab المختار)، scroll positions | لا انتهاء |
| **sessionStorage** | حالة الـ checkout wizard (step, planId — لا أسعار) | تُمسح بإغلاق التبويب |

**قاعدة:** بيانات الأسعار والصلاحية تُقرأ من cache للعرض، لكن **كل قرار (دفع، تفعيل) يقرأ Postgres مباشرة**.

---

## 6. معالجة الأخطاء

### Retries (حسب المصدر)
| مصدر | سياسة |
|---|---|
| Xtream Panel | exponential backoff: 1s → 4s → 15s → 60s → 5min، max 8 محاولات عبر ProvisionJob queue؛ بعدها status=DEAD + تنبيه Telegram + تذكرة تلقائية للعميل |
| Stripe API | retries مدمجة بالـ SDK + idempotency keys على كل create |
| Webhooks (نحن المستقبِل) | نرد 200 فوراً بعد التسجيل، المعالجة async — فشل المعالجة لا يخسر الحدث (موجود في WebhookEvent) |
| متصفح → API | React Query: retry 2 بـ backoff، الـ mutations لا تُعاد تلقائياً (تُعاد يدوياً بزر) |

### Circuit breaker (الـ Panel Adapter)
```
CLOSED ── 5 فشل متتالٍ خلال 60s ──► OPEN (كل الطلبات تفشل فوراً 30s)
OPEN ── مهلة ──► HALF_OPEN (طلب اختباري واحد) ── نجح → CLOSED / فشل → OPEN
```
أثناء OPEN: الـ trials تتحول لوضع "queued" برسالة صادقة ("aktiveras inom kort — vi mejlar dig")، والدفع **يستمر** (الخط يُنشأ حين يتعافى الـ Panel — outbox يضمن ذلك).

### Fallbacks
| فشل | fallback |
|---|---|
| Panel down وقت عرض بيانات الخط في الداشبورد | اعرض المرآة المحلية (PanelAccount) + شارة "senast uppdaterad för X min sedan" |
| كتالوج VOD غير متاح | Redis stale → وإلا snapshot ثابت من آخر build (المكتبة لا تعرض صفحة فارغة أبداً) |
| Stripe down | زر Swish يبقى؛ والعكس. مزوّدان = redundancy مدمج |
| سيرفر بث down (probe) | الخطوط الجديدة تُوزّع تلقائياً على السيرفر السليم التالي (`StreamServer.healthy`) |
| Search backend بطيء >2s | timeout → نتائج شائعة مسبقة التجهيز + رسالة |

### Offline (متصفح)
- **الموقع تسويق + إدارة، ليس تطبيق مشاهدة** — لا PWA offline كامل في v1.
- المطبق: `navigator.onLine` + مستمع → banner "Ingen anslutning" غير مقاطع؛ mutations تفشل فوراً برسالة واضحة (لا queue وهمي)؛ React Query يعيد الجلب تلقائياً عند `online` event؛ صفحة الاعتمادات (M3U) تعرض آخر نسخة من الـ query cache مع تنبيه — أهم حالة عملياً: مستخدم يضبط تلفازه والواي فاي متقلب.

### Reconciliation (شبكة الأمان الأخيرة)
Cron ليلي: يقارن كل `PanelAccount` نشط مع الـ Panel (`user_info`) — انحراف في exp_date أو status يُسجل في `SyncAudit`، يُصحح تلقائياً باتجاه Postgres (الحقيقة التجارية)، والحالات الغامضة تُعلَّم `driftDetected` لمراجعة بشرية. هذا يلتقط أي تعديل يدوي على الـ Panel أو webhook ضائع.
