import os
import telebot
import requests
from threading import Thread
from flask import Flask

# --- PHẦN 1: GIỮ BOT SỐNG (FLASK) ---
app = Flask('')
@app.route('/')
def home():
    return "Bot Quy Đổi đang chạy!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- PHẦN 2: CẤU HÌNH BOT & TỈ GIÁ ---
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Tỉ giá USDT/VND (Bạn có thể sửa số này theo ý muốn)
VND_PER_USDT = 25500 

def get_binance_price(symbol="BTCUSDT"):
    """Lấy giá từ sàn Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"Lỗi lấy giá Binance: {e}")
        return None

# --- PHẦN 3: XỬ LÝ QUY ĐỔI ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "Xin chào! Tôi là Bot Quy Đổi VND -> USDT.\n\n"
        "🔹 **Cách dùng**: Nhập chính xác số tiền VND bạn muốn đổi.\n"
        "🔹 **Ví dụ**: Nhập `200000` để tính cho 200.000đ.\n"
        f"_(Tỉ giá hiện tại: 1 USDT = {VND_PER_USDT:,}đ)_"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_conversion(message):
    # Kiểm tra xem tin nhắn có phải là số không
    text_input = message.text.replace(',', '').replace('.', '') # Loại bỏ dấu phẩy/chấm nếu có
    
    if text_input.isdigit():
        vnd_amount = float(text_input)
        
        # 1. Tính toán kết quả quy đổi
        usdt_result = vnd_amount / VND_PER_USDT
        
        # 2. Lấy thêm giá BTC từ Binance để minh họa dữ liệu sàn
        btc_price = get_binance_price("BTCUSDT")
        
        # 3. Trả lời kết quả
        response = (
            f"✅ **Kết quả quy đổi:**\n"
            f"💵 Số tiền: `{vnd_amount:,.0f}` VNĐ\n"
            f"➡️ Nhận được: **{usdt_result:.2f} USDT**\n\n"
            f"📊 **Thông tin sàn Binance:**\n"
            f"Giá BTC hiện tại: `${btc_price:,.2f}`"
        )
        bot.reply_to(message, response, parse_mode='Markdown')
    else:
        # Nếu không phải là số, bot sẽ báo lỗi thay vì nhại lại
        bot.reply_to(message, "⚠️ Vui lòng chỉ nhập số tiền (Ví dụ: 200000)")

# --- PHẦN 4: KHỞI CHẠY ---
if __name__ == "__main__":
    keep_alive()
    print("Bot đang lắng nghe...")
    bot.infinity_polling()
