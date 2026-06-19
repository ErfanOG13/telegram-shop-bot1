"""
هندلر نمایش نرخ ارز (دلار، طلا، ۱۰ ارز دیجیتال برتر)
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from keyboards import back_to_menu_keyboard
from services.exchange_rate import build_exchange_rate_text


async def show_exchange_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("⏳ در حال دریافت نرخ‌های لحظه‌ای...")

    text = await build_exchange_rate_text()

    await query.edit_message_text(
        text, reply_markup=back_to_menu_keyboard(), parse_mode=ParseMode.MARKDOWN
    )
