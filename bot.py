import requests
import time
import random
import hashlib
import os
import logging

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

APP_KEY = "530184"
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 1800
ERROR_DELAY = 60
MAX_RETRIES = 3

if not TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN missing")
if not APP_SECRET:
    raise Exception("❌ APP_SECRET missing")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# ================= KEYWORDS =================
KEYWORDS = [
    "tiktok made me buy it",
    "viral gadgets",
    "trending products",
    "smart home devices",
    "kitchen tools",
]

used_ids = []

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign.encode()).hexdigest().upper()

# ================= GET PRODUCTS =================
def get_products():
    try:
        url = "https://api-sg.aliexpress.com/rest"

        params = {
            "method": "aliexpress.affiliate.product.query",
            "app_key": APP_KEY,
            "timestamp": str(int(time.time() * 1000)),
            "format": "json",
            "v": "2.0",
            "keywords": random.choice(KEYWORDS),
            "page_size": 20,
            "tracking_id": TRACKING_ID
        }

        params["sign"] = generate_sign(params)

        res = requests.get(url, params=params, timeout=30)

        if res.status_code != 200:
            log.error(f"API HTTP {res.status_code}")
            return None

        return res.json()

    except Exception as e:
        log.error(f"API error: {e}")
        return None

# ================= FILTER =================
def pick_best_product(data):
    try:
        products = (
            data.get("aliexpress_affiliate_product_query_response", {})
            .get("resp_result", {})
            .get("result", {})
            .get("products", {})
            .get("product", [])
        )

        best = []

        for p in products:
            try:
                pid = p.get("product_id")
                if pid in used_ids:
                    continue

                price = float(p.get("target_sale_price", 0))
                orders = int(p.get("lastest_volume", 0))
                rating = float(p.get("evaluate_rate", 0))

                if 5 < price < 50 and orders > 1000 and rating >= 4.5:
                    score = orders * rating
                    best.append((score, p))
            except:
                continue

        if not best:
            log.warning("⚠️ No good products found")
            return None

        best.sort(reverse=True)
        product = best[0][1]

        used_ids.append(product.get("product_id"))
        if len(used_ids) > 100:
            used_ids.pop(0)

        return product

    except Exception as e:
        log.error(f"Parse error: {e}")
        return None

# ================= GENERATE LINK =================
def generate_link(product_url):
    try:
        url = "https://api-sg.aliexpress.com/rest"

        params = {
            "method": "aliexpress.affiliate.link.generate",
            "app_key": APP_KEY,
            "timestamp": str(int(time.time() * 1000)),
            "format": "json",
            "v": "2.0",
            "source_values": product_url,
            "tracking_id": TRACKING_ID
        }

        params["sign"] = generate_sign(params)

        res = requests.get(url, params=params, timeout=30)
        data = res.json()

        link = (
            data
            .get("aliexpress_affiliate_link_generate_response", {})
            .get("resp_result", {})
            .get("result", {})
            .get("promotion_links", {})
            .get("promotion_link", [{}])[0]
            .get("promotion_link")
        )

        if not link:
            log.error(f"❌ Affiliate link failed: {data}")
            return product_url

        return link

    except Exception as e:
        log.error(f"Link error: {e}")
        return product_url

# ================= FORMAT =================
def build_caption(p, link):
    title = (p.get("product_title") or "")[:70]
    price = p.get("target_sale_price")
    orders = p.get("lastest_volume")

    return f"""🔥 <b>منتج ترند في المغرب 🇲🇦</b>

📦 {title}

💰 فقط {price}$
📈 +{orders} طلب

⚠️ العرض محدود!

🚚 شحن سريع

🛒 <a href="{link}">اطلب الآن قبل نفاذ الكمية</a>
"""

# ================= TELEGRAM =================
def send_message(text):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=20
        )
        data = res.json()

        if not data.get("ok"):
            log.error(f"❌ Telegram error: {data}")
            return False

        return True

    except Exception as e:
        log.error(e)
        return False


def send(photo, caption):
    for attempt in range(MAX_RETRIES):
        try:
            img = requests.get(photo, timeout=10)

            if img.status_code != 200:
                return send_message(caption)

            res = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"},
                files={"photo": ("img.jpg", img.content)},
                timeout=20
            )

            data = res.json()

            if data.get("ok"):
                log.info("✅ Posted")
                return True
            else:
                log.error(f"❌ Telegram reject: {data}")

        except Exception as e:
            log.error(e)

        time.sleep(5)

    return False

# ================= MAIN =================
def main():
    log.info("🚀 Smart bot started")

    while True:
        try:
            data = get_products()
            if not data:
                time.sleep(ERROR_DELAY)
                continue

            product = pick_best_product(data)
            if not product:
                time.sleep(ERROR_DELAY)
                continue

            link = generate_link(product.get("product_detail_url"))
            caption = build_caption(product, link)

            success = send(product.get("product_main_image_url"), caption)

            if not success:
                log.warning("⚠️ Failed to send → retry soon")
                time.sleep(ERROR_DELAY)
                continue

            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(f"Loop error: {e}")
            time.sleep(ERROR_DELAY)

# ================= RUN =================
if __name__ == "__main__":
    main()
