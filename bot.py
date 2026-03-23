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

# ✅ Token check
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
except Exception as e:
    log.error(f"❌ CSV load failed: {e}")
    sys.exit(1)

# ================= TELEGRAM =================
def send_message(text):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text
            },
            timeout=20
        )

        # ✅ HTTP error
        if res.status_code != 200:
            log.error(f"❌ HTTP {res.status_code}: {res.text}")
            return False, None

        data = res.json()

        # ✅ Handle Telegram error
        if not data.get("ok"):
            error_code = data.get("error_code")

            # 🔥 429 RATE LIMIT
            if error_code == 429:
                retry_after = data.get("parameters", {}).get("retry_after", 30)
                log.warning(f"⏳ Rate limited. Retry after {retry_after}s")
                return False, retry_after

            log.error(f"❌ Telegram error: {data}")
            return False, None

        return True, None

    except Exception as e:
        log.error(f"❌ Request error: {e}")
        return False, None


# ================= RETRY =================
def send_with_retry(message):
    for attempt in range(1, MAX_RETRIES + 1):
        log.info(f"📤 Attempt {attempt}")

        success, retry_after = send_message(message)

        if success:
            log.info("✅ Sent")
            return True

        # 🔥 إذا كان Rate Limit
        if retry_after:
            log.info(f"⏳ Waiting {retry_after}s بسبب 429")
            time.sleep(retry_after)
        else:
            time.sleep(5)

    log.error("❌ Failed after retries")
    return False


# ================= MAIN =================
def main():
    log.info("🚀 BOT STARTED")

    last_link = None

    while True:
        try:
            product = df.sample(1).iloc[0]

            title = str(product.get("Product Title", "")).strip()[:70]
            link = product.get("Promotion Link") or product.get("Product URL")

            if not link:
                continue

            link = str(link).strip()

            # ❌ Skip fake links
            if "xxx" in link.lower():
                log.warning("⚠️ Fake link — skipped")
                continue

            # ❌ منع التكرار المباشر
            if link == last_link:
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

            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(f"🔥 Error: {e}")
            time.sleep(ERROR_DELAY)


# ================= RUN =================
if __name__ == "__main__":
    main()
