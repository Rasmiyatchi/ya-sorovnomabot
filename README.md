# InnoBot — Telegram so'rovnoma va ovoz berish boti

Ochiq ovoz berish tizimi (Python + Aiogram 3). Foydalanuvchilar nomzodlarga **1 marta**
ovoz beradi, natijalar real vaqtda ko'rinadi, adminlar so'rovnomani boshqaradi.

## Asosiy funksiyalar
- `/start` → banner + so'rovnoma nomi + tavsif + nomzod tugmalari (`{ovoz} {F.I.SH}`)
- Ovoz berish: tasdiq → **rasm captcha** → ovoz qabul qilinadi
- **Majburiy obuna** tekshiruvi (kanal(lar)ga a'zo bo'lmasa ovoz berolmaydi)
- **Bitta foydalanuvchi — bitta ovoz** (DB darajasida, parallellikka chidamli)
- `/top` — ommaviy reyting
- Admin panel (`/admin`): nomzod qo'shish/o'chirish, natijalar, **Excel eksport**,
  **statistika grafiklari**, majburiy kanallar, **broadcast**, sozlamalar (nom, tavsif,
  banner, tugash vaqti)
- **Yashirin ROOT** super-admin: adminlarni boshqaradi, har bir foydalanuvchini ko'radi
  va cheklangan tahrir qiladi (ovozni reset, bloklash) — boshqa adminlarga **ko'rinmaydi**

## Sozlash va ishga tushirish (lokal)
```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env             # token va ID'larni tekshiring (.env allaqachon to'ldirilgan)
.venv/bin/python bot.py          # long polling; DB va seed avtomatik yaratiladi
```

> Eslatma: `python bot.py` ishlamasligi mumkin, agar `~/.zshrc` da `alias python=...`
> bo'lsa (u venv'ni chetlab o'tadi). Shuning uchun yuqorida `.venv/bin/python` ishlatilgan.

## .env
| Kalit | Izoh |
|---|---|
| `BOT_TOKEN` | @BotFather tokeni (maxfiy, commit qilinmaydi) |
| `ADMIN_IDS` | oddiy adminlar (vergul bilan). ROOT'ni bu yerga **qo'shmang** |
| `ROOT_ID` | yashirin root (bitta ID) |
| `DATABASE_URL` | standart: `sqlite+aiosqlite:///data/innobot.db` |
| `CAPTCHA_LENGTH` / `CAPTCHA_TTL` / `CAPTCHA_MAX_ATTEMPTS` | captcha sozlamalari |
| `THROTTLE_RATE` | spam himoyasi (soniya) |
| `TIMEZONE` | deadline uchun (`Asia/Tashkent`) |

## Eslatmalar
- **Majburiy kanal** tekshiruvi ishlashi uchun bot o'sha kanalda **admin** bo'lishi shart.
- Tugash vaqti `Asia/Tashkent` da kiritiladi, DB'da UTC saqlanadi.
- Faqat **ROOT** Excel eksportida kim-kimga ovoz berganini ko'radi; oddiy admin faqat
  yig'ma natijani oladi.
- ⚠️ `BOT_TOKEN` maxfiy. Agar oshkor bo'lgan bo'lsa, @BotFather'da `/revoke` qiling.

## Loyiha tuzilmasi
```
bot.py                 # entrypoint (Dispatcher, middleware, polling, seed)
app/config.py          # .env sozlamalari
app/db/                # base (engine+PRAGMA), models, repositories
app/services/          # captcha, subscription, broadcast, export, charts, deadline, seed
app/middlewares/       # db sessiya, throttling
app/filters/           # IsAdmin, IsRoot
app/keyboards/         # user / admin / root tugmalari
app/states/            # FSM holatlari
app/handlers/user/     # start, vote (captcha), top
app/handlers/admin/    # menu, candidates, results, export, stats, channels, broadcast, settings
app/handlers/admin/root.py  # ROOT-only (yashirin)
```
