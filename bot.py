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

POST_INTERVAL = 300  # 5 دقائق للتجربة

if not TOKEN:
    raise Exception("❌ TOKEN missing")
if not APP_SECRET:
    raise Exception("❌ APP_SECRET missing")

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger()

log.info("🚀 BOT STARTED")

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

# ================= TELEGRAM =================
def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    try:
        log.info("📥 Downloading image...")
        img = requests.get(photo_url, timeout=10)

        if img.status_code != 200:
            log.error(f"❌ Image error: {img.status_code}")
            return False

        log.info("📤 Sending to Telegram...")
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

        log.info(f"📡 Telegram status: {res.status_code}")

        if res.status_code != 200:
            log.error(res.text)
            return False

        data = res.json()

        if not data.get("ok"):
            log.error(f"❌ Telegram رفض: {data}")
            return False

        log.info("✅ Message sent successfully")
        return True

    except Exception as e:
        log.error(f"❌ Telegram error: {e}")
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
        log.info("🌐 Fetching products...")
        res = requests.get(url, params=params, timeout=15)

        log.info(f"📡 API status: {res.status_code}")

        if res.status_code != 200:
            log.error("❌ API failed")
            return None

        return res.json()

    except Exception as e:
        log.error(f"❌ API error: {e}")
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
        res = requests.get(url, params=params, timeout=15).json()
        link = res["aliexpress_affiliate_link_generate_response"]["resp_result"]["result"]["promotion_links"]["promotion_link"][0]["promotion_link"]
        return link
    except:
        return product_url

# ================= FILTER =================
def pick_product(data):
    try:
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]

        valid = []

        for p in products:
            price = float(p.get("target_sale_price", 0))
            orders = int(p.get("lastest_volume", 0))

            if 5 < price < 40 and orders > 100:
                valid.append(p)

        log.info(f"📊 Found {len(valid)} good products")

        if not valid:
            return None

        return random.choice(valid)

    except Exception as e:
        log.error(f"❌ Parse error: {e}")
        return None

# ================= MAIN =================
def main():
    while True:
        log.info("🔄 New cycle")

        data = get_products()

        if not data:
            time.sleep(20)
            continue

        product = pick_product(data)

        if not product:
            time.sleep(20)
            continue

        image = product.get("product_main_image_url", "")
        link = generate_link(product.get("product_detail_url", ""))

        caption = f"""
🔥 عرض اليوم 🇲🇦

📦 {product.get("product_title","")[:60]}

💰 {product.get("target_sale_price")} $
📈 {product.get("lastest_volume")} طلب

🛒 <a href="{link}">اشتري الآن</a>
"""

        if image:
            send_photo(image, caption)

        time.sleep(POST_INTERVAL)

# ================= RUN =================
if __name__ == "__main__":
    main()
