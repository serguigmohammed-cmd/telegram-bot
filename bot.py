import requests
import time
import random
import hashlib
import os
import logging

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
APP_SECRET = os.getenv("APP_SECRET")

CHAT_ID = "@orodmaroc"
APP_KEY = "530184"
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 600

if not TOKEN:
    raise Exception("❌ TOKEN missing (add it in Secrets)")
if not APP_SECRET:
    raise Exception("❌ APP_SECRET missing (add it in Secrets)")

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
log = logging.getLogger()

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

# ================= TELEGRAM =================
def send_message(photo, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    try:
        img = requests.get(photo, timeout=10)

        res = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML"
            },
            files={"photo": ("img.jpg", img.content)},
            timeout=15
        )

        # ✅ تحقق من النتيجة
        if res.status_code != 200:
            log.error(f"❌ HTTP Error: {res.status_code}")
            return False

        data = res.json()

        if not data.get("ok"):
            log.error(f"❌ Telegram رفض الرسالة: {data}")
            return False

        log.info("✅ Message sent")
        return True

    except Exception as e:
        log.error(f"❌ Error: {e}")
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
        "page_size": 20,
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_sign(params)

    try:
        res = requests.get(url, params=params, timeout=15)

        if res.status_code != 200:
            log.error("❌ API error")
            return None

        return res.json()

    except Exception as e:
        log.error(f"❌ API exception: {e}")
        return None

# ================= AFFILIATE LINK =================
def generate_link(url_product):
    if not url_product:
        return ""

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

    try:
        res = requests.get(url, params=params, timeout=15).json()

        return res["aliexpress_affiliate_link_generate_response"]["resp_result"]["result"]["promotion_links"]["promotion_link"][0]["promotion_link"]

    except:
        return url_product

# ================= FILTER =================
def pick_product(data):
    try:
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]

        valid = []

        for p in products:
            price = float(p.get("target_sale_price", 0))
            orders = int(p.get("lastest_volume", 0))

            if 5 < price < 40 and orders > 200:
                valid.append(p)

        if not valid:
            return None

        return random.choice(valid)

    except:
        return None

# ================= MAIN =================
def main():
    log.info("🚀 Bot started")

    while True:
        data = get_products()

        if not data:
            time.sleep(30)
            continue

        product = pick_product(data)

        if not product:
            time.sleep(30)
            continue

        image = product.get("product_main_image_url", "")
        link = generate_link(product.get("product_detail_url", ""))

        caption = f"""
🔥 عرض اليوم

📦 {product.get("product_title","")[:70]}

💰 {product.get("target_sale_price")} $
📈 {product.get("lastest_volume")} طلب

🛒 <a href="{link}">اشتري الآن</a>
"""

        send_message(image, caption)

        time.sleep(POST_INTERVAL)

# ================= RUN =================
if __name__ == "__main__":
    main()
