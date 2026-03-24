import requests
import time
import os
import sys
import random
import signal

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POST_INTERVAL = 7200  # 2 hours
running = True

# ================= VALIDATION =================
if not TOKEN or TOKEN.strip() == "":
    print("❌ ERROR: TELEGRAM_TOKEN missing — stopping")
    sys.exit(1)

if not CHAT_ID or CHAT_ID.strip() == "":
    print("❌ ERROR: TELEGRAM_CHAT_ID missing — stopping")
    sys.exit(1)

# ================= SIGNAL HANDLER =================
def shutdown_handler(signum, frame):
    global running
    print("🛑 Shutdown signal received — stopping bot cleanly...")
    running = False

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# ================= POSTS =================
posts = [
    "🔥 عرض رهيب اليوم!\nhttps://s.click.aliexpress.com/e/xxx",
    "💥 تخفيض كبير لفترة محدودة!\nhttps://s.click.aliexpress.com/e/xxx",
    "🚀 منتج مطلوب بشدة!\nhttps://s.click.aliexpress.com/e/xxx"
]

# 🔁 Shuffle once
random.shuffle(posts)
post_index = 0

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
    global post_index

    print("🚀 Bot started (Stable Mode)")

    while running:
        try:
            message = posts[post_index]

            # ⚠️ منع الروابط الوهمية
            if "xxx" in message:
                print("⚠️ Placeholder link detected — skipping post")
                post_index = (post_index + 1) % len(posts)
                continue

            success = send_message(message)

            if success:
                print(f"✅ Sent post #{post_index + 1}")

                post_index += 1

                if post_index >= len(posts):
                    random.shuffle(posts)
                    post_index = 0

            time.sleep(POST_INTERVAL)

        except Exception as e:
            print(f"🔥 Error: {e}")
            time.sleep(60)

    print("👋 Bot stopped cleanly")


# ================= RUN =================
if __name__ == "__main__":
    main()
