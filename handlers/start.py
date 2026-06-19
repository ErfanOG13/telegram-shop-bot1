"""
هندلر /start و منوی اصلی + بازگشت به منو
"""
from telegram import Update
from telegram.ext import ContextTypes

from keyboards import main_menu_keyboard
from db import get_session, User

WELCOME_TEXT = (
    "👋 سلام {name} عزیز!\n\n"
    "به پنل کاربری خوش آمدید.\n"
    "یکی از گزینه‌های زیر را انتخاب کنید:"
)


def _ensure_user(tg_user):
    session = get_session()
    try:
        user = session.get(User, tg_user.id)
        if user is None:
            user = User(
                id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
            )
            session.add(user)
            session.commit()
        else:
            if user.username != tg_user.username or user.first_name != tg_user.first_name:
                user.username = tg_user.username
                user.first_name = tg_user.first_name
                session.commit()
    finally:
        session.close()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    _ensure_user(tg_user)

    text = WELCOME_TEXT.format(name=tg_user.first_name or "کاربر")
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())


async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tg_user = update.effective_user
    text = WELCOME_TEXT.format(name=tg_user.first_name or "کاربر")
    await query.edit_message_text(text, reply_markup=main_menu_keyboard())
