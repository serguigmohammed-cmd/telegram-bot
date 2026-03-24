import requests
import time
import os
import sys
import random

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POST_INTERVAL = 7200   # 2 hours
RETRY_DELAY = 60       # retry after failure (1 min)

# ================= VALIDATION =================
if not TOKEN or TOKEN.strip() == "":
    print("❌ ERROR: TELEGRAM_TOKEN missing — bot stopped")
    sys.exit(1)

if not CHAT_ID or CHAT_ID.strip() == "":
    print("❌ ERROR: TELEGRAM_CHAT_ID missing — bot stopped")
    sys.exit(1)

# ================= POSTS =================
posts = [
    "🔥 عرض رهيب اليوم!\nhttps://s.click.aliexpress.com/e/xxx",
    "💥 تخفيض كبير لفترة محدودة!\nhttps://s.click.aliexpress.com/e/xxx",
    "🚀 منتج مطلوب بشدة!\nhttps://s.click.aliexpress.com/e/xxx"
]

last_post = None

# ================= TELEGRAM =================
def send_message(text):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )

        if res.status_code != 200:
            print(f"❌ HTTP Error: {res.status_code}")
            return False

        data = res.json()

        if not data.get("ok"):
            print(f"❌ Telegram error: {data}")
            return False

        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


# ================= MAIN =================
def main():
    global last_post

    print("🚀 Bot started (Improved Version)")

    while True:
        try:
            # 🔁 منع التكرار
            available_posts = [p for p in posts if p != last_post]

            if not available_posts:
                available_posts = posts

            message = random.choice(available_posts)

            # ⚠️ منع الروابط الوهمية
            if "xxx" in message:
                print("⚠️ Placeholder link detected — skipping")
                time.sleep(30)
                continue

            success = send_message(message)

            if success:
                print("✅ Message sent")
                last_post = message
                time.sleep(POST_INTERVAL)
            else:
                print("⚠️ Failed — retrying soon")
                time.sleep(RETRY_DELAY)

        except Exception as e:
            print(f"🔥 Error: {e}")
            time.sleep(RETRY_DELAY)


# ================= RUN =================
if __name__ == "__main__":
    main()
