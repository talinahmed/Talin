import telebot
from openai import OpenAI
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# تهيئة التوكنات
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# تهيئة البوت وكلينت OpenAI
bot = telebot.TeleBot(BOT_TOKEN)
ai_client = OpenAI(api_key=OPENAI_API_KEY)

# قائمة الأوامر الرئيسية
COMMANDS = {
    'start': 'بدء استخدام البوت',
    'help': 'عرض جميع الأوامر المتاحة',
    'ask': 'اسأل أي سؤال وسأجيبك بالذكاء الاصطناعي',
    'time': 'عرض الوقت والتاريخ الحالي',
    'about': 'معلومات عن البوت والمطور',
    'settings': 'إعدادات البوت'
}

# معالجة أمر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    welcome_msg = f"""
    🎉 *مرحباً {user.first_name}!* 🎉

    أنا بوتك الذكي الشخصي، مصمم لمساعدتك في مختلف المهام. 
    يمكنك استخدامي للاستفسارات، الأسئلة، أو حتى التذكيرات.

    📅 *التاريخ اليوم:* {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

    استخدم الأمر /help لرؤية جميع الإمكانيات المتاحة.
    """
    
    # إنشاء أزرار إنلاين
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("الذكاء الاصطناعي", callback_data="ai_help"),
        InlineKeyboardButton("المساعدة", callback_data="general_help")
    )
    
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=markup)

# معالجة أمر /help
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = "📜 *قائمة الأوامر المتاحة:*\n\n"
    for cmd, desc in COMMANDS.items():
        help_text += f"*/{cmd}* - {desc}\n"
    
    help_text += "\nيمكنك أيضاً إرسال أي سؤال مباشرة وسأحاول الإجابة عليه."
    bot.reply_to(message, help_text, parse_mode="Markdown")

# معالجة أمر /ask
@bot.message_handler(commands=['ask'])
def handle_ai_request(message):
    question = message.text.replace('/ask', '').strip()
    if not question:
        bot.reply_to(message, "⚠️ الرجاء كتابة سؤالك بعد الأمر /ask")
        return
    
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}],
            temperature=0.7
        )
        answer = response.choices[0].message.content
        bot.reply_to(message, f"🤖 *الإجابة:*\n\n{answer}", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء معالجة سؤالك: {str(e)}")

# معالجة أمر /time
@bot.message_handler(commands=['time'])
def send_time(message):
    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    bot.reply_to(message, f"🕒 الوقت الحالي: {time_str}")

# معالجة أمر /about
@bot.message_handler(commands=['about'])
def about_bot(message):
    about_text = """
    *ℹ️ معلومات عن البوت:*
    
    - الإصدار: 1.0
    - المطور: أنت!
    - التقنية: Python + Telegram Bot API
    - الذكاء الاصطناعي: OpenAI GPT-3.5-turbo
    
    هذا البوت تم تطويره كمساعد شخصي ذكي.
    """
    bot.reply_to(message, about_text, parse_mode="Markdown")

# معالجة الرسائل النصية العادية
@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    if message.text.startswith('/'):
        bot.reply_to(message, "⚠️ الأمر غير معروف. استخدم /help لرؤية الأوامر المتاحة")
    else:
        handle_ai_request(message)  # معالجة كرسالة AI عادية

# معالجة ضغط أزرار الإنلاين
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "ai_help":
        bot.answer_callback_query(call.id, "اكتب سؤالك مباشرة أو استخدم /ask متبوعاً بسؤالك")
    elif call.data == "general_help":
        show_help(call.message)

# تشغيل البوت
if __name__ == "__main__":
    print("✅ البوت يعمل...")
    bot.infinity_polling()
