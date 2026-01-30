import os
# Lấy token từ cấu hình hệ thống thay vì dán trực tiếp
API_TOKEN = os.getenv('BOT_TOKEN')

# 2. Khởi tạo con bot
# Thêm dấu ngoặc kép bao quanh mã Token của bạn
bot = telebot.TeleBot("8546336362:AAG1z6W2mce9StJlKSl3tgLm2ngbkqpODi8")
# 3. Xử lý lệnh /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Gửi tin nhắn chào mừng kèm tên người dùng
    user_name = message.from_user.first_name
    bot.reply_to(message, f"Chào {user_name}! Mình là bot Python của bạn. Rất vui được gặp bạn!")

# 4. Xử lý khi người dùng gửi văn bản bất kỳ
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # Bot sẽ "nhại" lại những gì bạn vừa gửi
    bot.send_message(message.chat.id, f"Bạn vừa nói là: {message.text}")

# 5. Giữ cho bot luôn chạy
print("Bot đang khởi động... Hãy vào Telegram và nhắn tin cho nó!")
bot.infinity_polling()