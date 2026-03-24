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
if not TOKEN:
    print("❌ TELEGRAM_TOKEN missing")
    sys.exit(1)

if not CHAT_ID:
    print("❌ TELEGRAM_CHAT_ID missing")
    sys.exit(1)

# ================= LOG =================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
log = logging.getLogger()

# ================= LOAD CSV =================
df = pd.read_csv("products.csv")

# ================= TRACKING =================
performance = {}

# ================= AFFILIATE =================
link_cache = {}

def generate_affiliate_link(url):
    try:
        api_url = "https://api-sg.aliexpress.com/sync"

        params = {
            "app_key": APP_KEY,
            "method": "aliexpress.affiliate.link.generate",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "format": "json",
            "v": "2.0",
            "sign_method": "md5",
            "promotion_link_type": "0",
            "source_values": url,
            "tracking_id": TRACKING_ID
        }

        sign_str = APP_SECRET + "".join(f"{k}{params[k]}" for k in sorted(params)) + APP_SECRET
        params["sign"] = hashlib.md5(sign_str.encode()).hexdigest().upper()

        res = requests.get(api_url, params=params, timeout=20)
        data = res.json()

        return data.get("aliexpress_affiliate_link_generate_response", {}) \
                   .get("resp_result", {}) \
                   .get("result", {}) \
                   .get("promotion_links", [{}])[0] \
                   .get("promotion_link")

    except:
        return None


def get_affiliate(url):
    if url in link_cache:
        return link_cache[url]

    aff = generate_affiliate_link(url)
    if aff:
        link_cache[url] = aff

    return aff

# ================= SMART SCORE =================
def score_product(p):
    try:
        sales = float(p.get("Sales180Day", 0))
        rating = float(p.get("Positive Feedback", 0))
        price = float(p.get("Discount Price", 1))

        return (sales * 0.5) + (rating * 20) - price
    except:
        return 0

# ================= PICK PRODUCT =================
def pick_product():
    df["score"] = df.apply(score_product, axis=1)
    top = df.sort_values("score", ascending=False).head(50)

    for _ in range(20):
        p = top.sample(1).iloc[0]

        title = str(p.get("Product Desc", "")).strip()
        raw_link = p.get("Product URL")
        image = p.get("Image Url")

        if not title or not raw_link or not image:
            continue

        aff = get_affiliate(raw_link)
        if not aff:
            continue

        if aff in performance:
            performance[aff] += 1
            if performance[aff] > 2:
                continue
        else:
            performance[aff] = 1

        return title[:80], aff, image

    return None, None, None

# ================= CAPTION =================
def generate_caption(title, link):
    hooks = [
        "🔥 خصم قوي اليوم!",
        "🚀 منتج عليه إقبال كبير!",
        "💥 عرض لا يفوّت!",
        "😱 الناس كاملين كيشريوه!",
        "🛒 ترند حالياً!"
    ]

    return f"""{random.choice(hooks)} 🇲🇦

📦 {title}

⚠️ الكمية محدودة!

🛒 اطلب الآن 👇
{link}
"""

# ================= TELEGRAM =================
def send_photo(photo, caption):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
            data={"chat_id": CHAT_ID, "photo": photo, "caption": caption},
            timeout=20
        )

        data = res.json()

        if not data.get("ok"):
            if data.get("error_code") == 429:
                return False, data["parameters"]["retry_after"]

            return False, None

        return True, None

    except:
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
def wait_for_time():
    while True:
        now = datetime.now()
        if now.hour in POST_HOURS and now.minute == 0:
            return
        time.sleep(30)

# ================= MAIN =================
def main():
    log.info("💰 MONEY BOT STARTED")

    while True:
        try:
            wait_for_time()

            title, link, image = pick_product()

            if not link:
                continue

            caption = generate_caption(title, link)

            if send_with_retry(image, caption):
                log.info(f"💸 Posted: {title}")

            time.sleep(60)

        except Exception as e:
            log.error(e)
            time.sleep(ERROR_DELAY)

# ================= RUN =================
if __name__ == "__main__":
    main()
