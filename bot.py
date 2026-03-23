import requests
import time
import random
import hashlib
import os
import logging

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")   # ✅ من Secrets
APP_SECRET = os.getenv("APP_SECRET")

CHAT_ID = "@orodmaroc"
APP_KEY = "530184"
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 600
ERROR_DELAY = 30

if not TOKEN:
    raise Exception("❌ TOKEN missing")
if not APP_SECRET:
    raise Exception("❌ APP_SECRET missing")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

log.info("🚀 BOT STARTED")

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

# ================= TELEGRAM =================
def send_message(photo, caption):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={
                "chat_id": CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML"
            },
            files={"photo": requests.get(photo).content},
            timeout=20
        )

        if res.status_code != 200:
            log.error(res.text)
            return False

        data = res.json()
        if not data.get("ok"):
            log.error(data)
            return False

        log.info("✅ Sent")
        return True

    except Exception as e:
        log.error(e)
        return False

# ================= PRODUCTS =================
def get_products():
    url = "https://api-sg.aliexpress.com/rest"

    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": APP_KEY,
        "timestamp": str(int(time.time() * 1000)),
        "format": "json",
        "v": "2.0",
        "keywords": random.choice(["gadgets","kitchen","car"]),
        "page_size": 10,
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_sign(params)

    try:
        res = requests.get(url, params=params, timeout=20)
        return res.json()
    except:
        return None

# ================= LINK =================
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

        res = requests.get(url, params=params).json()

        return res["aliexpress_affiliate_link_generate_response"]["resp_result"]["result"]["promotion_links"]["promotion_link"][0]["promotion_link"]

    except:
        return url_product

# ================= PICK =================
def pick_product(data):
    try:
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]

        valid = []
        for p in products:
            price = float(p.get("target_sale_price", 0))
            orders = int(p.get("lastest_volume", 0))

            if price > 5 and orders > 100:
                valid.append(p)

        if not valid:
            return None

        return random.choice(valid)

    except:
        return None

# ================= MAIN =================
def main():
    time.sleep(10)  # avoid instant send

    while True:
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
🔥 <b>عرض اليوم</b>

📦 {product.get("product_title")[:60]}

💰 {product.get("target_sale_price")} $
📈 {product.get("lastest_volume")} طلب

🛒 <a href="{link}">اشتري الآن</a>
"""

        send_message(image, caption)

        time.sleep(POST_INTERVAL)

# ================= RUN =================
if __name__ == "__main__":
    main()
