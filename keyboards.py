"""
کیبوردهای شیشه‌ای (Inline Keyboard) استفاده شده در ربات.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import PRODUCTS, PLANS, SUPPORT_USERNAME


def main_menu_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for key, product in PRODUCTS.items():
        rows.append([InlineKeyboardButton(f"📦 {product['name']}", callback_data=f"product:{key}")])

    rows.append([InlineKeyboardButton("💱 نرخ ارز", callback_data="exchange_rate")])
    rows.append([InlineKeyboardButton("🆘 پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")])
    return InlineKeyboardMarkup(rows)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu")]]
    )


def product_description_keyboard(product_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ انتخاب اشتراک", callback_data=f"choose_plan:{product_key}")],
            [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu")],
        ]
    )


def plans_keyboard(product_key: str) -> InlineKeyboardMarkup:
    rows = []
    for plan_key, plan in PLANS.items():
        text = f"{plan['label']} — {plan['price_usd']}$"
        rows.append(
            [InlineKeyboardButton(text, callback_data=f"plan:{product_key}:{plan_key}")]
        )
    rows.append([InlineKeyboardButton("🔙 بازگشت", callback_data=f"product:{product_key}")])
    return InlineKeyboardMarkup(rows)


def payment_keyboard(product_key: str, plan_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🧾 ارسال رسید", callback_data=f"send_receipt:{product_key}:{plan_key}")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data=f"choose_plan:{product_key}")],
        ]
    )


def admin_review_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ تایید", callback_data=f"admin_approve:{order_id}"),
                InlineKeyboardButton("❌ رد", callback_data=f"admin_reject:{order_id}"),
            ]
        ]
    )
