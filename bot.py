import os
import telebot
import requests
from threading import Thread
from flask import Flask

# --- 1. GIỮ BOT SỐNG ---
app = Flask('')
@app.route('/')
def home(): return "Bot P2P đang chạy!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    Thread(target=run).start()

# --- 2. HÀM LẤY GIÁ P2P TỪ BINANCE ---
def get_p2p_price(trade_type="BUY"):
    """
    trade_type="BUY" lấy giá ở tab 'Mua' (bạn mua USDT)
    trade_type="SELL" lấy giá ở tab 'Bán' (bạn bán USDT)
    """
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    # Cấu hình dữ liệu gửi đi (Payload)
    data = {
        "asset": "USDT",
        "fiat": "VND",
        "merchantCheck": False,
        "page": 1,
        "rows": 5, # Lấy 5 người đầu tiên để tính trung bình cho chính xác
        "payTypes": [],
        "publisherType": None,
        "tradeType": trade_type
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            ads = response.json().get('data', [])
            if ads:
                # Lấy giá của người đăng tin đầu tiên (giá tốt nhất)
                return float(ads[0]['adv']['price'])
    except Exception as e:
        print(f"Lỗi P2P {trade_type}: {e}")
    return None

# --- 3. CẤU HÌNH BOT ---
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Chào Bạn! Nhập số tiền VND để tính toán theo giá P2P thực tế.")

@bot.message_handler(func=lambda message: True)
def handle_p2p_conversion(message):
    raw_text = "".join(filter(str.isdigit, message.text))
    
    if raw_text:
        vnd_amount = float(raw_text)
        
        # Lấy giá P2P thực tế thay vì dùng số cố định
        buy_price = get_p2p_rate("BUY")   # Giá bạn phải trả khi mua
        sell_price = get_p2p_rate("SELL") # Giá bạn nhận được khi bán
        
        if not buy_price or not sell_price:
            bot.reply_to(message, "⚠️ Không lấy được dữ liệu từ Binance P2P, vui lòng thử lại sau.")
            return

        # Tính toán quy đổi
        usdt_to_buy = vnd_amount / buy_price
        vnd_from_sell = (vnd_amount / 1000) * sell_price # Nếu bạn coi số nhập vào là số lượng USDT

        response = (
            f"🚀 **TỈ GIÁ P2P BINANCE (VND/USDT)**\n\n"
            f"🔴 **Bạn Mua (Pay VND):**\n"
            f"  - Tỉ giá: `{buy_price:,.0f}đ`\n"
            f"  - `{vnd_amount:,.0f}đ` -> **{usdt_to_buy:.2f} USDT**\n\n"
            f"🟢 **Bạn Bán (Get VND):**\n"
            f"  - Tỉ giá: `{sell_price:,.0f}đ`\n"
            f"  - Với `{vnd_amount:,.0f}` USDT -> Nhận **{vnd_amount * sell_price:,.0f}đ**\n\n"
            f"⚖️ **Chênh lệch (Spread):** `{buy_price - sell_price:,.0f}đ`"
        )
        bot.reply_to(message, response, parse_mode='Markdown')
    else:
        bot.reply_to(message, "⚠️ Vui lòng chỉ nhập số tiền.")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
