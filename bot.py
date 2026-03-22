import requests
import time
import random
import hashlib
import os

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

print("🚀 BOT STARTED (SECURE MODE)")

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

# ================= TELEGRAM =================
def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    try:
        img = requests.get(photo_url, timeout=10)

        if img.status_code != 200:
            print(f"❌ Image download failed: {img.status_code}")
            return False

        res = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML"
            },
            files={"photo": ("image.jpg", img.content)},
            timeout=15
        )

        # ✅ CHECK TELEGRAM RESPONSE
        if res.status_code != 200:
            print(f"❌ Telegram HTTP error: {res.status_code}")
            print(res.text)
            return False

        data = res.json()

        if not data.get("ok"):
            print("❌ Telegram API rejected message:")
            print(data)
            return False

        print("✅ Message sent")
        return True

    except Exception as e:
        print("❌ Telegram Exception:", e)
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
            "car accessories",
            "kitchen tools",
            "fitness",
            "home decor"
        ]),
        "page_size": 20,
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_sign(params)

    try:
        res = requests.get(url, params=params, timeout=15)

        print("🌐 API Status:", res.status_code)

        if res.status_code != 200:
            print("❌ API HTTP error")
            return None

        data = res.json()

        return data

    except Exception as e:
        print("❌ API Exception:", e)
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
        "promotion_link_type": "0",
        "source_values": product_url,
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_sign(params)

    try:
        res = requests.get(url, params=params, timeout=15)

        if res.status_code != 200:
            print("❌ Link HTTP error")
            return product_url

        data = res.json()

        link = data["aliexpress_affiliate_link_generate_response"]["resp_result"]["result"]["promotion_links"]["promotion_link"][0]["promotion_link"]

        return link

    except Exception as e:
        print("❌ Affiliate link error:", e)
        return product_url

# ================= FILTER =================
def pick_product(data):
    try:
        products = data.get("aliexpress_affiliate_product_query_response", {}) \
                      .get("resp_result", {}) \
                      .get("result", {}) \
                      .get("products", {}) \
                      .get("product", [])

        if not products:
            print("❌ No products found")
            return None

        good = []

        for p in products:
            try:
                price = float(p.get("target_sale_price", 0))
                orders = int(p.get("lastest_volume", 0))

                if 5 < price < 40 and orders > 200:
                    good.append(p)

            except:
                continue

        print(f"📊 Found {len(good)} good products")

        if not good:
            return None

        return random.choice(good)

    except Exception as e:
        print("❌ Parse error:", e)
        return None

# ================= TEXT =================
def generate_text(product):
    title = product.get("product_title", "")[:70]
    price = product.get("target_sale_price", "")
    orders = product.get("lastest_volume", "0")

    hooks = [
        "🔥 عرض قوي اليوم!",
        "😱 الناس كاملين كيشريوه!",
        "🚀 منتج ترند!",
        "💥 فرصة محدودة!"
    ]

    return f"""{random.choice(hooks)}

📦 {title}

💰 {price} $
📈 {orders} طلب

🚚 شحن للمغرب
"""

# ================= TEST =================
def test_telegram():
    print("🧪 Testing Telegram...")
    return send_photo(
        "https://ae01.alicdn.com/kf/Sample.jpg",
        "✅ Bot is working"
    )

# ================= MAIN =================
def main():
    if not test_telegram():
        print("❌ Telegram test failed")
        return

    while True:
        print("\n🔄 New cycle...\n")

        data = get_products()

        if not data:
            time.sleep(30)
            continue

        product = pick_product(data)

        if not product:
            time.sleep(30)
            continue

        image = product.get("product_main_image_url", "")
        normal_link = product.get("product_detail_url", "")

        aff_link = generate_link(normal_link)

        text = generate_text(product)
        caption = text + f'\n🛒 <a href="{aff_link}">اشتري الآن</a>'

        if image:
            success = send_photo(image, caption)

            if not success:
                print("⚠️ Failed to send post")

        time.sleep(POST_INTERVAL)

# ================= RUN =================
if __name__ == "__main__":
    main()
