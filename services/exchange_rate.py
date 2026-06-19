"""
دریافت نرخ ارز:
- دلار و طلا از BrsApi.ir
- ۱۰ ارز دیجیتال برتر از CoinGecko
"""
import aiohttp
import logging

from config import BRSAPI_KEY

logger = logging.getLogger(__name__)

BRSAPI_URL = "https://brsapi.ir/Api/Market/Gold_Currency.php"
COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
)


async def fetch_usd_gold():
    if not BRSAPI_KEY:
        return None
    url = f"{BRSAPI_URL}?key={BRSAPI_KEY}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data
    except Exception:
        logger.exception("خطا در دریافت نرخ از BrsApi")
        return None


async def fetch_top_cryptos():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(COINGECKO_URL, timeout=10) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()
    except Exception:
        logger.exception("خطا در دریافت نرخ از CoinGecko")
        return None


def _find_in_brsapi(data, keys):
    if not data:
        return None
    pools = []
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                pools.append(v)
        pools.append([data])
    elif isinstance(data, list):
        pools.append(data)

    for pool in pools:
        for item in pool:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).lower()
            symbol = str(item.get("symbol", "")).lower()
            for k in keys:
                if k.lower() in name or k.lower() in symbol:
                    return item
    return None


async def build_exchange_rate_text() -> str:
    lines = ["💱 *نرخ ارز لحظه‌ای*\n"]

    brs_data = await fetch_usd_gold()
    if brs_data:
        usd_item = _find_in_brsapi(brs_data, ["usd", "dollar", "دلار"])
        gold_item = _find_in_brsapi(brs_data, ["geram18", "gold", "طلا"])

        if usd_item:
            price = usd_item.get("price") or usd_item.get("Price") or usd_item.get("value")
            lines.append(f"💵 دلار آمریکا: `{price}` تومان")
        if gold_item:
            price = gold_item.get("price") or gold_item.get("Price") or gold_item.get("value")
            lines.append(f"🥇 طلای ۱۸ عیار (گرم): `{price}` تومان")

        if not usd_item and not gold_item:
            lines.append("⚠️ دریافت نرخ دلار/طلا موقتاً ممکن نشد.")
    else:
        lines.append("⚠️ دریافت نرخ دلار/طلا موقتاً ممکن نشد.")

    lines.append("")
    lines.append("🪙 *۱۰ ارز دیجیتال برتر (دلار):*")

    cryptos = await fetch_top_cryptos()
    if cryptos:
        for c in cryptos:
            symbol = c.get("symbol", "").upper()
            price = c.get("current_price")
            change = c.get("price_change_percentage_24h")
            change_str = f"{change:+.2f}%" if change is not None else "—"
            lines.append(f"• {symbol}: `${price}` ({change_str})")
    else:
        lines.append("⚠️ دریافت نرخ ارزهای دیجیتال موقتاً ممکن نشد.")

    return "\n".join(lines)
