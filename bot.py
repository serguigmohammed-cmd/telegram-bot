import requests
import time
import random
import hashlib

# ================= CONFIG =================
TOKEN = "8784580909:AAGliHWx9aalI_mOjXhreZxGFgrxuodpDaw"
CHAT_ID = "@orodmaroc"

APP_KEY = "530184"
APP_SECRET = "Eiyy8WsXvwGsVXhTyL2pxnuFRNwWo8UX"
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 300  # كل 5 دقائق

print("🚀 BOT STARTED...")

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

# ================= TELEGRAM =================
def send_photo_to_telegram(photo, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    data = {
        "chat_id": CHAT_ID,
        "caption": caption,
        "parse_mode": "HTML"
    }

    try:
        res = requests.post(url, data=data, files={"photo": requests.get(photo).content})
        print("📤 Telegram:", res.status_code)
    except Exception as e:
        print("❌ Telegram Error:", e)

# ================= GET PRODUCTS =================
def get_products():
    url = "https://api-sg.aliexpress.com/rest"
print(response.text)
    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": APP_KEY,
        "timestamp": str(int(time.time() * 1000)),
        "format": "json",
        "v": "2.0",
        "keywords": random.choice([
            "smart gadgets",
            "kitchen tools",
            "car accessories",
            "home decor",
            "tech gadgets"
        ]),
        "page_size": 20,
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_sign(params)

    try:
        response = requests.get(url, params=params)
        return response.json()
    except:
        return None

# ================= FILTER =================
def select_best_product(data):
    try:
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]

        best = []

        for p in products:
            try:
                price = float(p.get("target_sale_price", 0))
                orders = int(p.get("lastest_volume", 0))

                if 5 < price < 50 and orders > 100:
                    best.append(p)
            except:
                continue

        if not best:
            return None

        return random.choice(best)

    except:
        return None

# ================= FORMAT =================
def format_caption(product):
    title = product.get("product_title", "")[:80]
    price = product.get("target_sale_price", "")
    link = product.get("promotion_link") or product.get("product_detail_url", "")
    orders = product.get("lastest_volume", "0")

    return f"""
🔥 <b>عرض خاص اليوم 🇲🇦</b>

📦 {title}

💰 السعر: {price} $
📈 طلبوه: {orders} مرة

🚚 شحن للمغرب

🛒 <a href="{link}">اطلب الآن</a>
"""

# ================= MAIN =================
def main():
    while True:
        print("\n🔄 New Cycle...\n")

        data = get_products()

        if not data:
            print("❌ API Error")
            time.sleep(30)
            continue

        product = select_best_product(data)

        if not product:
            print("❌ No good product")
            time.sleep(30)
            continue

        image = product.get("product_main_image_url", "")
        caption = format_caption(product)

        send_photo_to_telegram(image, caption)

        print("✅ Posted:", product.get("product_title"))

        time.sleep(POST_INTERVAL)

# ================= RUN =================
if __name__ == "__main__":
    main()
