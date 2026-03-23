import requests
import time
import random
import os
import logging

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POST_INTERVAL = 1800
MAX_RETRIES = 3

logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# ✅ ضع روابطك هنا مرة واحدة فقط
POSTS = [
    {
        "title": "🔥 منتج ترند",
        "link": "https://s.click.aliexpress.com/e/_abc123"
    },
    {
        "title": "💡 عرض قوي",
        "link": "https://s.click.aliexpress.com/e/_def456"
    },
    {
        "title": "🎯 لا تفوت هذا",
        "link": "https://s.click.aliexpress.com/e/_ghi789"
    }
]

# ================= TELEGRAM =================
def send_message(text):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=20
        )
        return res.json().get("ok", False)
    except:
        return False

def send_with_retry(msg):
    for i in range(MAX_RETRIES):
        if send_message(msg):
            log.info("✅ Sent")
            return True
        time.sleep(5)
    return False

# ================= MAIN =================
def main():
    last_post = None

    while True:
        post = random.choice(POSTS)

        # منع التكرار
        while post == last_post:
            post = random.choice(POSTS)

        msg = f"{post['title']}\n\n🛒 {post['link']}"

        if send_with_retry(msg):
            last_post = post

        time.sleep(POST_INTERVAL)

# ================= RUN =================
main()
