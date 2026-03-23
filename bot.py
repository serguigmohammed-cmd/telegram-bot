import requests
import time
import random
import hashlib
import os
import logging

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")

CHAT_ID = "@orodmaroc"
APP_KEY = "530184"
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 1800
ERROR_DELAY = 60

if not TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN missing")
if not APP_SECRET:
    raise Exception("❌ APP_SECRET missing")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# ================= KEYWORDS =================
KEYWORDS = [
    "tiktok gadgets",
    "viral products",
    "smart gadgets",
    "kitchen tools",
    "car accessories"
]

used_ids = []

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign.encode()).hexdigest().upper()

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
    except Exception as e:
        log.error(e)
        return None

# ================= FILTER =================
def pick_best_product(data):
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

                # 🔥 فلترة ذكية
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

    except Exception as e:
        log.error(e)
        return None

# ================= GENERATE LINK =================
def generate_link(url_product):
    try:
        url = "https://api-sg.aliexpress.com/rest"

        params = {
            "method": "aliexpress.affiliate.link.generate",
            "app_key": APP_KEY,
            "timestamp": str(int(time.time() * 1000)),
            "format": "json",
            "v": "2.0",
            "source_values": url_product,
            "tracking_id": TRACKING_ID
        }

        params["sign"] = generate_sign(params)

        res = requests.get(url, params=params, timeout=30).json()

        return res["aliexpress_affiliate_link_generate_response"]["resp_result"]["result"]["promotion_links"]["promotion_link"][0]["promotion_link"]

    except:
        return url_product

# ================= FORMAT =================
def build_caption(p, link):
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

# ================= TELEGRAM =================
def send(photo, caption):
    try:
        img = requests.get(photo, timeout=10)

        if img.status_code != 200:
            return

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"},
            files={"photo": ("img.jpg", img.content)}
        )

        log.info("✅ Posted")

    except Exception as e:
        log.error(e)

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

            send(product.get("product_main_image_url"), caption)

            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(e)
            time.sleep(ERROR_DELAY)

# ================= RUN =================
if __name__ == "__main__":
    main()
