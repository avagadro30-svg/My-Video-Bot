import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def download_send(chat_id, url):
    # Eng yangi blokirovkalarni aylanib o'tish sozlamalari
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        # YouTube blokirovkasidan qochish uchun 'cookies' ishlatish kerak, 
        # lekin renderda bu qiyin, shuning uchun 'ios' clientidan foydalanamiz
        'extractor_args': {'youtube': {'player_client': ['ios']}}, 
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open('song.mp3', 'rb') as f:
            bot.send_audio(chat_id, f, caption="Tayyor! ✅ @avagadro30_bot")
        os.remove('song.mp3')
    except Exception as e:
        raise e

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! YouTube linkini yuboring, men uni MP3 qilib beraman! 🎵")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    url = message.text
    if "youtube.com" in url or "youtu.be" in url:
        msg = bot.send_message(message.chat.id, "Yuklashni boshladim... (Bu 1 daqiqagacha vaqt olishi mumkin) ⏳")
        try:
            download_send(message.chat.id, url)
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.send_message(message.chat.id, f"Xatolik: YouTube bu videoni blokladi. Boshqa link yuboring. ❌")
            print(f"Error: {e}")
    else:
        bot.send_message(message.chat.id, "Iltimos, faqat YouTube linkini yuboring! 📎")

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    bot.polling(none_stop=True)
