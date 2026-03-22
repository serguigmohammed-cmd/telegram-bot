import requests
import time
import random
import hashlib
import hmac
import urllib.parse
from datetime import datetime

# ================== CONFIG ==================
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "@orodmaroc"

APP_KEY = "YOUR_APP_KEY"
APP_SECRET = "YOUR_APP_SECRET"
TRACKING_ID = "YOUR_TRACKING_ID"

# ================== TELEGRAM ==================
def send_to_telegram(text, image=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto" if image else f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    data = {
        "chat_id": CHAT_ID,
        "caption" if image else "text": text,
        "parse_mode": "HTML"
    }

    if image:
        data["photo"] = image

    requests.post(url, data=data)

# ================== GET PRODUCTS ==================
def get_products():
    url = "https://api-sg.aliexpress.com/sync"

    params = {
        "app_key": APP_KEY,
        "method": "aliexpress.affiliate.product.query",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "sign_method": "sha256",
        "format": "json",
        "v": "2.0",
        "keywords": "gadgets",
        "page_no": 1,
        "page_size": 5,
        "tracking_id": TRACKING_ID
    }

    # توليد التوقيع
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    sign = hashlib.sha256(sign_str.encode()).hexdigest().upper()

    params["sign"] = sign

    response = requests.get(url, params=params)
    data = response.json()

    try:
        return data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]
    except:
        return []

# ================== FORMAT POST ==================
def format_post(product):
    title = product.get("product_title", "منتج رائع")
    price = product.get("target_sale_price", "")
    discount = product.get("discount", "")
    link = product.get("promotion_link", "")
    image = product.get("product_main_image_url", "")

    text = f"""🔥 عرض اليوم 🇲🇦

🛍️ {title}

💰 السعر: {price}
🎯 تخفيض: {discount}

🚚 شحن للمغرب

🔗 اطلب الآن:
{link}
"""

    return text, image

# ================== MAIN LOOP ==================
while True:
    products = get_products()

    if products:
        product = random.choice(products)
        text, image = format_post(product)
        send_to_telegram(text, image)

    else:
        send_to_telegram("⚠️ لم يتم جلب منتجات")

    time.sleep(7200)  # كل ساعتين
