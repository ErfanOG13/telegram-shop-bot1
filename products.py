"""
هندلرهای مربوط به:
- نمایش توضیحات محصول
- انتخاب پلن اشتراک (۱/۶/۱۲ ماهه)
- نمایش صفحه‌ی پرداخت (قیمت + آدرس ولت‌ها)
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import PRODUCTS, PLANS, WALLETS
from keyboards import (
    product_description_keyboard,
    plans_keyboard,
    payment_keyboard,
    back_to_menu_keyboard,
)


async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_key = query.data.split(":")[1]
    product = PRODUCTS.get(product_key)
    if not product:
        await query.edit_message_text("محصول یافت نشد.", reply_markup=back_to_menu_keyboard())
        return

    await query.edit_message_text(
        product["description"],
        reply_markup=product_description_keyboard(product_key),
        parse_mode=ParseMode.MARKDOWN,
    )


async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_key = query.data.split(":")[1]
    product = PRODUCTS.get(product_key)
    if not product:
        await query.edit_message_text("محصول یافت نشد.", reply_markup=back_to_menu_keyboard())
        return

    text = f"📦 *{product['name']}*\n\nلطفاً مدت اشتراک مورد نظر خود را انتخاب کنید:"
    await query.edit_message_text(
        text, reply_markup=plans_keyboard(product_key), parse_mode=ParseMode.MARKDOWN
    )


async def show_payment_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, product_key, plan_key = query.data.split(":")
    product = PRODUCTS.get(product_key)
    plan = PLANS.get(plan_key)
    if not product or not plan:
        await query.edit_message_text("اطلاعات نامعتبر است.", reply_markup=back_to_menu_keyboard())
        return

    wallet_lines = []
    for w in WALLETS.values():
        wallet_lines.append(f"*{w['label']}*:\n`{w['address']}`")
    wallets_text = "\n\n".join(wallet_lines)

    text = (
        f"📦 *{product['name']}*\n"
        f"⏳ مدت اشتراک: {plan['label']}\n"
        f"💰 قیمت: *{plan['price_usd']}$*\n\n"
        f"لطفاً مبلغ فوق را به یکی از آدرس‌های زیر واریز کنید:\n\n"
        f"{wallets_text}\n\n"
        f"بعد از واریز، روی دکمه‌ی «ارسال رسید» بزنید."
    )

    await query.edit_message_text(
        text,
        reply_markup=payment_keyboard(product_key, plan_key),
        parse_mode=ParseMode.MARKDOWN,
    )
