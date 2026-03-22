import requests
import time
import random
import hashlib
import urllib.parse

# Telegram
TOKEN = "PUT_YOUR_TELEGRAM_TOKEN"
CHAT_ID = "@orodmaroc"

# AliExpress API
APP_KEY = "PUT_YOUR_APP_KEY"
APP_SECRET = "PUT_YOUR_APP_SECRET"
TRACKING_ID = "PUT_YOUR_TRACKING_ID"

def get_products():
    url = "https://api-sg.aliexpress.com/sync"
    
    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": APP_KEY,
        "sign_method": "sha256",
        "timestamp": str(int(time.time() * 1000)),
        "format": "json",
        "v": "2.0",
        "keywords": "gadget",
        "sort": "SALE_PRICE_ASC",
        "target_currency": "MAD",
        "target_language": "AR",
        "tracking_id": TRACKING_ID
    }

    # توقيع الطلب (signature)
    sorted_params = sorted(params.items())
    sign_str = APP_SECRET + ''.join(f"{k}{v}" for k, v in sorted_params) + APP_SECRET
    sign = hashlib.sha256(sign_str.encode()).hexdigest().upper()
    params["sign"] = sign

    response = requests.get(url, params=params)
    data = response.json()

    try:
        products = data["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]
        return products
    except:
        return []

def format_post(product):
    title = product.get("product_title", "منتج رائع")
    price = product.get("target_sale_price", "??")
    link = product.get("promotion_link", "")

    return f"""🔥 عرض اليوم 🇲🇦

{title[:80]}

💸 السعر: {price} درهم
🚚 شحن للمغرب

🔗 اطلب الآن:
{link}"""

while True:
    products = get_products()

    if products:
        product = random.choice(products)
        message = format_post(product)

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": message
            }
        )

    time.sleep(7200)
