import os
import telebot
import requests
from threading import Thread
from flask import Flask

# --- PHẦN 1: GIỮ BOT SỐNG (FLASK) ---
app = Flask('')
@app.route('/')
def home():
    return "Bot quy đổi đang chạy!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- PHẦN 2: CẤU HÌNH BOT & TỈ GIÁ ---
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Giả sử tỉ giá 1 USDT = 25,500 VND (Bạn có thể điều chỉnh số này)
VND_PER_USDT = 25500 

def get_binance_price(symbol="BTCUSDT"):
    """Lấy giá coin từ Binance API"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url)
        data = response.json()
        return float(data['price'])
    except:
        return None

# --- PHẦN 3: XỬ LÝ TIN NHẮN ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"Xin chào **{message.from_user.first_name}**!\n\n"
        "Tôi là bot quy đổi VND sang USDT.\n"
        "Hãy gửi một số tiền (bot sẽ tự hiểu là **nghìn đồng**).\n\n"
        "Ví dụ: Gửi `200` để quy đổi 200.000đ"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def convert_money(message):
    try:
        # Lấy số tiền người dùng nhập (ví dụ 200)
        amount_k = float(message.text)
        vnd_amount = amount_k * 1000 # Đổi ra đồng (200.000)
        
        # Tính toán quy đổi
        usdt_result = vnd_amount / VND_PER_USDT
        
        # Lấy thêm giá BTC từ Binance để làm tin nhắn thêm chuyên nghiệp
        btc_price = get_binance_price("BTCUSDT")
        
        response = (
            f"💰 **Kết quả quy đổi:**\n"
            f"Số tiền: {vnd_amount:,.0f} VNĐ\n"
            f"Thành: **{usdt_result:.2f} USDT**\n"
            f"_(Tỉ giá áp dụng: 1 USDT = {VND_PER_USDT:,}đ)_\n\n"
            f"📊 **Thông tin Binance:**\n"
            f"Giá BTC hiện tại: ${btc_price:,.2f}"
        )
        
        bot.reply_to(message, response, parse_mode='Markdown')
        
    except ValueError:
        bot.reply_to(message, "⚠️ Vui lòng chỉ nhập số (ví dụ: 100, 200, 500).")

# --- PHẦN 4: KHỞI CHẠY ---
if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
