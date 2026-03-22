import requests
import time
import random

TOKEN = "8784580909:AAHZ8B-K_DplvsKuJquLGuZzE_ZCLgemRPI"
CHAT_ID = "@orodmaroc"

posts = [
"""🔥 عرض اليوم 🇲🇦 جهاز قياس الضغط
😱 بثمن خيالي!

✔ دقيق وسريع
✔ سهل الاستعمال
✔ مناسب للمنزل

🚚 شحن مباشر للمغرب
💸 تخفيض كبير

🔗 اطلب الآن:
https://s.click.aliexpress.com/e/رابطك""",

"""📶 عندك مشكل في الويفي؟ 😤
الحل هنا 👇

🔥 جهاز تقوية إشارة WiFi
✔ يغطي الدار كاملة
✔ تركيب سهل
✔ سرعة عالية

💥 عرض محدود!

🔗 اشتري الآن:
https://s.click.aliexpress.com/e/رابطك""",

"""⚡ كابل شحن سريع 🔥
ما غاديش تبقى تسنى!

✔ شحن سريع جدا
✔ متوافق مع جميع الهواتف
✔ جودة عالية 💯

💸 ثمن رخيص بزاف

🔗 خذو دابا:
https://s.click.aliexpress.com/e/رابطك"""
]

while True:
    post = random.choice(posts)

    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": post
        }
    )

    # طباعة الحالة (باش تعرف واش خدم)
    print(response.json())

    # كل ساعتين
    time.sleep(7200)
