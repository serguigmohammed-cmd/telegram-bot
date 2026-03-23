import pandas as pd
import requests
import time
import random
import hashlib
import os
import logging

# ================= CONFIG =================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
APP_SECRET = os.getenv("APP_SECRET")

APP_KEY = "530184"
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 1800
MAX_RETRIES = 3

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# ================= LOAD FILE =================
df = pd.read_csv("products.csv")

# ================= SMART FILTER =================
def filter_products(df):
    try:
        return df[
            (df["Orders"] > 1000) &
            (df["Rating"] >= 4.5) &
            (df["Price"] > 3) &
            (df["Price"] < 50)
        ]
    except:
        return df

df = filter_products(df)

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    s = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(s.encode()).hexdigest().upper()

# ================= AFFILIATE =================
def generate_affiliate_link(product_url):
    try:
        url = "https://api-sg.aliexpress.com/rest"

        params = {
            "method": "aliexpress.affiliate.link.generate",
            "app_key": APP_KEY,
            "timestamp": str(int(time.time() * 1000)),
            "format": "json",
            "v": "2.0",
            "source_values": product_url,
            "tracking_id": TRACKING_ID
        }

        params["sign"] = generate_sign(params)

        res = requests.get(url, params=params, timeout=30)
        data = res.json()

        link = (
            data.get("aliexpress_affiliate_link_generate_response", {})
            .get("resp_result", {})
            .get("result", {})
            .get("promotion_links", {})
            .get("promotion_link", [{}])[0]
            .get("promotion_link")
        )

        return link if link else product_url

    except:
        return product_url

# ================= CAPTION =================
def build_caption(title, price, orders, link):
    return f"""🔥 منتج ترند في المغرب 🇲🇦

📦 {title[:60]}

💰 فقط {price}$
📈 +{orders} طلب

⚠️ العرض محدود!

🚚 شحن سريع

🛒 اطلب الآن 👇
{link}
"""

# ================= TELEGRAM =================
def send(msg):
    for _ in range(MAX_RETRIES):
        try:
            res = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": msg},
                timeout=20
            )

            if res.json().get("ok"):
                return True
        except:
            pass

        time.sleep(5)

    return False

# ================= MAIN =================
def main():
    log.info("🚀 PRO BOT STARTED")

    used = set()

    while True:
        try:
            product = df.sample(1).iloc[0]

            pid = product.get("ProductId")
            if pid in used:
                continue

            title = str(product.get("Product Title", ""))
            price = product.get("Price", "")
            orders = product.get("Orders", "")

            url = product.get("Product URL")
            if not url:
                continue

            link = generate_affiliate_link(url)

            msg = build_caption(title, price, orders, link)

            if send(msg):
                log.info("✅ Posted")
                used.add(pid)

                if len(used) > 100:
                    used.pop()

            time.sleep(POST_INTERVAL)

        except Exception as e:
            log.error(e)
            time.sleep(60)

# ================= RUN =================
main()
