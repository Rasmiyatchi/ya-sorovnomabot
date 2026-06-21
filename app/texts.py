"""Barcha foydalanuvchi/admin UI matnlari (o'zbekcha, lotin)."""
from __future__ import annotations

# ── Umumiy ─────────────────────────────────────────────────────────────
BACK = "⬅️ Orqaga"
CANCEL = "❌ Bekor qilish"
CANCELLED = "Bekor qilindi."
UNKNOWN = "Noma'lum buyruq. /start ni bosing."
NO_ACCESS = "⛔ Sizda bunday huquq yo'q."

# ── /start & foydalanuvchi ─────────────────────────────────────────────
DEFAULT_POLL_NAME = "So'rovnoma"
DEFAULT_DESCRIPTION = "Quyidagi nomzodlardan biriga ovoz bering 👇"
NO_CANDIDATES = "Hozircha nomzodlar qo'shilmagan. Tez orada qaytib keling."
TOP_BUTTON = "🏆 TOP reyting"

# ── Ovoz berish ────────────────────────────────────────────────────────
CONFIRM_VOTE = "Siz rostdan ham ushbu nomzodga ovoz bermoqchimisiz?\n\n👤 <b>{name}</b>"
BTN_CONFIRM = "✅ Ovoz berishni tasdiqlash"
ALREADY_VOTED = "Siz allaqachon ovoz bergansiz!"
POLL_CLOSED = "So'rovnoma yakunlandi."
VOTE_ACCEPTED = "✅ Ovozingiz qabul qilindi. Rahmat!"
CANDIDATE_NOT_FOUND = "Bu nomzod topilmadi."

# ── Captcha ────────────────────────────────────────────────────────────
ENTER_CAPTCHA = "Tasdiqlash uchun rasmda ko'rsatilgan kodni kiriting:"
WRONG_CAPTCHA = "❌ Kod noto'g'ri. Qaytadan kiriting ({left} ta urinish qoldi):"
CAPTCHA_EXPIRED = "⏱ Kod muddati tugadi. Iltimos, qaytadan ovoz bering."
TOO_MANY_ATTEMPTS = "❌ Urinishlar tugadi. Iltimos, qaytadan ovoz bering."
SEND_TEXT_ONLY = "Iltimos, faqat rasmda ko'rsatilgan kodni matn ko'rinishida yuboring."

# ── Majburiy obuna ─────────────────────────────────────────────────────
MUST_SUBSCRIBE = (
    "Ovoz berish uchun avval quyidagi kanal(lar)ga a'zo bo'ling, "
    "so'ngra «Obuna bo'ldim» tugmasini bosing 👇"
)
SUB_OK = "✅ Rahmat! Endi ovoz berishingiz mumkin."
SUB_BTN_JOINED = "✅ Obuna bo'ldim"
SUB_BTN_CHANNEL = "{i}-kanalga a'zo bo'lish"

# ── TOP reyting ────────────────────────────────────────────────────────
TOP_TITLE = "🏆 <b>TOP reyting</b>\n\n"
TOP_ROW = "{rank}. {name} — <b>{votes}</b> ovoz\n"
TOP_TOTAL = "\nJami ovozlar: <b>{total}</b>"
TOP_EMPTY = "Hozircha ovozlar yo'q."

# ── Admin panel ────────────────────────────────────────────────────────
ADMIN_MENU = "🛠 <b>Admin panel</b>\nKerakli bo'limni tanlang:"
ADM_ADD_CANDIDATE = "➕ Nomzod qo'shish"
ADM_DEL_CANDIDATE = "➖ Nomzod o'chirish"
ADM_RESULTS = "📊 Natijalar"
ADM_EXPORT = "📥 Excel eksport"
ADM_STATS = "📈 Statistika grafiklari"
ADM_CHANNELS = "📢 Majburiy kanallar"
ADM_BROADCAST = "✉️ Xabar yuborish"
ADM_SETTINGS = "⚙️ Sozlamalar"
ROOT_PANEL_BTN = "🔐 ROOT panel"

# Nomzod qo'shish/o'chirish
ASK_CANDIDATE_NAME = "Yangi nomzodning to'liq F.I.SH ini yuboring:"
CANDIDATE_ADDED = "✅ Nomzod qo'shildi:\n👤 {name}"
DEL_PICK = "O'chirish uchun nomzodni tanlang:"
DEL_EMPTY = "O'chiriladigan nomzod yo'q."
CANDIDATE_DELETED = "🗑 Nomzod o'chirildi: {name}"

# Natijalar
RESULTS_TITLE = "📊 <b>Natijalar</b>\n\n"
RESULTS_ROW = "{rank}. {name} — <b>{votes}</b>\n"
RESULTS_TOTAL = "\nJami ovozlar: <b>{total}</b>"
RESULTS_EMPTY = "Hali nomzodlar yoki ovozlar yo'q."

# Eksport / statistika
EXPORT_CAPTION = "📥 Natijalar (Excel)"
STATS_CAPTION = "📈 Statistika"
STATS_EMPTY = "Grafik uchun yetarli ma'lumot yo'q."

# Kanallar
CHANNELS_TITLE = "📢 <b>Majburiy kanallar</b>\n\n"
CHANNELS_EMPTY = "Hozircha majburiy kanallar yo'q."
CHANNELS_ROW = "{i}. {title} (<code>{chat_id}</code>)\n"
ADD_CHANNEL_HELP = (
    "Kanal qo'shish uchun:\n"
    "• kanaldan istalgan postni shu yerga <b>forward</b> qiling, yoki\n"
    "• kanal <code>@username</code> yoki <code>chat_id</code> sini yuboring.\n\n"
    "⚠️ Bot o'sha kanalda <b>admin</b> bo'lishi shart (aks holda a'zolikni tekshira olmaydi)."
)
CHANNEL_ADDED = "✅ Kanal qo'shildi: {title}"
CHANNEL_REMOVED = "🗑 Kanal o'chirildi."
CHANNEL_BAD = "❌ Kanalni aniqlay olmadim. Botni kanalga admin qilib, qaytadan urinib ko'ring."
CH_BTN_DEL = "🗑 {title}"

# Broadcast
BROADCAST_ASK = "Hammaga yubormoqchi bo'lgan xabaringizni yuboring (matn/rasm/video...):"
BROADCAST_CONFIRM = "Ushbu xabar <b>{n}</b> ta foydalanuvchiga yuborilsinmi?"
BROADCAST_YES = "✅ Ha, yuborish"
BROADCAST_START = "📤 Yuborilmoqda..."
BROADCAST_PROGRESS = "📤 Yuborildi: {sent}/{total}"
BROADCAST_DONE = (
    "✅ Yakunlandi.\n"
    "Yuborildi: {sent}\n"
    "Bloklagan: {blocked}\n"
    "Xato: {failed}"
)

# Sozlamalar
SETTINGS_TITLE = "⚙️ <b>Sozlamalar</b>\n\n{summary}\n\nO'zgartirish uchun tanlang:"
SET_NAME = "📝 So'rovnoma nomi"
SET_DESC = "🧾 Tavsif"
SET_BANNER = "🖼 Banner rasmi"
SET_DEADLINE = "⏰ Tugash vaqti"
ASK_NAME = "Yangi so'rovnoma nomini yuboring:"
ASK_DESC = "Yangi tavsif matnini yuboring:"
ASK_BANNER = "Yangi banner rasmini (photo) yuboring:"
ASK_DEADLINE = (
    "Tugash vaqtini <code>YYYY-MM-DD HH:MM</code> ko'rinishida yuboring "
    "(Asia/Tashkent).\nMisol: <code>2026-07-01 18:00</code>\n"
    "O'chirish uchun <code>-</code> yuboring."
)
SET_SAVED = "✅ Saqlandi."
BAD_DEADLINE = "❌ Format noto'g'ri. Misol: 2026-07-01 18:00"
DEADLINE_CLEARED = "✅ Tugash vaqti o'chirildi."

SUM_NAME = "Nomi: <b>{v}</b>"
SUM_DESC = "Tavsif: {v}"
SUM_BANNER = "Banner: {v}"
SUM_DEADLINE = "Tugash vaqti: <b>{v}</b>"
SUM_NONE = "—"
SUM_SET = "bor ✅"
SUM_UNSET = "yo'q"

# ── ROOT panel ─────────────────────────────────────────────────────────
ROOT_TITLE = "🔐 <b>ROOT panel</b>\nKerakli bo'limni tanlang:"
ROOT_DASHBOARD = "📊 Dashboard"
ROOT_ADMINS = "👮 Adminlar"
ROOT_USERS = "👥 Foydalanuvchilar"

DASHBOARD = (
    "📊 <b>Tizim holati</b>\n\n"
    "👥 Foydalanuvchilar: <b>{users}</b>\n"
    "✅ Ovoz berganlar: <b>{voted}</b>\n"
    "⛔ Bloklangan: <b>{blocked}</b>\n"
    "🗳 Jami ovozlar: <b>{votes}</b>\n"
    "👤 Nomzodlar: <b>{candidates}</b>\n"
    "📢 Kanallar: <b>{channels}</b>\n"
    "👮 Adminlar: <b>{admins}</b>\n"
    "⏰ Tugash vaqti: <b>{deadline}</b>\n"
    "📌 Holat: <b>{status}</b>"
)
POLL_OPEN = "ochiq"
POLL_DONE = "yakunlangan"

ROOT_ADMINS_TITLE = "👮 <b>Adminlar</b>\n\n"
ROOT_ADMINS_EMPTY = "Oddiy adminlar yo'q."
ROOT_ADMIN_ROW = "{i}. <code>{tg_id}</code>\n"
ROOT_ADD_ADMIN = "➕ Admin qo'shish"
ROOT_ASK_ADMIN_ID = "Yangi adminning Telegram ID sini yuboring:"
ROOT_ADMIN_ADDED = "✅ Admin qo'shildi: <code>{tg_id}</code>"
ROOT_ADMIN_REMOVED = "🗑 Admin o'chirildi: <code>{tg_id}</code>"
ROOT_BAD_ID = "❌ Noto'g'ri ID. Raqam yuboring."
ROOT_ADMIN_EXISTS = "Bu foydalanuvchi allaqachon admin."
ADM_BTN_DEL = "🗑 {tg_id}"

ROOT_ASK_USER = "Foydalanuvchini ID yoki @username bo'yicha yuboring:"
ROOT_USER_NOT_FOUND = "Foydalanuvchi topilmadi."
ROOT_USER_CARD = (
    "👤 <b>Foydalanuvchi</b>\n\n"
    "ID: <code>{tg_id}</code>\n"
    "Username: {username}\n"
    "Ism: {first_name}\n"
    "Ovoz holati: <b>{vote_status}</b>\n"
    "Ovoz bergan nomzod: {voted_for}\n"
    "Bloklangan: <b>{blocked}</b>\n"
    "Faol: <b>{active}</b>\n"
    "Sana: {date}"
)
ROOT_USER_RESET = "♻️ Ovozni reset qilish"
ROOT_USER_BLOCK = "⛔ Bloklash"
ROOT_USER_UNBLOCK = "✅ Blokdan chiqarish"
ROOT_VOTE_RESET_OK = "♻️ Foydalanuvchi ovozi reset qilindi."
ROOT_VOTE_RESET_NONE = "Bu foydalanuvchi hali ovoz bermagan."
ROOT_USER_BLOCKED = "⛔ Bloklandi."
ROOT_USER_UNBLOCKED = "✅ Blokdan chiqarildi."
YES = "Ha"
NO = "Yo'q"
