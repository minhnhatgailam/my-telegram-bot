import os
import telebot
import requests
from threading import Thread
from flask import Flask

# --- 1. KHỞI TẠO SERVER GIẢ (GIỮ BOT LUÔN SỐNG TRÊN RENDER) ---
app = Flask('')

@app.route('/')
def home():
    # Khi Cron-job hoặc Render truy cập, bot sẽ báo vẫn đang thức
    return "Bot P2P Shorthand đang chạy 24/7!"

def run():
    # Render cấp cổng PORT ngẫu nhiên, ta cần lấy nó để mở server
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    # Chạy Flask trong một luồng (thread) riêng để không làm treo Bot
    t = Thread(target=run)
    t.start()

# --- 2. HÀM LẤY DỮ LIỆU P2P TỪ KÊNH THỨ 2 ---
def get_p2p_price(trade_type="BUY"):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    data = {
        "asset": "USDT",
        "fiat": "VND",
        "merchantCheck": False,
        "page": 1,
        "rows": 5, 
        "payTypes": [],
        "tradeType": trade_type
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            ads = res_data.get('data', [])
            if len(ads) >= 2:
                return float(ads[1]['adv']['price'])
            elif len(ads) == 1:
                return float(ads[0]['adv']['price'])
    except Exception as e:
        print(f"Lỗi gọi API Binance ({trade_type}): {e}")
    return None

# --- 3. CẤU HÌNH BOT TELEGRAM ---
API_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # ĐÃ SỬA LỖI: Thêm dấu đóng ngoặc kép và ký tự xuống dòng \n
    welcome_text = (
        f"👋 Chào **{message.from_user.first_name}**!\n\n"
        "🔹 Nhập số ví dụ: `1` = 1,000 VNĐ (Mua)\n"
        "🔹 Nhập số ví dụ: `1` = 1 USDT (Bán)\n\n"
        "⚠️ Giá được lấy từ **thương nhân thứ 2** trên sàn Binance P2P để đảm bảo tính thực tế."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_conversion(message):
    raw_text = "".join(filter(str.isdigit, message.text))
    
    if raw_text:
        try:
            val = float(raw_text)
            buy_rate = get_p2p_price("BUY")
            sell_rate = get_p2p_price("SELL")
            
            if not buy_rate or not sell_rate:
                bot.reply_to(message, "❌ Hiện không lấy được tỉ giá từ Binance, hãy thử lại sau ít giây.")
                return

            vnd_pay = val * 1000
            usdt_receive = vnd_pay / buy_rate
            usdt_sell = val
            vnd_receive = usdt_sell * sell_rate
            
            response = (
                f"📊 **KẾT QUẢ QUY ĐỔI (KÊNH 2)**\n"
                f"--- \n"
                f"🔴 **BẠN ĐI MUA (Pay VND):**\n"
                f"💰 Bỏ ra: `{vnd_pay:,.0f}đ`\n"
                f"💵 Tỉ giá: `{buy_rate:,.0f}đ`\n"
                f"📥 Nhận về: **{usdt_receive:.2f} USDT**\n\n"
                f"🟢 **BẠN ĐI BÁN (Get VND):**\n"
                f"💰 Bỏ ra: `{usdt_sell:,.0f} USDT`\n"
                f"💵 Tỉ giá: `{sell_rate:,.0f}đ`\n"
                f"📤 Nhận về: **{vnd_receive:,.0f}đ**\n"
                f"--- \n"
                f"⚖️ Chênh lệch (Spread): `{buy_rate - sell_rate:,.0f}đ`"
            )
            bot.reply_to(message, response, parse_mode='Markdown')
            
        except Exception as e:
            bot.reply_to(message, "⚠️ Có lỗi xảy ra khi tính toán. Vui lòng thử lại.")
            print(f"Lỗi xử lý tin nhắn: {e}")
    else:
        bot.reply_to(message, "⚠️ Vui lòng nhập một con số (ví dụ: 100, 500, 2000).")

# --- 4. KÍCH HOẠT ---
if __name__ == "__main__":
    keep_alive() 
    print("Bot đang khởi động...")
    bot.infinity_polling()
