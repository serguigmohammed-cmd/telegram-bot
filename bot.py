import requests
import time
import random

# 🔐 بياناتك
TELEGRAM_TOKEN = "PUT_YOUR_TELEGRAM_TOKEN"
CHAT_ID = "@orodmaroc"

ALIEXPRESS_APP_KEY = "PUT_API_KEY"
ALIEXPRESS_APP_SECRET = "PUT_SECRET"

TRACKING_ID = "orodmaroc"

# 🧠 GPT (اختياري لكن مهم)
OPENAI_API_KEY = "PUT_OPENAI_KEY"


# 🟢 جلب منتجات من AliExpress
def get_products():
    url = "https://api-sg.aliexpress.com/sync"
    
    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": ALIEXPRESS_APP_KEY,
        "format": "json",
        "sign_method": "sha256",
        "keywords": "gadgets",
        "target_currency": "MAD",
        "target_language": "AR",
        "page_size": 10
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()

        products = data.get("result", {}).get("products", [])
        return products

    except:
        return []


# 🧠 اختيار منتج رابح
def pick_winning_product(products):
    good = []

    for p in products:
        try:
            price = float(p["target_sale_price"])
            orders = int(p.get("orders_count", 0))

            if price < 200 and orders > 50:
                good.append(p)
        except:
            continue

    return random.choice(good) if good else None


# 🤖 كتابة محتوى بالذكاء الاصطناعي
def generate_text(title, price):
    prompt = f"""
    اكتب إعلان تسويقي احترافي باللهجة المغربية لمنتج:
    {title}
    السعر: {price} درهم

    اجعله قصير + جذاب + فيه إيموجي + يدفع للشراء
    """

    try:
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        return res.json()["choices"][0]["message"]["content"]

    except:
        return f"🔥 عرض قوي! {title} بثمن {price} درهم فقط!"


# 🔗 توليد رابط أفلييت
def make_affiliate_link(link):
    return f"{link}&aff_trace_key={TRACKING_ID}"


# 📤 إرسال إلى تيليجرام
def send_to_telegram(text, image):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    data = {
        "chat_id": CHAT_ID,
        "caption": text,
        "photo": image,
        "parse_mode": "HTML"
    }

    requests.post(url, data=data)


# 🔁 التشغيل المستمر
while True:
    print("🚀 جاري جلب المنتجات...")

    products = get_products()

    if not products:
        print("❌ لا يوجد منتجات")
        time.sleep(60)
        continue

    product = pick_winning_product(products)

    if not product:
        print("❌ لا يوجد منتج رابح")
        time.sleep(60)
        continue

    title = product["product_title"]
    price = product["target_sale_price"]
    image = product["product_main_image_url"]
    link = product["promotion_link"]

    affiliate_link = make_affiliate_link(link)

    text = generate_text(title, price)

    final_post = f"""
{text}

💰 السعر: {price} درهم
🚚 شحن للمغرب 🇲🇦

🔗 اطلب الآن:
{affiliate_link}
"""

    send_to_telegram(final_post, image)

    print("✅ تم النشر")

    # كل ساعتين
    time.sleep(7200)
