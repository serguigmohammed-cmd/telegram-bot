import requests
import time
import random
import os
import logging
import signal
import sys

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = "@orodmaroc"

POST_INTERVAL = 7200   # 2 ساعات
RETRY_DELAY = 60       # إعادة المحاولة بعد 1 دقيقة
MAX_RETRIES = 3

if not TOKEN:
    raise Exception("❌ TELEGRAM_TOKEN missing in environment")

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger()

# ================= POSTS =================
POSTS = [
    {
        "title": "🔥 منتج رهيب",
        "link": "https://s.click.aliexpress.com/e/_abc123"
    },
    {
        "title": "💡 عرض قوي",
        "link": "https://s.click.aliexpress.com/e/_def456"
    },
    {
        "title": "🎯 لا تفوت هذا المنتج",
        "link": "https://s.click.aliexpress.com/e/_ghi789"
    }
]

# ================= SHUTDOWN FLAG =================
running = True

def shutdown_handler(signum, frame):
    global running
    log.info("🛑 Shutting down gracefully...")
    running = False

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# ================= TELEGRAM =================
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    try:
        res = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": text
        }, timeout=20)

        if res.status_code != 200:
            log.error(f"❌ HTTP {res.status_code}: {res.text}")
            return False

        data = res.json()
        return data.get("ok", False)

    except Exception as e:
        log.error(f"❌ Request error: {e}")
        return False

# ================= RETRY SYSTEM =================
def send_with_retry(message):
    for attempt in range(1, MAX_RETRIES + 1):
        log.info(f"📤 Attempt {attempt}")

        success = send_message(message)

        if success:
            log.info("✅ Message sent successfully")
            return True

        log.warning(f"⚠️ Failed attempt {attempt}")
        time.sleep(RETRY_DELAY)

    log.error("❌ All retries failed")
    return False

# ================= MAIN LOOP =================
def main():
    log.info("🚀 Bot started")

    while running:
        try:
            post = random.choice(POSTS)

            message = f"{post['title']}\n\n🛒 {post['link']}"

            success = send_with_retry(message)

            if not success:
                log.warning("⚠️ Will retry soon (not waiting 2h)")
                time.sleep(RETRY_DELAY)
                continue

            log.info("⏳ Waiting for next post...")
            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(f"🔥 Loop error: {e}")
            time.sleep(RETRY_DELAY)

    log.info("👋 Bot stopped cleanly")

# ================= RUN =================
if __name__ == "__main__":
    main()
