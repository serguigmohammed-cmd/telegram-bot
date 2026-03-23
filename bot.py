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

POST_INTERVAL = 600      # 10 دقائق
ERROR_DELAY = 30         # retry عند الخطأ

if not TOKEN:
    raise Exception("❌ TOKEN missing (set it in Secrets)")
if not APP_SECRET:
    raise Exception("❌ APP_SECRET missing")

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger()

log.info("🚀 BOT STARTED")

# ================= MEMORY =================
used_ids = []

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
            log.info(f"📤 Attempt {attempt+1}")

            img = requests.get(photo_url, timeout=15)
            if img.status_code != 200:
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
                log.error(res.text)
                time.sleep(2)
                continue

            data = res.json()

            if not data.get("ok"):
                log.error(data)
                time.sleep(2)
                continue

            log.info("✅ Sent")
            return True

        except Exception as e:
            log.error(e)
            time.sleep(2)

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
        "keywords": random.choice(["gadgets","kitchen","car"]),
        "page_size": 20,
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_sign(params)

    try:
        res = requests.get(url, params=params, timeout=30)
        return res.json()
    except:
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
    except:
        return product_url

# ================= PICK PRODUCT =================
def pick_product(data):
    try:
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]

        valid = []

        for p in products:
            try:
                pid = p.get("product_id")

                if pid in used_ids:
                    continue

                price = float(p.get("target_sale_price", 0))
                orders = int(p.get("lastest_volume", 0))

                if 5 < price < 40 and orders > 100:
                    valid.append(p)
            except:
                continue

        if not valid:
            return None

        product = random.choice(valid)

        used_ids.append(product.get("product_id"))

        # تنظيف الذاكرة باش ما تكبرش بزاف
        if len(used_ids) > 50:
            used_ids.pop(0)

        return product

    except:
        return None

# ================= MAIN =================
def main():
    log.info("⏳ Waiting before first post...")
    time.sleep(POST_INTERVAL)

    while True:
        try:
            data = get_products()

            if not data:
                time.sleep(ERROR_DELAY)
                continue

            product = pick_product(data)

            if not product:
                time.sleep(ERROR_DELAY)
                continue

            image = product.get("product_main_image_url")
            link = generate_link(product.get("product_detail_url"))

            caption = f"""
🔥 <b>عرض اليوم 🇲🇦</b>

📦 {product.get("product_title")[:60]}

💰 {product.get("target_sale_price")} $
📈 {product.get("lastest_volume")} طلب

🚚 شحن للمغرب

🛒 <a href="{link}">اشتري الآن</a>
"""

            success = send_photo(image, caption)

            if not success:
                log.warning("⚠️ Failed → retry soon")
                time.sleep(ERROR_DELAY)
                continue

            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(f"🔥 LOOP ERROR: {e}")
            time.sleep(ERROR_DELAY)

# ================= RUN =================
if __name__ == "__main__":
    main()
