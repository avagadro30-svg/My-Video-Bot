import os
import telebot
import yt_dlp
from telebot import types
from youtubesearchpython import VideosSearch
from flask import Flask # Render uchun kerak
from threading import Thread # Bot va Veb-server birga ishlashi uchun

# 1. Botingiz tokeni
TOKEN = '8555165776:AAEmC7plkWLizvZRglQa4XzWG6hyC34QFt0'
bot = telebot.TeleBot(TOKEN)

# 2. Render uchun kichik veb-server (Bot o'chib qolmasligi uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# 3. Yuklash funksiyasi
def download_send(chat_id, url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'nocheckcertificate': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    with open('song.mp3', 'rb') as f:
        bot.send_audio(chat_id, f, caption="Muvaffaqiyatli yuklandi! ✅")
    os.remove('song.mp3')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Ism yozing (masalan: Shahzoda) yoki YouTube link yuboring! 🎵")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text
    if "http" in text:
        bot.send_message(message.chat.id, "Link qabul qilindi... ⏳")
        try:
            download_send(message.chat.id, text)
        except:
            bot.send_message(message.chat.id, "Yuklashda xato bo'ldi. ❌")
    else:
        msg = bot.send_message(message.chat.id, f"🔎 '{text}' qidirilmoqda...")
        try:
            search = VideosSearch(text, limit = 1)
            results = search.result()['result']
            if results:
                url = results[0]['link']
                download_send(message.chat.id, url)
                bot.delete_message(message.chat.id, msg.message_id)
            else:
                bot.edit_message_text("Topilmadi. 😕", message.chat.id, msg.message_id)
        except:
            bot.edit_message_text("Qidiruvda xatolik. ❌", message.chat.id, msg.message_id)

# 4. Botni va Veb-serverni parallel ishga tushirish
if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)
