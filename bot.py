import requests
import time
import os
import sys
import random
import hashlib

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

APP_KEY = os.getenv("ALI_APP_KEY")
APP_SECRET = os.getenv("ALI_APP_SECRET")

POST_INTERVAL = 7200
RETRY_DELAY = 60

# ================= VALIDATION =================
if not TOKEN or TOKEN.strip() == "":
    print("❌ TELEGRAM_TOKEN missing")
    sys.exit(1)

if not CHAT_ID or CHAT_ID.strip() == "":
    print("❌ TELEGRAM_CHAT_ID missing")
    sys.exit(1)

if not APP_KEY or not APP_SECRET:
    print("❌ AliExpress API keys missing")
    sys.exit(1)

# ================= PRODUCT SOURCE =================
# 👇 حط هنا روابط منتجات حقيقية (NOT xxx)
product_urls = [
    "https://www.aliexpress.com/item/1005004757833857.html",
    "https://www.aliexpress.com/item/1005007588427363.html"
]

last_product = None

# ================= HELPERS =================
def extract_id(url):
    try:
        return url.split("/item/")[1].split(".html")[0]
    except:
        return None


def get_product_details(product_id):
    url = "https://api-sg.aliexpress.com/sync"

    params = {
        "app_key": APP_KEY,
        "method": "aliexpress.affiliate.product.sku.detail.get",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "format": "json",
        "v": "2.0",
        "sign_method": "md5",

        "product_id": product_id,
        "ship_to_country": "MA",
        "target_currency": "USD",
        "target_language": "EN"
    }

    sign_str = APP_SECRET + "".join(f"{k}{params[k]}" for k in sorted(params)) + APP_SECRET
    params["sign"] = hashlib.md5(sign_str.encode()).hexdigest().upper()

    try:
        res = requests.get(url, params=params, timeout=20)
        data = res.json()

        result = data.get("result", {}).get("result", {})
        item = result.get("ae_item_info", {})
        sku = result.get("ae_item_sku_info", [{}])[0]

        return {
            "title": item.get("en_title"),
            "rating": float(item.get("product_score", 0)),
            "orders": float(item.get("order_number", 0)),
            "price": float(sku.get("sale_price_with_tax", 0)),
            "currency": sku.get("currency"),
            "image": sku.get("sku_image_link"),
            "delivery": sku.get("min_delivery_days")
        }

    except Exception as e:
        print("❌ API error:", e)
        return None


# ================= TELEGRAM =================
def send_message(text):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )

        if res.status_code != 200:
            return False

        data = res.json()
        return data.get("ok", False)

    except:
        return False


# ================= PICK SMART PRODUCT =================
def pick_product():
    global last_product

    for _ in range(10):
        url = random.choice(product_urls)

        if url == last_product:
            continue

        product_id = extract_id(url)
        if not product_id:
            continue

        details = get_product_details(product_id)
        if not details:
            continue

        # 🔥 فلترة احترافية
        if details["orders"] < 50:
            continue

        if details["rating"] < 4.5:
            continue

        if details["price"] > 50:
            continue

        last_product = url
        return details, url

    return None, None


# ================= MAIN =================
def main():
    print("🚀 Smart API Bot Started")

    while True:
        try:
            details, url = pick_product()

            if not details:
                print("⚠️ No valid product found")
                time.sleep(RETRY_DELAY)
                continue

            message = f"""🔥 منتج ترند اليوم 🇲🇦

📦 {details['title']}

💰 السعر: {details['price']} {details['currency']}
⭐ تقييم: {details['rating']}
🔥 طلبات: {details['orders']}

🚚 توصيل خلال {details['delivery']} أيام

🛒 اطلب الآن 👇
{url}
"""

            success = send_message(message)

            if success:
                print("✅ Sent smart product")
                time.sleep(POST_INTERVAL)
            else:
                print("⚠️ Failed — retrying")
                time.sleep(RETRY_DELAY)

        except Exception as e:
            print("🔥 Error:", e)
            time.sleep(RETRY_DELAY)


# ================= RUN =================
if __name__ == "__main__":
    main()
