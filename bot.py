import pandas as pd
import requests
import time
import random
import os
import logging
import sys

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POST_INTERVAL = 1800
ERROR_DELAY = 60
MAX_RETRIES = 3

# ✅ FIX: تحقق من التوكن
if not TOKEN or TOKEN.strip() == "":
    print("❌ TELEGRAM_TOKEN missing — STOP")
    sys.exit(1)

if not CHAT_ID:
    print("❌ TELEGRAM_CHAT_ID missing — STOP")
    sys.exit(1)

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# ================= LOAD CSV =================
df = pd.read_csv("products.csv")

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
            log.info("✅ Sent")
            return True

        time.sleep(5)

    log.error("❌ Failed after retries")
    return False


# ================= MAIN =================
def main():
    log.info("🚀 BOT STARTED")

    used_links = set()

    while True:
        try:
            product = df.sample(1).iloc[0]

            title = str(product.get("Product Title", ""))[:70]

            # 🔗 اختيار الرابط الصحيح
            link = product.get("Promotion Link") or product.get("Product URL")

            if not link:
                continue

            # ❌ منع روابط xxx
            if "xxx" in link:
                log.warning("⚠️ Fake link detected — skip")
                continue

            # ❌ منع التكرار
            if link in used_links:
                continue

            message = f"""🔥 منتج ترند اليوم 🇲🇦

📦 {title}

⚠️ العرض محدود!

🛒 اطلب الآن 👇
{link}
"""

            success = send_with_retry(message)

            if success:
                used_links.add(link)

                # حافظ على الحجم
                if len(used_links) > 100:
                    used_links.pop()

            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(f"🔥 Error: {e}")
            time.sleep(ERROR_DELAY)


# ================= RUN =================
if __name__ == "__main__":
    main()
