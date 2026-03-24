import requests
import time
import os
import sys
import random

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POST_INTERVAL = 7200  # 2 hours

# ================= VALIDATION =================
if not TOKEN or TOKEN.strip() == "":
    print("❌ ERROR: TELEGRAM_TOKEN is missing — bot stopped")
    sys.exit(1)

if not CHAT_ID or CHAT_ID.strip() == "":
    print("❌ ERROR: TELEGRAM_CHAT_ID is missing — bot stopped")
    sys.exit(1)

# ================= POSTS =================
posts = [
    "🔥 عرض رهيب اليوم!\nhttps://s.click.aliexpress.com/e/xxx",
    "💥 تخفيض كبير لفترة محدودة!\nhttps://s.click.aliexpress.com/e/xxx",
    "🚀 منتج مطلوب بشدة!\nhttps://s.click.aliexpress.com/e/xxx"
]

# ================= PREPARE POSTS =================
# 🔥 Shuffle once and cycle (no repetition until full cycle ends)
random.shuffle(posts)
post_index = 0

# ================= TELEGRAM =================
def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

        res = requests.post(
            url,
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

    print("🚀 Bot started")

    while True:
        try:
            # 🔁 Cycle through posts
            message = posts[post_index]

            # ⚠️ Warning for fake links
            if "xxx" in message:
                print("⚠️ WARNING: Placeholder link detected!")

            success = send_message(message)

            if success:
                print(f"✅ Sent post #{post_index + 1}")

                # Move to next post
                post_index += 1

                # Restart cycle
                if post_index >= len(posts):
                    random.shuffle(posts)
                    post_index = 0

            time.sleep(POST_INTERVAL)

        except Exception as e:
            print(f"🔥 Error: {e}")
            time.sleep(60)


# ================= RUN =================
if __name__ == "__main__":
    main()
