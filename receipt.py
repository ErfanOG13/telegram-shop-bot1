"""
فرآیند ارسال رسید:
1. کاربر روی «ارسال رسید» می‌زند -> ربات می‌گوید «رسیدت رو بفرست» و در user_data منتظر عکس می‌ماند
2. کاربر عکس می‌فرستد -> یک Order در دیتابیس ساخته می‌شود (status=pending_review)
   و عکس + اطلاعات سفارش با دکمه‌های تایید/رد به گروه ادمین فوروارد می‌شود
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import PRODUCTS, PLANS, ADMIN_GROUP_ID
from keyboards import admin_review_keyboard, back_to_menu_keyboard
from db import get_session, Order, User

# کلیدهایی که در context.user_data استفاده می‌کنیم
WAITING_PRODUCT_KEY = "awaiting_receipt_product"
WAITING_PLAN_KEY = "awaiting_receipt_plan"


async def ask_for_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی کاربر دکمه‌ی «ارسال رسید» را می‌زند."""
    query = update.callback_query
    await query.answer()

    _, product_key, plan_key = query.data.split(":")
    if product_key not in PRODUCTS or plan_key not in PLANS:
        await query.edit_message_text("اطلاعات نامعتبر است.", reply_markup=back_to_menu_keyboard())
        return

    # ذخیره‌ی سفارش در حال انتظار برای این کاربر
    context.user_data[WAITING_PRODUCT_KEY] = product_key
    context.user_data[WAITING_PLAN_KEY] = plan_key

    await query.edit_message_text(
        "🧾 لطفاً اسکرین‌شات (عکس) رسید پرداخت خود را همینجا ارسال کنید."
    )


async def receive_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی کاربر عکس می‌فرستد - فقط در صورتی پردازش می‌شود که منتظر رسید باشیم."""
    product_key = context.user_data.get(WAITING_PRODUCT_KEY)
    plan_key = context.user_data.get(WAITING_PLAN_KEY)

    if not product_key or not plan_key:
        # کاربر بدون اینکه در فرآیند خرید باشد عکس فرستاده
        return

    if not update.message or not update.message.photo:
        return

    product = PRODUCTS[product_key]
    plan = PLANS[plan_key]
    tg_user = update.effective_user

    # بزرگترین سایز عکس را برمی‌داریم
    photo = update.message.photo[-1]

    session = get_session()
    try:
        # مطمئن می‌شویم کاربر در دیتابیس وجود دارد
        user = session.get(User, tg_user.id)
        if user is None:
            user = User(id=tg_user.id, username=tg_user.username, first_name=tg_user.first_name)
            session.add(user)
            session.commit()

        order = Order(
            user_id=tg_user.id,
            product_key=product_key,
            plan_key=plan_key,
            price_usd=plan["price_usd"],
            status="pending_review",
            receipt_file_id=photo.file_id,
        )
        session.add(order)
        session.commit()
        order_id = order.id
    finally:
        session.close()

    # پاک کردن وضعیت انتظار
    context.user_data.pop(WAITING_PRODUCT_KEY, None)
    context.user_data.pop(WAITING_PLAN_KEY, None)

    await update.message.reply_text(
        "✅ رسید شما برای بررسی ارسال شد. پس از تایید ادمین، لینک اشتراک برای شما ارسال می‌شود."
    )

    # ارسال به گروه ادمین
    if ADMIN_GROUP_ID:
        username_part = f"@{tg_user.username}" if tg_user.username else "(بدون یوزرنیم)"
        caption = (
            f"🧾 *رسید جدید*\n\n"
            f"👤 کاربر: {tg_user.first_name or ''} {username_part}\n"
            f"🆔 آیدی عددی: `{tg_user.id}`\n"
            f"📦 محصول: {product['name']}\n"
            f"⏳ پلن: {plan['label']}\n"
            f"💰 قیمت: {plan['price_usd']}$\n"
            f"🔢 شماره سفارش: #{order_id}"
        )
        sent = await context.bot.send_photo(
            chat_id=ADMIN_GROUP_ID,
            photo=photo.file_id,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=admin_review_keyboard(order_id),
        )

        # ذخیره‌ی آیدی پیام ادمین برای ادیت بعدی (تایید/رد)
        session = get_session()
        try:
            order = session.get(Order, order_id)
            order.admin_message_chat_id = sent.chat_id
            order.admin_message_id = sent.message_id
            session.commit()
        finally:
            session.close()
    else:
        # اگر آیدی گروه ادمین تنظیم نشده باشد
        await context.bot.send_message(
            chat_id=tg_user.id,
            text="⚠️ خطای داخلی: گروه ادمین تنظیم نشده است. لطفاً با پشتیبانی تماس بگیرید.",
        )
