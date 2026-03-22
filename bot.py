import requests
import time
import random
import hashlib

# ================= CONFIG =================
TOKEN = "8784580909:AAGfB5zAWaWuLwOeYDqgfQK0qPg_kw3OY4s"  # ⚠️ بدل التوكن فوراً
CHAT_ID = "@orodmaroc"

APP_KEY = "530184"
APP_SECRET = "Eiyy8WsXvwGsVXhTyL2pxnuFRNwWo8UX"
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 600  # 10 دقائق

used_products = set()

print("🚀 AUTO MONEY BOT STARTED")

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

# ================= TELEGRAM =================
def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    try:
        response = requests.get(photo_url, timeout=10)

        if response.status_code != 200:
            print("❌ Image download failed")
            return

        res = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML"
            },
            files={"photo": ("image.jpg", response.content)},
            timeout=15
        )

        print("📤 Telegram:", res.status_code, res.text)

    except Exception as e:
        print("❌ Telegram error:", e)

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
            "home decor",
            "fitness",
            "beauty"
        ]),
        "page_size": 20,
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_sign(params)

    try:
        res = requests.get(url, params=params, timeout=15)
        print("🌐 API STATUS:", res.status_code)
        print("📥 RAW:", res.text[:300])
        return res.json()
    except Exception as e:
        print("❌ API Error:", e)
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
        res = requests.get(url, params=params, timeout=15).json()

        link = res["aliexpress_affiliate_link_generate_response"]["resp_result"]["result"]["promotion_links"]["promotion_link"][0]["promotion_link"]

        return link

    except Exception as e:
        print("❌ Link Error:", e)
        return product_url  # fallback

# ================= FILTER =================
def pick_product(data):
    try:
        products = data.get("aliexpress_affiliate_product_query_response", {}) \
                      .get("resp_result", {}) \
                      .get("result", {}) \
                      .get("products", {}) \
                      .get("product", [])

        if not products:
            print("❌ No products returned")
            return None

        best = []

        for p in products:
            try:
                price = float(p.get("target_sale_price", 0))
                orders = int(p.get("lastest_volume", 0))
                pid = p.get("product_id")

                if not pid or pid in used_products:
                    continue

                if 5 < price < 40 and orders > 200:
                    best.append(p)

            except:
                continue

        print(f"📊 Found {len(best)} good products")

        if not best:
            return None

        product = random.choice(best)
        used_products.add(product.get("product_id"))

        return product

    except Exception as e:
        print("❌ Parse Error:", e)
        return None

# ================= TEXT =================
def generate_text(product):
    title = product.get("product_title", "")[:60]
    price = product.get("target_sale_price", "")
    orders = product.get("lastest_volume", "0")

    hooks = [
        "😱 هذا المنتج كيدير ضجة!",
        "🔥 الناس كاملين كيشريوه دابا!",
        "💥 عرض محدود!",
        "🚀 ترند قوي!"
    ]

    return f"""{random.choice(hooks)}

📦 {title}

💰 فقط {price} $
📈 أكثر من {orders} طلب

🚚 شحن للمغرب
"""

# ================= MAIN =================
def main():
    while True:
        print("\n🔄 Searching...\n")

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
            send_photo(image, caption)
        else:
            print("❌ No image found")

        print("✅ Posted:", product.get("product_title"))

        time.sleep(POST_INTERVAL)

# ================= RUN =================
if __name__ == "__main__":
    main()
