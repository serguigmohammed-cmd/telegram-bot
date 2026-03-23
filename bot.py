import requests
import time
import random
import hashlib
import os
import logging
import sys

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POST_INTERVAL = 1800
ERROR_DELAY = 60
MAX_RETRIES = 3

# ✅ FIX 1: تحقق من التوكن
if not TOKEN or TOKEN.strip() == "":
    print("❌ TELEGRAM_TOKEN missing — stop bot")
    sys.exit(1)

if not CHAT_ID:
    print("❌ TELEGRAM_CHAT_ID missing")
    sys.exit(1)

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# ================= POSTS =================
POSTS = [
    {
        "title": "🔥 عرض اليوم",
        "link": "https://s.click.aliexpress.com/e/_PUT_REAL_LINK1"
    },
    {
        "title": "💡 منتج رهيب",
        "link": "https://s.click.aliexpress.com/e/_PUT_REAL_LINK2"
    },
    {
        "title": "🎯 لا تفوت هذا",
        "link": "https://s.click.aliexpress.com/e/_PUT_REAL_LINK3"
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

        data = res.json()

        if not data.get("ok"):
            log.error(f"❌ Telegram error: {data}")
            return False

        return True

    except Exception as e:
        log.error(f"❌ Request error: {e}")
        return False


# ================= RETRY =================
def send_with_retry(message):
    for attempt in range(1, MAX_RETRIES + 1):
        log.info(f"📤 Attempt {attempt}")

        if send_message(message):
            log.info("✅ Message sent")
            return True

        time.sleep(5)

    log.error("❌ All retries failed")
    return False


# ================= MAIN =================
def main():
    log.info("🚀 Bot started")

    last_post = None  # ✅ FIX 3: منع التكرار

    while True:
        try:
            post = random.choice(POSTS)

            # 🔁 منع نفس المنشور
            while post == last_post:
                post = random.choice(POSTS)

            # ❌ منع روابط وهمية
            if "xxx" in post["link"]:
                log.warning("⚠️ Placeholder link detected — skipping")
                time.sleep(ERROR_DELAY)
                continue

            message = f"{post['title']}\n\n🛒 {post['link']}"

            success = send_with_retry(message)

            if success:
                last_post = post  # حفظ آخر منشور

            else:
                time.sleep(ERROR_DELAY)
                continue

            log.info("⏳ Waiting next post...")
            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(f"🔥 Loop error: {e}")
            time.sleep(ERROR_DELAY)


# ================= RUN =================
if __name__ == "__main__":
    main()
