import hashlib

def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.sha256(sign_str.encode()).hexdigest().upper()
import requests
import time
import random

# ================= CONFIG =================
TOKEN = "8784580909:AAGliHWx9aalI_mOjXhreZxGFgrxuodpDaw"
CHAT_ID = "@orodmaroc"

APP_KEY = "530184"
APP_SECRET = "Eiyy8WsXvwGsVXhTyL2pxnuFRNwWo8UX"
TRACKING_ID = "orodmaroc"

# ================= TELEGRAM =================
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

# ================= GET PRODUCTS =================
def get_products():
    url = "https://api-sg.aliexpress.com/sync"

    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": APP_KEY,
        "sign_method": "sha256",
        "timestamp": int(time.time() * 1000),
        "format": "json",
        "v": "2.0",
        "keywords": "smart gadgets",
        "page_size": 10,
        "fields": "product_title,product_main_image_url,sale_price,product_detail_url,product_id,commission_rate"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data
    except:
        return None

# ================= FILTER WINNING PRODUCTS =================
def select_best_product(data):
    try:
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]

        # فلترة المنتجات
        good_products = []

        for p in products:
            try:
                price = float(p.get("sale_price", 0))
                commission = float(p.get("commission_rate", 0))

                # شروط الربح
                if price > 5 and commission > 5:
                    good_products.append(p)
            except:
                continue

        if not good_products:
            return None

        return random.choice(good_products)

    except:
        return None

# ================= FORMAT MESSAGE =================
def format_message(product):
    title = product.get("product_title", "منتج رائع")
    price = product.get("sale_price", "")
    link = product.get("product_detail_url", "")

    affiliate_link = f"{link}&aff_fcid={TRACKING_ID}"

    message = f"""
🔥 <b>عرض اليوم</b>

📦 {title}

💰 السعر: {price} $

🚚 شحن للمغرب 🇲🇦

🔗 <a href="{affiliate_link}">اضغط هنا للشراء</a>
"""

    return message

# ================= MAIN LOOP =================
while True:
    data = get_products()

    if data:
        product = select_best_product(data)

        if product:
            msg = format_message(product)
            send_to_telegram(msg)
            print("Posted:", product.get("product_title"))

    time.sleep(7200)  # كل ساعتين
