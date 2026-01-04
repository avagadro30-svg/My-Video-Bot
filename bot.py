import os
import telebot
import yt_dlp
from telebot import types
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
    # YouTube blokirovkasidan qochish uchun sozlamalar
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_check_certificate': True,
        'noproxy': True,  # Proxy muammosini hal qilish uchun
        'add_header': [
            'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    with open('song.mp3', 'rb') as f:
        bot.send_audio(chat_id, f, caption="Tayyor! ✅")
    os.remove('song.mp3')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! YouTube linkini yuboring, men uni MP3 qilib beraman! 🎵")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    url = message.text
    if "youtube.com" in url or "youtu.be" in url:
        bot.send_message(message.chat.id, "Yuklashni boshladim... ⏳")
        try:
            download_send(message.chat.id, url)
        except Exception as e:
            bot.send_message(message.chat.id, f"Xatolik yuz berdi: {str(e)[:50]}... ❌")
    else:
        bot.send_message(message.chat.id, "Iltimos, faqat YouTube linkini yuboring! 📎")

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)
