import os
import telebot
import requests
from threading import Thread
from flask import Flask

# --- 1. GIỮ BOT SỐNG ---
app = Flask('')
@app.route('/')
def home():
    return "Bot đang hoạt động!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    Thread(target=run).start()

# --- 2. CẤU HÌNH ---
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

def get_exchange_rate():
    """Lấy tỉ giá USD/VND thực tế từ API công khai"""
    try:
        # Sử dụng API tỉ giá hối đoái công khai
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        return float(data['rates']['VND'])
    except:
        return 25500  # Giá dự phòng nếu API gặp sự cố

def get_binance_price(symbol="BTCUSDT"):
    """Lấy giá BTC từ Binance với cơ chế thử lại"""
    urls = [
        f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api1.binance.com/api/v3/ticker/price?symbol={symbol}",
        f"https://api2.binance.com/api/v3/ticker/price?symbol={symbol}"
    ]
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return float(response.json()['price'])
        except:
            continue
    return None

# --- 3. XỬ LÝ ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    current_rate = get_exchange_rate()
    text = (
        f"Chào **{message.from_user.first_name}**!\n"
        f"Nhập số tiền VND để quy đổi sang USDT.\n\n"
        f"📌 Tỉ giá thị trường hiện tại: `1 USDT ~ {current_rate:,.0f} VND`"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_conversion(message):
    raw_text = "".join(filter(str.isdigit, message.text))
    
    if raw_text:
        vnd_amount = float(raw_text)
        # Lấy tỉ giá mới nhất mỗi khi người dùng nhắn tin
        real_rate = get_exchange_rate()
        usdt_result = vnd_amount / real_rate
        
        btc_price = get_binance_price("BTCUSDT")
        btc_display = f"${btc_price:,.2f}" if btc_price else "Đang cập nhật..."
        
        response = (
            f"✅ **Kết quả quy đổi:**\n"
            f"💵 VND: `{vnd_amount:,.0f}`\n"
            f"➡️ USDT: **{usdt_result:.2f}**\n\n"
            f"📊 **Thông tin thị trường:**\n"
            f"Tỉ giá áp dụng: `1 USD = {real_rate:,.0f} VND`\n"
            f"Giá BTC: `{btc_display}`"
        )
        bot.reply_to(message, response, parse_mode='Markdown')
    else:
        bot.reply_to(message, "⚠️ Vui lòng chỉ nhập số tiền.")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
