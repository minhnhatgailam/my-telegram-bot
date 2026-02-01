import os
import telebot
import requests
from threading import Thread
from flask import Flask

# --- 1. GIỮ BOT SỐNG ---
app = Flask('')
@app.route('/')
def home():
    return "Bot đang chạy!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    Thread(target=run).start()

# --- 2. CẤU HÌNH ---
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
VND_PER_USDT = 25500 

def get_binance_price(symbol="BTCUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        return float(response.json()['price'])
    except:
        return "Không khả dụng"

# --- 3. XỬ LÝ QUY ĐỔI ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Chào bạn! Nhập số tiền VND để đổi sang USDT (Ví dụ: 200000).")

@bot.message_handler(func=lambda message: True)
def handle_conversion(message):
    # Loại bỏ các ký tự không phải số
    raw_text = "".join(filter(str.isdigit, message.text))
    
    if raw_text:
        vnd_amount = float(raw_text)
        usdt_result = vnd_amount / VND_PER_USDT
        btc_price = get_binance_price("BTCUSDT")
        
        # Xử lý hiển thị giá BTC để tránh lỗi định dạng
        btc_display = f"${btc_price:,.2f}" if isinstance(btc_price, float) else btc_price
        
        response = (
            f"✅ **Kết quả:**\n"
            f"💵 VND: `{vnd_amount:,.0f}`\n"
            f"➡️ USDT: **{usdt_result:.2f}**\n\n"
            f"📊 **Binance Info:**\n"
            f"BTC: `{btc_display}`"
        )
        bot.reply_to(message, response, parse_mode='Markdown')
    else:
        bot.reply_to(message, "⚠️ Vui lòng chỉ nhập số tiền (Ví dụ: 200000)")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
