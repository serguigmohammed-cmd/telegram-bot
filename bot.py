import requests
import time
import random
import hashlib

# ================= CONFIG =================
TOKEN = "8784580909:AAGliHWx9aalI_mOjXhreZxGFgrxuodpDaw"
CHAT_ID = "@orodmaroc"

APP_KEY = "530184"
APP_SECRET = "Eiyy8WsXvwGsVXhTyL2pxnuFRNwWo8UX"  # بدون مسافة
TRACKING_ID = "orodmaroc"

print("🔥 BOT IS STARTING...")

# ================= SIGN FUNCTION =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
sign = hashlib.md5(sign_str.encode()).hexdigest().upper()
print("🔐 SIGN:", sign)
    return sign

# ================= TELEGRAM =================
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        res = requests.post(url, data=data)
        print("📤 Telegram Status:", res.status_code)
    except Exception as e:
        print("❌ Telegram Error:", e)

# ================= GET PRODUCTS =================
def get_products():
url = "https://api-sg.aliexpress.com/rest"
    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": APP_KEY,
        "timestamp": str(int(time.time() * 1000)),  # ✅ تصحيح مهم
        "format": "json",
        "v": "2.0",
        "keywords": "smart gadgets",
        "page_size": 10,
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_sign(params)

    print("📡 PARAMS:", params)

    try:
        response = requests.get(url, params=params)

        print("🌐 STATUS:", response.status_code)
        print("📥 RESPONSE:", response.text[:500])

        return response.json()

    except Exception as e:
        print("❌ API Error:", e)
        return None

# ================= FILTER PRODUCTS =================
def select_best_product(data):
    try:
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]

        good_products = []

        for p in products:
            try:
                price = float(p.get("target_sale_price", 0))
                orders = int(p.get("lastest_volume", 0))

                if price > 5 and orders > 20:
                    good_products.append(p)

            except:
                continue

        print(f"📊 Found {len(good_products)} good products")

        if not good_products:
            return None

        return random.choice(good_products)

    except Exception as e:
        print("❌ Parse Error:", e)
        return None

# ================= FORMAT MESSAGE =================
def format_message(product):
    title = product.get("product_title", "منتج رائع")
    price = product.get("target_sale_price", "")
    link = product.get("promotion_link", "")

    return f"""
🔥 <b>عرض اليوم 🇲🇦</b>

📦 {title[:100]}

💰 السعر: {price} $

🚚 شحن مباشر للمغرب

🔗 <a href="{link}">اطلب الآن</a>
"""

# ================= MAIN =================
def main():
    while True:
        print("\n🔄 دورة جديدة...\n")

        data = get_products()

        if not data:
            print("❌ API لم يرجع بيانات")
            time.sleep(20)
            continue

        product = select_best_product(data)

        if not product:
            print("❌ لا يوجد منتج مناسب")
            time.sleep(20)
            continue

        msg = format_message(product)

        send_to_telegram(msg)

        print("✅ تم النشر:", product.get("product_title"))

        time.sleep(20)  # للتجربة

# ================= RUN =================
if __name__ == "__main__":
    main()
