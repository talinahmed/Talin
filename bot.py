from flask import Flask, request
import telebot
import os
from openai import OpenAI

# تحميل التوكنات من المتغيرات البيئية
BOT_TOKEN = os.environ.get('BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# تهيئة البوت وعميل الذكاء الاصطناعي
bot = telebot.TeleBot(BOT_TOKEN)
ai_client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

# استقبال التحديثات من Telegram
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def receive_update():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

# تسجيل الـ Webhook عند زيارة الرابط الأساسي
@app.route('/', methods=['GET'])
def set_webhook():
    bot.remove_webhook()
    webhook_url = f"https://talin-lf6y.onrender.com/{BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)
    return '✅ Webhook تم تسجيله بنجاح!', 200

# أوامر البوت
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 أهلاً بيك في البوت! اسألني بأي وقت باستخدام /ask")

@bot.message_handler(commands=['ask'])
def ask_ai(message):
    question = message.text.split('/ask')[1].strip()
    if not question:
        bot.reply_to(message, "⚠️ اكتب سؤالك بعد /ask")
        return
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"❌ حصل خطأ: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
