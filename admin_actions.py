"""
وقتی ادمین در گروه روی دکمه‌ی «تایید» یا «رد» می‌زند:

- تایید: ساخت لینک دعوت یک‌بارمصرف (member_limit=1) برای کانال محصول و ارسال آن به کاربر
- رد: ارسال پیام رد به کاربر

نکات امنیتی:
- فقط اعضای همان گروه ادمین اجازه‌ی این عملیات را دارند (چون callback از همان چت می‌آید
  و در صورت نیاز می‌توان لیست سفید ادمین‌ها را هم چک کرد).
- هر سفارش فقط یک‌بار قابل تایید/رد است (وضعیت order.status چک می‌شود تا با کلیک
  تکراری دوبار پردازش نشود).
"""
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config import PRODUCTS, PLANS, RECEIPT_REJECTED_MESSAGE
from db import get_session, Order

logger = logging.getLogger(__name__)


async def _append_status_to_admin_message(query, suffix_plain: str):
    """افزودن وضعیت تایید/رد به کپشن پیام ادمین، بدون استفاده از مارک‌داون
    (تا کاراکترهای خاص داخل نام کاربری/کپشن باعث خطا نشوند)."""
    try:
        current = query.message.caption or ""
        await query.edit_message_caption(caption=f"{current}\n\n{suffix_plain}")
    except TelegramError:
        logger.exception("خطا در ادیت کپشن پیام ادمین")


async def _user_is_group_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """بررسی اینکه کلیک‌کننده، ادمین همان گروه است (لایه‌ی امنیتی اضافه)."""
    try:
        member = await context.bot.get_chat_member(
            chat_id=update.effective_chat.id, user_id=update.effective_user.id
        )
        return member.status in ("administrator", "creator")
    except TelegramError:
        logger.exception("خطا در بررسی ادمین بودن کاربر")
        return False


async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if not await _user_is_group_admin(update, context):
        await query.answer("فقط ادمین می‌تواند این کار را انجام دهد.", show_alert=True)
        return

    order_id = int(query.data.split(":")[1])

    session = get_session()
    try:
        order = session.query(Order).filter(Order.id == order_id).with_for_update().first()
        if order is None:
            await query.answer("سفارش یافت نشد.", show_alert=True)
            return

        if order.status != "pending_review":
            await query.answer("این سفارش قبلاً بررسی شده است.", show_alert=True)
            return
        plan = PLANS.get(order.plan_key)
        channel_id = product["channel_id"] if product else None

        invite_link = None
        if channel_id:
            try:
                link_obj = await context.bot.create_chat_invite_link(
                    chat_id=channel_id,
                    member_limit=1,
                    name=f"order-{order_id}",
                )
                invite_link = link_obj.invite_link
            except TelegramError:
                logger.exception("خطا در ساخت لینک دعوت")

        order.status = "approved"
        order.reviewed_by = update.effective_user.id
        order.reviewed_at = datetime.utcnow()
        session.commit()

        user_id = order.user_id

        if invite_link:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"✅ رسید شما تایید شد!\n\n"
                    f"📦 محصول: {product['name']}\n"
                    f"⏳ پلن: {plan['label']}\n\n"
                    f"لینک عضویت یک‌بارمصرف شما:\n{invite_link}\n\n"
                    f"⚠️ این لینک فقط یک‌بار قابل استفاده است."
                ),
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "✅ رسید شما تایید شد، اما در ساخت لینک عضویت خطایی رخ داد. "
                    "لطفاً با پشتیبانی تماس بگیرید."
                ),
            )

        await query.answer("تایید شد ✅")
        await _append_status_to_admin_message(query, "✅ تایید شد")

    finally:
        session.close()


async def admin_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if not await _user_is_group_admin(update, context):
        await query.answer("فقط ادمین می‌تواند این کار را انجام دهد.", show_alert=True)
        return

    order_id = int(query.data.split(":")[1])

    session = get_session()
    try:
        order = session.query(Order).filter(Order.id == order_id).with_for_update().first()
        if order is None:
            await query.answer("سفارش یافت نشد.", show_alert=True)
            return

        if order.status != "pending_review":
            await query.answer("این سفارش قبلاً بررسی شده است.", show_alert=True)
            return

        order.status = "rejected"
        order.reviewed_by = update.effective_user.id
        order.reviewed_at = datetime.utcnow()
        session.commit()

        user_id = order.user_id

        await context.bot.send_message(chat_id=user_id, text=RECEIPT_REJECTED_MESSAGE)

        await query.answer("رد شد ❌")
        await _append_status_to_admin_message(query, "❌ رد شد")
    finally:
        session.close()
