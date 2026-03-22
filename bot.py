import requests
import time
import random
import hashlib
import os

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")
CHAT_ID = "@orodmaroc"

APP_KEY = "530184"
APP_SECRET = os.getenv("APP_SECRET")
TRACKING_ID = "orodmaroc"

POST_INTERVAL = 600

if not TOKEN:
    raise Exception("❌ TOKEN not found in environment variables")

print("🚀 BOT STARTED SECURELY")

# ================= SIGN =================
def generate_sign(params):
    sorted_params = dict(sorted(params.items()))
    sign_str = APP_SECRET + "".join(f"{k}{v}" for k, v in sorted_params.items()) + APP_SECRET
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

# ================= TELEGRAM =================
def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    try:
        img = requests.get(photo_url, timeout=10)

        if img.status_code != 200:
            print("❌ Image download failed:", img.status_code)
            return False

        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML"
            },
            files={"photo": ("image.jpg", img.content)},
            timeout=15
        )

        # ✅ CHECK RESPONSE
        if response.status_code != 200:
            print("❌ Telegram HTTP Error:", response.status_code)
            print(response.text)
            return False

        data = response.json()

        if not data.get("ok"):
            print("❌ Telegram API رفض الرسالة:")
            print(data)
            return False

        print("✅ Message sent successfully")
        return True

    except Exception as e:
        print("❌ Telegram Exception:", e)
        return False

# ================= AFFILIATE LINK =================
def generate_link(product_url):
    if not product_url:
        return ""

    url = "https://api-sg.aliexpress.com/rest"

    params = {
        "method": "aliexpress.affiliate.link.generate",
        "app_key": APP_KEY,
        "timestamp": str(int(time.time() * 1000)),
        "format": "json",
        "v": "2.0",
        "promotion_link_type": "0",
        "source_values": product_url,
        "tracking_id": TRACKING_ID
    }

    params["sign"] = generate_sign(params)

    try:
        res = requests.get(url, params=params, timeout=15).json()

        link = res["aliexpress_affiliate_link_generate_response"]["resp_result"]["result"]["promotion_links"]["promotion_link"][0]["promotion_link"]

        return link

    except Exception as e:
        print("❌ Affiliate link error:", e)
        return product_url

# ================= SIMPLE TEST =================
def test_telegram():
    print("🧪 Testing Telegram...")
    return send_photo(
        "https://ae01.alicdn.com/kf/Sample.jpg",
        "✅ Bot is working!"
    )

# ================= MAIN =================
def main():
    if not test_telegram():
        print("❌ Telegram test failed — check token or permissions")
        return

    while True:
        print("🔄 Running...")

        # (هنا تحط logic ديال products ديالك)

        time.sleep(POST_INTERVAL)

# ================= RUN =================
if __name__ == "__main__":
    main()
