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

# ✅ تحقق من التوكن
if not TOKEN or TOKEN.strip() == "":
    print("❌ TELEGRAM_TOKEN missing — STOP")
    sys.exit(1)

if not CHAT_ID or CHAT_ID.strip() == "":
    print("❌ TELEGRAM_CHAT_ID missing — STOP")
    sys.exit(1)

# ================= LOG =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger()

# ================= LOAD CSV =================
try:
    df = pd.read_csv("products.csv")

    # ✅ تحقق من الأعمدة
    required_columns = ["Product Title", "Promotion Link", "Product URL"]
    for col in required_columns:
        if col not in df.columns:
            log.error(f"❌ Missing column in CSV: {col}")
            sys.exit(1)

except Exception as e:
    log.error(f"❌ Failed to load CSV: {e}")
    sys.exit(1)

# ================= TELEGRAM =================
def send_message(text):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "disable_web_page_preview": False
            },
            timeout=20
        )

        if res.status_code != 200:
            log.error(f"❌ HTTP Error: {res.status_code} - {res.text}")
            return False

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

    used_links = []
    last_link = None

    while True:
        try:
            # 🔁 اختيار منتج عشوائي
            product = df.sample(1).iloc[0]

            title = str(product.get("Product Title", "")).strip()[:70]

            # 🔗 اختيار الرابط الصحيح
            link = product.get("Promotion Link") or product.get("Product URL")

            if not link or str(link).strip() == "":
                continue

            link = str(link).strip()

            # ❌ منع روابط وهمية
            if "xxx" in link.lower():
                log.warning("⚠️ Fake link detected — skip")
                continue

            # ❌ منع التكرار المباشر
            if link == last_link:
                continue

            # ❌ منع التكرار العام
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
                last_link = link
                used_links.append(link)

                # ✅ حافظ على الحجم (FIFO بدل pop عشوائي)
                if len(used_links) > 100:
                    used_links.pop(0)

            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(f"🔥 Error: {e}")
            time.sleep(ERROR_DELAY)


# ================= RUN =================
if __name__ == "__main__":
    main()
