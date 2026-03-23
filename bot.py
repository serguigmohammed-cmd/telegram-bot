import requests
import time
import random
import hashlib
import os
import logging

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

APP_KEY = "530184"
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 1800
ERROR_DELAY = 60
MAX_RETRIES = 3

# ✅ FIX 1: تحقق من التوكن
if not TOKEN or TOKEN.strip() == "":
    raise Exception("❌ TELEGRAM_TOKEN is missing or empty")

if not APP_SECRET:
    raise Exception("❌ APP_SECRET missing")

if not CHAT_ID:
    raise Exception("❌ TELEGRAM_CHAT_ID missing")

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# ================= POSTS (استعمل روابط حقيقية) =================
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

        if res.status_code != 200:
            log.error(f"❌ HTTP {res.status_code}: {res.text}")
            return False

        data = res.json()
        return data.get("ok", False)

    except Exception as e:
        log.error(f"❌ Request error: {e}")
        return False


# ✅ FIX 3: Retry system
def send_with_retry(message):
    for attempt in range(1, MAX_RETRIES + 1):
        log.info(f"📤 Attempt {attempt}")

        success = send_message(message)

        if success:
            log.info("✅ Message sent")
            return True

        log.warning("⚠️ Failed attempt, retrying...")
        time.sleep(5)

    log.error("❌ All retries failed")
    return False


# ================= MAIN =================
def main():
    log.info("🚀 Bot started")

    while True:
        try:
            post = random.choice(POSTS)

            # ⚠️ منع إرسال روابط خاطئة
            if "xxx" in post["link"]:
                log.warning("⚠️ Placeholder link detected, skipping")
                time.sleep(ERROR_DELAY)
                continue

            message = f"{post['title']}\n\n🛒 {post['link']}"

            success = send_with_retry(message)

            if not success:
                log.warning("⚠️ Will retry soon")
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
