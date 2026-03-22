import requests
import time
import random
import hashlib
from datetime import datetime

# ========= CONFIG =========
TOKEN = "8784580909:AAGliHWx9aalI_mOjXhreZxGFgrxuodpDaw"
CHAT_ID = "@orodmaroc"

APP_KEY = "YOUR_APP_KEY"
APP_SECRET = "YOUR_APP_SECRET"
TRACKING_ID = "YOUR_TRACKING_ID"

sent_links = set()

# ========= TELEGRAM =========
def send_post(text, image):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    data = {
        "chat_id": CHAT_ID,
        "photo": image,
        "caption": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

# ========= SIGN =========
def sign(params):
    sorted_params = dict(sorted(params.items()))
    s = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.sha256(s.encode()).hexdigest().upper()

# ========= GET PRODUCTS =========
def get_products():
    url = "https://api-sg.aliexpress.com/sync"

    keywords_list = [
        "kitchen tools",
        "car accessories",
        "smart gadgets",
        "fitness",
        "home improvement"
    ]

    params = {
        "app_key": APP_KEY,
        "method": "aliexpress.affiliate.product.query",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "sign_method": "sha256",
        "format": "json",
        "v": "2.0",
        "keywords": random.choice(keywords_list),
        "page_no": 1,
        "page_size": 20,
        "tracking_id": TRACKING_ID,
        "sort": "LAST_VOLUME_DESC"  # الأكثر مبيعًا 🔥
    }

    params["sign"] = sign(params)

    try:
        res = requests.get(url, params=params).json()
        return res["aliexpress_affiliate_product_query_response"]["resp_result"]["result"]["products"]["product"]
    except:
        return []

# ========= AI SCORE =========
def score_product(p):
    try:
        price = float(p.get("target_sale_price", 0))
        orders = int(p.get("lastest_volume", 0))
        rating = float(p.get("evaluate_rate", 0))

        score = 0

        if price < 30:
            score += 2
        if orders > 100:
            score += 3
        if rating >= 4.5:
            score += 3

        return score
    except:
        return 0

# ========= PICK BEST =========
def pick_winner(products):
    scored = [(p, score_product(p)) for p in products]
    scored = sorted(scored, key=lambda x: x[1], reverse=True)

    for p, s in scored:
        link = p.get("promotion_link", "")
        if link not in sent_links and s >= 5:
            return p

    return None

# ========= AI COPYWRITING =========
def generate_caption(p):
    title = p.get("product_title", "")
    price = p.get("target_sale_price", "")
    discount = p.get("discount", "")
    link = p.get("promotion_link", "")
    image = p.get("product_main_image_url", "")

    hooks = [
        "🔥 منتج عليه طلب كبير!",
        "💥 الناس كاملين كيشريوه!",
        "🚀 الأكثر مبيعًا الآن!",
        "😱 عرض محدود!"
    ]

    benefits = [
        "✔ جودة عالية",
        "✔ سهل الاستعمال",
        "✔ مفيد يوميًا",
        "✔ تصميم رائع"
    ]

    caption = f"""
{random.choice(hooks)} 🇲🇦

🛍️ <b>{title}</b>

{random.choice(benefits)}
{random.choice(benefits)}

💰 السعر: {price}$
🎯 تخفيض: {discount}

🚚 شحن للمغرب

🔗 <a href="{link}">اطلب الآن</a>
"""

    return caption, image, link

# ========= MAIN =========
while True:
    products = get_products()

    if not products:
        time.sleep(1800)
        continue

    winner = pick_winner(products)

    if winner:
        caption, image, link = generate_caption(winner)
        send_post(caption, image)
        sent_links.add(link)
        print("Posted:", link)

    else:
        print("No good product found")

    time.sleep(3600)  # كل ساعة
