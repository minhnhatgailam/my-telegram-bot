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

# --- 2. HÀM LẤY GIÁ P2P (Đã sửa lỗi tên hàm) ---
def get_p2p_price(trade_type="BUY"):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    data = {
        "asset": "USDT", "fiat": "VND", "merchantCheck": False,
        "page": 1, "rows": 3, "payTypes": [], "tradeType": trade_type
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get('data'):
                return float(res_data['data'][0]['adv']['price'])
    except Exception as e:
        print(f"Lỗi lấy giá {trade_type}: {e}")
    return None

# --- 3. CẤU HÌNH BOT ---
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Chào bạn! Nhập số tiền VND để tính toán theo giá P2P thực tế.")

@bot.message_handler(func=lambda message: True)
def handle_conversion(message):
    raw_text = "".join(filter(str.isdigit, message.text))
    
    if raw_text:
        try:
            vnd_amount = float(raw_text)
            
            # Gọi đúng tên hàm get_p2p_price
            buy_price = get_p2p_price("BUY")
            sell_price = get_p2p_price("SELL")
            
            if not buy_price or not sell_price:
                bot.reply_to(message, "⚠️ Không thể kết nối tới Binance P2P. Vui lòng thử lại sau vài giây.")
                return

            usdt_to_buy = vnd_amount / buy_price
            
            response = (
                f"🚀 **TỈ GIÁ P2P BINANCE (VND/USDT)**\n\n"
                f"🔴 **Bạn Mua (Trả VND):**\n"
                f"  - Tỉ giá: `{buy_price:,.0f}đ`\n"
                f"  - `{vnd_amount:,.0f}đ` -> **{usdt_to_buy:.2f} USDT**\n\n"
                f"🟢 **Bạn Bán (Nhận VND):**\n"
                f"  - Tỉ giá: `{sell_price:,.0f}đ`\n"
                f"  - `{vnd_amount:,.0f} USDT` -> **{vnd_amount * sell_price:,.0f}đ**\n\n"
                f"⚖️ **Chênh lệch:** `{buy_price - sell_price:,.0f}đ`"
            )
            bot.reply_to(message, response, parse_mode='Markdown')
        except Exception as e:
            bot.reply_to(message, f"❌ Có lỗi xảy ra trong quá trình tính toán.")
            print(f"Lỗi xử lý: {e}")
    else:
        bot.reply_to(message, "⚠️ Vui lòng chỉ nhập số tiền (Ví dụ: 1000000)")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
