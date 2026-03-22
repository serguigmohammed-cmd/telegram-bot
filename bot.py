import requests
import time
import random

TOKEN = "8784580909:AAHZ8B-K_DplvsKuJquLGuZzE_ZCLgemRPI"
CHAT_ID = "@orodmaroc"

posts = [
"🔥 عرض اليوم 🇲🇦 منتج رائع بثمن رخيص 💸 https://s.click.aliexpress.com/e/xxx",
"📶 حل مشكلة الويفي 😱 جهاز قوي بزاف https://s.click.aliexpress.com/e/xxx",
"⚡ كابل شحن سريع 🔥 https://s.click.aliexpress.com/e/xxx"
]

while True:
    post = random.choice(posts)
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={
        "chat_id": CHAT_ID,
        "text": post
    })
    time.sleep(7200)  # كل ساعتين
