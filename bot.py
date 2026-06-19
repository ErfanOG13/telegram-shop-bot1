"""
فایل اصلی اجرای ربات.

روش اجرا: Webhook (نه Polling) چون روی Render Free Tier به صورت Web Service
دیپلوی می‌شود. python-telegram-bot از نسخه‌ی 20 به بعد یک وب‌سرور aiohttp
داخلی دارد که مستقیماً webhook را مدیریت می‌کند (نیازی به Flask جدا نیست).
"""
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN, WEBHOOK_BASE_URL, WEBHOOK_PATH, PORT
from db import init_db

from handlers.start import start_command, back_to_menu_callback
from handlers.products import show_product, show_plans, show_payment_page
from handlers.receipt import ask_for_receipt, receive_receipt_photo
from handlers.admin_actions import admin_approve, admin_reject
from handlers.exchange_rate import show_exchange_rate

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_application() -> Application:
    application = Application.builder().token(BOT_TOKEN).build()

    # دستورات
    application.add_handler(CommandHandler("start", start_command))

    # منو / ناوبری
    application.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern=r"^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(show_exchange_rate, pattern=r"^exchange_rate$"))

    # محصول -> پلن‌ها -> صفحه پرداخت
    application.add_handler(CallbackQueryHandler(show_product, pattern=r"^product:"))
    application.add_handler(CallbackQueryHandler(show_plans, pattern=r"^choose_plan:"))
    application.add_handler(CallbackQueryHandler(show_payment_page, pattern=r"^plan:"))

    # ارسال رسید
    application.add_handler(CallbackQueryHandler(ask_for_receipt, pattern=r"^send_receipt:"))
    application.add_handler(MessageHandler(filters.PHOTO, receive_receipt_photo))

    # اقدامات ادمین
    application.add_handler(CallbackQueryHandler(admin_approve, pattern=r"^admin_approve:"))
    application.add_handler(CallbackQueryHandler(admin_reject, pattern=r"^admin_reject:"))

    return application


def main():
    init_db()
    application = build_application()

    if WEBHOOK_BASE_URL:
        webhook_url = f"{WEBHOOK_BASE_URL.rstrip('/')}/{WEBHOOK_PATH}"
        logger.info("راه‌اندازی با Webhook: %s", webhook_url)
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=WEBHOOK_PATH,
            webhook_url=webhook_url,
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        # حالت توسعه/تست لوکال - بدون نیاز به دامنه عمومی
        logger.info("WEBHOOK_BASE_URL تنظیم نشده - اجرا با Polling (فقط برای تست لوکال).")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
