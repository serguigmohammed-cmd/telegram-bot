import requests
import time
import random
import hashlib
import os
import logging
from datetime import datetime

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")

CHAT_ID = "@orodmaroc"
APP_KEY = "530184"
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 1800  # كل 30 دقيقة
ERROR_DELAY = 60

if not TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN missing")
if not APP_SECRET:
    raise Exception("❌ APP_SECRET missing")

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# ================= SMART KEYWORDS =================
KEYWORDS = [
    "trending gadgets",
    "tiktok gadgets",
    "smart home devices",
    "car accessories",
    "kitchen tools",
    "viral products",
]

# ================= MEMORY =================
used_ids = []

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

# ================= BEST TIME FILTER =================
def is_good_time():
    hour = datetime.now().hour
    # أوقات قوية للنشر
    return hour in [10, 13, 18, 21, 23]

# ================= TELEGRAM =================
def send_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=20
        )
    except Exception as e:
        log.error(e)

def send_photo(photo_url, caption):
    try:
        img = requests.get(photo_url, timeout=10)
        if img.status_code != 200:
            return send_message(caption)

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"},
            files={"photo": ("img.jpg", img.content)},
            timeout=20
        )
    except Exception as e:
        log.error(e)

# ================= GET PRODUCTS =================
def get_products():
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

    try:
        res = requests.get(url, params=params, timeout=30)
        return res.json()
    except:
        return None

# ================= SMART FILTER =================
def pick_product(data):
    try:
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]

        best = []

        for p in products:
            try:
                pid = p.get("product_id")
                if pid in used_ids:
                    continue

                price = float(p.get("target_sale_price", 0))
                orders = int(p.get("lastest_volume", 0))
                rating = float(p.get("evaluate_rate", 0))

                # 🔥 فلترة احترافية
                if (
                    3 < price < 50 and
                    orders > 300 and
                    rating >= 4.5
                ):
                    score = orders * rating
                    best.append((score, p))

            except:
                continue

        if not best:
            return None

        best.sort(reverse=True)
        product = best[0][1]

        used_ids.append(product.get("product_id"))
        if len(used_ids) > 100:
            used_ids.pop(0)

        return product

    except:
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

        res = requests.get(url, params=params, timeout=30).json()

        return res["aliexpress_affiliate_link_generate_response"]["resp_result"]["result"]["promotion_links"]["promotion_link"][0]["promotion_link"]

    except:
        return product_url

# ================= FORMAT POST =================
def format_caption(p, link):
    title = (p.get("product_title") or "")[:70]
    price = p.get("target_sale_price")
    orders = p.get("lastest_volume")

    return f"""🔥 <b>منتج ترند اليوم 🇲🇦</b>

📦 {title}

💰 فقط {price}$
📈 +{orders} طلب

🚚 شحن سريع للمغرب

🛒 <a href="{link}">اطلب الآن قبل نفاذ الكمية</a>
"""

# ================= MAIN =================
def main():
    while True:
        try:
            if not is_good_time():
                time.sleep(600)
                continue

            log.info("🚀 Posting...")

            data = get_products()
            if not data:
                time.sleep(ERROR_DELAY)
                continue

            product = pick_product(data)
            if not product:
                time.sleep(ERROR_DELAY)
                continue

            link = generate_link(product.get("product_detail_url"))
            caption = format_caption(product, link)

            send_photo(product.get("product_main_image_url"), caption)

            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(f"ERROR: {e}")
            time.sleep(ERROR_DELAY)

# ================= RUN =================
if __name__ == "__main__":
    main()
