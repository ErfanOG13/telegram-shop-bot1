"""
تنظیمات اصلی ربات.
همه‌ی مقادیر حساس از Environment Variables خوانده می‌شوند.
برای تست لوکال می‌توانید یک فایل .env بسازید (نمونه در .env.example).
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default=None):
    val = os.getenv(name)
    if val is None or val.strip() == "":
        return default
    try:
        return int(val)
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# توکن و آدرس‌های اصلی
# ---------------------------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

# آیدی عددی گروه ادمین که رسیدها برای تایید/رد در آن ارسال می‌شود.
# باید با عدد منفی (مثلا -1001234567890) باشد.
ADMIN_GROUP_ID = _get_int("ADMIN_GROUP_ID", None)

# یوزرنیم تلگرام پشتیبانی (بدون @) که دکمه‌ی پشتیبانی به آن لینک می‌شود.
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "ge3369")

# آدرس عمومی سرویس روی Render، برای ست کردن وبهوک. مثال:
# https://my-shop-bot.onrender.com
# Render به صورت خودکار RENDER_EXTERNAL_URL را برای هر Web Service ست می‌کند،
# پس معمولاً نیازی به ست کردن دستی WEBHOOK_BASE_URL نیست.
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL") or os.getenv("RENDER_EXTERNAL_URL", "")
# مسیر دلخواه برای وبهوک (یک رشته‌ی تصادفی برای امنیت بیشتر بهتر است)
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "telegram-webhook")
PORT = _get_int("PORT", 10000)

# اتصال دیتابیس (Render به صورت خودکار DATABASE_URL را برای Postgres می‌دهد)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local_test.db")
# Render مقدار را با postgres:// می‌دهد ولی SQLAlchemy نسخه‌ی جدید postgresql:// می‌خواهد
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# کلید رایگان BrsApi.ir برای نرخ دلار/طلا (در https://brsapi.ir ثبت‌نام و دریافت شود)
BRSAPI_KEY = os.getenv("BRSAPI_KEY", "")

# ---------------------------------------------------------------------------
# آدرس‌های ولت دریافت پرداخت
# ---------------------------------------------------------------------------
WALLETS = {
    "USDT": {
        "label": "USDT (ERC20)",
        "address": os.getenv("WALLET_USDT", "0x7207f38f8c95a7f93d6f497ed4b8a2dea98f491c"),
    },
    "TRX": {
        "label": "TRX (Tron)",
        "address": os.getenv("WALLET_TRX", "TEFGTFdsjgerqTPHQWpzfjnTJwamDqo94L"),
    },
    "TON": {
        "label": "TON",
        "address": os.getenv("WALLET_TON", "UQDOrl7d_EzSUsBtSXUVildMJWcTjpLu0h41fcKYPTGrsBiJ"),
    },
}

# ---------------------------------------------------------------------------
# پلن‌های اشتراک (مشترک بین هر سه محصول - در صورت نیاز جدا قابل تعریف است)
# ---------------------------------------------------------------------------
PLANS = {
    "1m": {"label": "۱ ماهه", "months": 1, "price_usd": 19},
    "6m": {"label": "۶ ماهه", "months": 6, "price_usd": 49},
    "12m": {"label": "۱ ساله", "months": 12, "price_usd": 89},
}

# ---------------------------------------------------------------------------
# محصولات (هر کدام یک کانال پرایوت تلگرامی)
# ---------------------------------------------------------------------------
PRODUCTS = {
    "product_1": {
        "name": "محصول ۱",
        "description": (
            "📦 *محصول ۱*\n\n"
            "توضیحات کامل محصول اینجا قرار می‌گیرد.\n"
            "این یک کانال پرایوت تلگرامی اشتراکی است که پس از پرداخت و تایید، "
            "لینک عضویت یک‌بارمصرف برای شما ارسال می‌شود."
        ),
        # آیدی عددی کانال پرایوت (باید با -100 شروع شود). ربات باید ادمین کانال باشد
        # و دسترسی «Invite Users via Link» داشته باشد.
        "channel_id": _get_int("CHANNEL_1_ID", -1003988509395),
    },
    "product_2": {
        "name": "محصول ۲",
        "description": (
            "📦 *محصول ۲*\n\n"
            "توضیحات کامل محصول اینجا قرار می‌گیرد.\n"
            "این یک کانال پرایوت تلگرامی اشتراکی است که پس از پرداخت و تایید، "
            "لینک عضویت یک‌بارمصرف برای شما ارسال می‌شود."
        ),
        "channel_id": _get_int("CHANNEL_2_ID", -1003988509395),
    },
    "product_3": {
        "name": "محصول ۳",
        "description": (
            "📦 *محصول ۳*\n\n"
            "توضیحات کامل محصول اینجا قرار می‌گیرد.\n"
            "این یک کانال پرایوت تلگرامی اشتراکی است که پس از پرداخت و تایید، "
            "لینک عضویت یک‌بارمصرف برای شما ارسال می‌شود."
        ),
        "channel_id": _get_int("CHANNEL_3_ID", -1003988509395),
    },
}

# پیام رد رسید
RECEIPT_REJECTED_MESSAGE = "❌ رسید شما تایید نشد، با پشتیبانی تماس بگیرید."
