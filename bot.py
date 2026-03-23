import pandas as pd
import requests
import time
import random
import os
import logging
import sys
from datetime import datetime

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAX_RETRIES = 3
ERROR_DELAY = 60

POST_HOURS = [12, 18, 21]  # أوقات النشر (المغرب)

# ================= VALIDATION =================
if not TOKEN or TOKEN.strip() == "":
    print("❌ TELEGRAM_TOKEN missing")
    sys.exit(1)

if not CHAT_ID or CHAT_ID.strip() == "":
    print("❌ TELEGRAM_CHAT_ID missing")
    sys.exit(1)

# ================= LOG =================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
log = logging.getLogger()

# ================= LOAD CSV =================
try:
    df = pd.read_csv("products.csv")
except Exception as e:
    log.error(f"CSV error: {e}")
    sys.exit(1)

# ================= SMART FILTER =================
def pick_product():
    for _ in range(20):
        product = df.sample(1).iloc[0]

        title = str(product.get("Product Title", "")).strip()
        link = product.get("Promotion Link") or product.get("Product URL")
        image = product.get("Image URL")

        if not title or not link or not image:
            continue

        if "xxx" in str(link).lower():
            continue

        return title[:80], link.strip(), image

    return None, None, None


# ================= AI CAPTION =================
def generate_caption(title, link):
    hooks = [
        "🔥 عرض اليوم!",
        "🚀 ترند الآن!",
        "💥 تخفيض قوي!",
        "😱 فرصة لا تعوض!",
        "🛒 الأفضل حالياً!"
    ]

    ctas = [
        "اطلب الآن قبل نفاذ الكمية 👇",
        "سارع قبل انتهاء العرض ⏳",
        "اضغط وشوف العرض الآن 🔥",
        "لا تفوّت الفرصة 👇"
    ]

    return f"""{random.choice(hooks)} 🇲🇦

📦 {title}

{random.choice(ctas)}
{link}
"""


# ================= TELEGRAM =================
def send_photo(photo, caption):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={
                "chat_id": CHAT_ID,
                "photo": photo,
                "caption": caption
            },
            timeout=20
        )

        data = res.json()

        if not data.get("ok"):
            if data.get("error_code") == 429:
                retry = data.get("parameters", {}).get("retry_after", 30)
                return False, retry

            log.error(data)
            return False, None

        return True, None

    except Exception as e:
        log.error(e)
        return False, None


# ================= RETRY =================
def send_with_retry(photo, caption):
    for i in range(MAX_RETRIES):
        success, retry = send_photo(photo, caption)

        if success:
            return True

        time.sleep(retry if retry else 5)

    return False


# ================= SCHEDULER =================
def wait_for_next_post():
    while True:
        now = datetime.now()
        if now.hour in POST_HOURS and now.minute == 0:
            return
        time.sleep(30)


# ================= MAIN =================
def main():
    log.info("🚀 Advanced BOT Started")

    used_links = set()

    while True:
        try:
            wait_for_next_post()

            title, link, image = pick_product()

            if not link or link in used_links:
                continue

            caption = generate_caption(title, link)

            if send_with_retry(image, caption):
                used_links.add(link)
                log.info("✅ Posted")

            time.sleep(60)

        except Exception as e:
            log.error(f"Error: {e}")
            time.sleep(ERROR_DELAY)


# ================= RUN =================
if __name__ == "__main__":
    main()
