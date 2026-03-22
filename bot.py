import requests
import time
import random

# 🔐 بياناتك (عدّلها فقط هنا)
TOKEN = "8784580909:AAGliHWx9aalI_mOjXhreZxGFgrxuodpDaw"
CHAT_ID = "@orodmaroc"
APP_KEY = "530184"
TRACKING_ID = "orodmaroc"

# 🟢 جلب منتجات من AliExpress
def get_products():
    url = "https://api-sg.aliexpress.com/sync"

    params = {
        "method": "aliexpress.affiliate.product.query",
        "app_key": APP_KEY,
        "format": "json",
        "sign_method": "sha256",
        "keywords": "gadgets",  # 🔥 تقدر تبدلها
        "target_currency": "MAD",
        "target_language": "AR",
        "page_size": 10
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()
        return data.get("result", {}).get("products", [])
    except Exception as e:
        print("❌ API Error:", e)
        return []

# 🧠 اختيار منتج جيد
def pick_product(products):
    good = []

    for p in products:
        try:
            price = float(p.get("target_sale_price", 0))
            orders = int(p.get("orders_count", 0))

            if price < 200 and orders > 20:
                good.append(p)
        except:
            continue

    return random.choice(good) if good else None

# ✍️ نصوص جاهزة
templates = [
"""🔥 عرض اليوم 🇲🇦
😱 منتج غادي يعجبك بزاف!

✔ جودة عالية
✔ سهل الاستعمال
✔ مفيد يوميًا

💸 ثمن مناسب

🚚 شحن مباشر للمغرب

🔗 اطلب الآن:
{link}
""",

"""⚡ فرصة ما تتفوتش!
🔥 منتج مطلوب بزاف

✔ عملي وسريع
✔ جودة ممتازة

💰 ثمن قليل

📦 شحن للمغرب 🇲🇦

🛒 الرابط:
{link}
""",

"""🎯 حل بسيط لمشكل كبير!
😎 منتج ذكي

✔ تصميم رائع
✔ سهل الاستخدام

💸 سعر مغري

🚚 توصيل متوفر

🔗 شري دابا:
{link}
"""
]

# 🔗 إنشاء رابط أفلييت
def make_link(link):
    return f"{link}&aff_trace_key={TRACKING_ID}"

# 📤 إرسال إلى تيليجرام
def send(text, image):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    data = {
        "chat_id": CHAT_ID,
        "caption": text,
        "photo": image
    }

    try:
        requests.post(url, data=data)
    except Exception as e:
        print("❌ Telegram Error:", e)

# 🔁 تشغيل مستمر
while True:
    print("🚀 جاري جلب المنتجات...")

    products = get_products()

    if not products:
        print("❌ لا يوجد منتجات")
        time.sleep(60)
        continue

    product = pick_product(products)

    if not product:
        print("❌ لا يوجد منتج مناسب")
        time.sleep(60)
        continue

    try:
        title = product.get("product_title", "")
        price = product.get("target_sale_price", "")
        image = product.get("product_main_image_url", "")
        link = product.get("promotion_link", "")

        affiliate_link = make_link(link)

        template = random.choice(templates)
        text = template.format(link=affiliate_link)

        send(text, image)

        print("✅ تم النشر:", title)

    except Exception as e:
        print("❌ خطأ:", e)

    # ⏱️ كل ساعتين
    time.sleep(7200)
