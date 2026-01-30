import os
import telebot
from threading import Thread
from flask import Flask

# --- PHẦN 1: TẠO SERVER GIẢ ĐỂ GIỮ BOT LUÔN SỐNG TRÊN RENDER ---
app = Flask('')

@app.route('/')
def home():
    # Khi Render kiểm tra cổng mạng, nó sẽ thấy chữ này và biết bot vẫn sống
    return "Bot đang chạy 24/7!"

def run():
    # Render cấp một cổng (Port) ngẫu nhiên, ta cần lấy nó ra
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    # Chạy server Flask trong một luồng riêng để không làm gián đoạn bot
    t = Thread(target=run)
    t.start()

# --- PHẦN 2: CẤU HÌNH BOT TELEGRAM ---
# Lấy Token từ tab Environment trên Render (không dán trực tiếp mã vào đây)
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Chào Nhật Minh! Bot đã online 24/7 trên Render rồi nhé!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Bot nhận được: {message.text}")

# --- PHẦN 3: KHỞI CHẠY ---
if __name__ == "__main__":
    keep_alive() # Kích hoạt server giả
    print("Bot đang khởi động...")
    bot.infinity_polling() # Giữ bot luôn lắng nghe tin nhắn
