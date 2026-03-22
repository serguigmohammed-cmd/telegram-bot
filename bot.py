import requests
import time
import random
import hashlib
import os
import logging

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")              # 🔐 من Secrets
APP_SECRET = os.getenv("APP_SECRET")

CHAT_ID = "@orodmaroc"
APP_KEY = "530184"
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 600  # 10 دقائق

if not TOKEN:
    raise Exception("❌ TOKEN missing (add it in Secrets)")
if not APP_SECRET:
    raise Exception("❌ APP_SECRET missing (add it in Secrets)")

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger()

log.info("🚀 BOT STARTED")

# ================= MEMORY =================
used_products = set()

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

# ================= TELEGRAM =================
def send_photo(photo_url, caption, retries=3):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    for attempt in range(retries):
        try:
            img = requests.get(photo_url, timeout=15)

            if img.status_code != 200:
                log.error(f"❌ Image error: {img.status_code}")
                return False

            res = requests.post(
                url,
                data={
                    "chat_id": CHAT_ID,
                    "caption": caption,
                    "parse_mode": "HTML"
                },
                files={"photo": ("img.jpg", img.content)},
                timeout=30
            )

            if res.status_code != 200:
                log.error(f"❌ HTTP {res.status_code}: {res.text}")
                time.sleep(2)
                continue

            data = res.json()

            if not data.get("ok"):
                log.error(f"❌ Telegram rejected: {data}")
                time.sleep(2)
                continue

            log.info("✅ Message sent successfully")
            return True

        except Exception as e:
            log.error(f"❌ Send error: {e}")
            time.sleep(2)

    log.error("❌ Failed after retries")
    return False

# ================= GET PRODUCTS =================
def get_products():
    url = "https://api-sg.aliexpress.com/rest"

    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": APP_KEY,
        "timestamp": str(int(time.time() * 1000)),
        "format": "json",
        "v": "2.0",
        "keywords": random.choice([
            "smart gadgets",
            "kitchen tools",
            "car accessories"
        ]),
        "page_size": 10,
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_sign(params)

    try:
        res = requests.get(url, params=params, timeout=30)

        log.info(f"🌐 API Status: {res.status_code}")

        if res.status_code != 200:
            log.error("❌ API error")
            return None

        return res.json()

    except Exception as e:
        log.error(f"❌ API exception: {e}")
        return None

# ================= AFFILIATE LINK =================
def generate_link(product_url):
    if not product_url:
        return ""

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

    try:
        res = requests.get(url, params=params, timeout=30).json()

        return res["aliexpress_affiliate_link_generate_response"]["resp_result"]["result"]["promotion_links"]["promotion_link"][0]["promotion_link"]

    except Exception as e:
        log.error(f"❌ Link error: {e}")
        return product_url

# ================= FILTER =================
def pick_product(data):
    try:
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]

        good = []

        for p in products:
            try:
                pid = p.get("product_id")

                if pid in used_products:
                    continue

                price = float(p.get("target_sale_price", 0))
                orders = int(p.get("lastest_volume", 0))

                if 5 < price < 40 and orders > 100:
                    good.append(p)

            except:
                continue

        log.info(f"📊 Found {len(good)} good products")

        if not good:
            return None

        product = random.choice(good)
        used_products.add(product.get("product_id"))

        return product

    except Exception as e:
        log.error(f"❌ Parse error: {e}")
        return None

# ================= MAIN =================
def main():
    log.info("🚀 Bot started successfully")

    while True:
        try:
            log.info("🔄 New cycle")

            data = get_products()

            if not data:
                time.sleep(20)
                continue

            product = pick_product(data)

            if not product:
                log.warning("⚠️ No product found")
                time.sleep(20)
                continue

            image = product.get("product_main_image_url", "")
            normal_link = product.get("product_detail_url", "")

            aff_link = generate_link(normal_link)

            caption = f"""
🔥 <b>عرض اليوم 🇲🇦</b>

📦 {product.get("product_title","")[:60]}

💰 السعر: {product.get("target_sale_price")} $
📈 الطلبات: {product.get("lastest_volume")}

🚚 شحن للمغرب

🛒 <a href="{aff_link}">اشتري الآن</a>
"""

            if image:
                success = send_photo(image, caption)

                if not success:
                    time.sleep(30)
                    continue

            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(f"🔥 LOOP ERROR: {e}")
            time.sleep(30)

# ================= RUN =================
if __name__ == "__main__":
    main()
