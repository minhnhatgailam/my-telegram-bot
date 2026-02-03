import os
import telebot
import requests
from threading import Thread
from flask import Flask

# --- 1. GIỮ BOT SỐNG ---
app = Flask('')
@app.route('/')
def home(): return "Bot P2P Pro đang chạy!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    Thread(target=run).start()

# --- 2. HÀM LẤY GIÁ P2P (LẤY KÊNH THỨ 2) ---
def get_p2p_price(trade_type="BUY"):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    data = {
        "asset": "USDT", "fiat": "VND", "merchantCheck": False,
        "page": 1, "rows": 5, "payTypes": [], "tradeType": trade_type
    }
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            ads = res_data.get('data', [])
            # Kiểm tra nếu có ít nhất 2 người bán/mua
            if len(ads) >= 2:
                # ads[1] chính là người đứng thứ 2 trong danh sách
                return float(ads[1]['adv']['price'])
            elif len(ads) == 1:
                # Nếu chỉ có duy nhất 1 người thì đành lấy người thứ 1
                return float(ads[0]['adv']['price'])
    except Exception as e:
        print(f"Lỗi P2P {trade_type}: {e}")
    return None

# --- 3. CẤU HÌNH BOT ---
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🏦 **Bot Tỉ Giá P2P Binance**\n\nNhập số tiền VND để tính toán quy đổi theo giá thực tế từ **kênh thứ 2** trên sàn.", parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_conversion(message):
    raw_text = "".join(filter(str.isdigit, message.text))
    
    if raw_text:
        try:
            vnd_amount = float(raw_text)
            
            # Lấy giá từ kênh thứ 2
            buy_price = get_p2p_price("BUY")   # Tỉ giá khi bạn đi mua USDT
            sell_price = get_p2p_price("SELL") # Tỉ giá khi bạn đi bán USDT
            
            if not buy_price or not sell_price:
                bot.reply_to(message, "❌ Không thể kết nối dữ liệu P2P. Thử lại sau.")
                return

            usdt_receive = vnd_amount / buy_price
            
            # Giao diện phản hồi mới (Scannable & Clear)
            response = (
                f"📊 **KẾT QUẢ QUY ĐỔI P2P**\n"
                f"--- \n"
                f"💰 **Số tiền bạn nhập:** `{vnd_amount:,.0f} VND`\n\n"
                f"🔴 **Nếu bạn đi MUA USDT:**\n"
                f"👉 Tỉ giá (Kênh 2): `{buy_price:,.0f} đ/USDT`\n"
                f"📥 Bạn sẽ nhận: **{usdt_receive:.2f} USDT**\n\n"
                f"🟢 **Nếu bạn đi BÁN USDT:**\n"
                f"👉 Tỉ giá (Kênh 2): `{sell_price:,.0f} đ/USDT`\n"
                f"📤 Bạn sẽ nhận: **{vnd_amount * sell_price:,.0f} VND**\n"
                f"--- \n"
                f"⚖️ **Chênh lệch sàn:** `{buy_price - sell_price:,.0f} đ`"
            )
            bot.reply_to(message, response, parse_mode='Markdown')
            
        except Exception as e:
            bot.reply_to(message, "❌ Lỗi tính toán. Vui lòng nhập số hợp lệ.")
    else:
        bot.reply_to(message, "⚠️ Vui lòng nhập số tiền (Ví dụ: 5000000)")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
