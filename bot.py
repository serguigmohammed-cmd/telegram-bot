import pandas as pd
import requests
import time
import random
import os
import logging
import sys
import hashlib
from datetime import datetime

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

APP_KEY = os.getenv("ALI_APP_KEY")
APP_SECRET = os.getenv("ALI_APP_SECRET")
TRACKING_ID = os.getenv("ALI_TRACKING_ID", "default")

MAX_RETRIES = 3
ERROR_DELAY = 60

POST_HOURS = [12, 18, 21]

# ================= VALIDATION =================
if not TOKEN or TOKEN.strip() == "":
    print("❌ TELEGRAM_TOKEN missing")
    sys.exit(1)

if not CHAT_ID or CHAT_ID.strip() == "":
    print("❌ TELEGRAM_CHAT_ID missing")
    sys.exit(1)

if not APP_KEY or not APP_SECRET:
    print("❌ AliExpress API keys missing")
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

# ================= AFFILIATE CACHE =================
link_cache = {}

def generate_affiliate_link(original_url):
    try:
        url = "https://api-sg.aliexpress.com/sync"

        params = {
            "app_key": APP_KEY,
            "method": "aliexpress.affiliate.link.generate",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "format": "json",
            "v": "2.0",
            "sign_method": "md5",
            "promotion_link_type": "0",
            "source_values": original_url,
            "tracking_id": TRACKING_ID
        }

        sign_str = APP_SECRET + "".join(f"{k}{params[k]}" for k in sorted(params)) + APP_SECRET
        sign = hashlib.md5(sign_str.encode()).hexdigest().upper()
        params["sign"] = sign

        res = requests.get(url, params=params, timeout=20)
        data = res.json()

        link = data.get("aliexpress_affiliate_link_generate_response", {}) \
                   .get("resp_result", {}) \
                   .get("result", {}) \
                   .get("promotion_links", [{}])[0] \
                   .get("promotion_link")

        return link

    except Exception as e:
        log.error(f"Affiliate error: {e}")
        return None


def get_affiliate_link(url):
    if url in link_cache:
        return link_cache[url]

    aff = generate_affiliate_link(url)

    if aff:
        link_cache[url] = aff

    return aff

# ================= SMART FILTER =================
def pick_product():
    for _ in range(30):
        product = df.sample(1).iloc[0]

        title = str(product.get("Product Desc", "")).strip()
        raw_link = product.get("Product URL")
        image = product.get("Image Url")

        if not title or not raw_link or not image:
            continue

        # 🔥 توليد affiliate link
        link = get_affiliate_link(raw_link)

        if not link:
            continue

        return title[:80], link, image

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
    for _ in range(MAX_RETRIES):
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
    log.info("🚀 PRO BOT WITH AFFILIATE STARTED")

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
                log.info("✅ Posted with affiliate link 💰")

            time.sleep(60)

        except Exception as e:
            log.error(f"Error: {e}")
            time.sleep(ERROR_DELAY)

# ================= RUN =================
if __name__ == "__main__":
    main()
