import os
import re
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from telegram import Bot
from telegram.error import TelegramError

# .envファイルの読み込み
load_dotenv()

# .envファイルからbotのトークンとchat_idを取得
bot_token = os.getenv("YOUR_BOT_TOKEN")
chat_id = os.getenv("YOUR_CHAT_ID")

if not bot_token:
    raise ValueError("Bot token not found in environment variables")
if not chat_id:
    raise ValueError("Chat ID not found in environment variables")

# 文字列型のchat_idを整数型に変換
chat_id = int(chat_id)

# Telegram Botのインスタンスを作成
bot = Bot(token=bot_token)

# Flaskのアプリケーションのセットアップ
app = Flask(__name__)

def translate_text(text):
    # NOTE: put API KEY
    API_KEY = os.getenv("YOUR_DEEPL_KEY")
    txt = text

    params = {
                "auth_key": API_KEY,
                "text": txt,
                "source_lang": 'RU',
                "target_lang": 'EN'
            }

    request = requests.post("https://api-free.deepl.com/v2/translate", data=params)
    if request.status_code == 200:
        result = request.json()
        message = result["translations"][0]["text"]
        return message
    else:
        return "translation failed"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        message_text = data["message"]["text"]
        
        matches = re.findall(r'"([^"]*)"', message_text)
        if matches:
            translated_text = translate_text(matches[0])
            if not chat_id:
                return jsonify({"status": "Chat ID not configured"}), 500
            try:
                # Telegramにメッセージを送信
                result = bot.send_message(
                    chat_id=chat_id, 
                    text=f"translation: {translated_text}"
                )
                print(result)
                return jsonify({"status": "Message sent", "translated_text": translated_text})
            except TelegramError as e:
                print(f"Error sending message: {e}")
                return jsonify({"status": "Failed to send message", "error": str(e)}), 500

    return jsonify({"status": "No message found"}), 400

if __name__ == "__main__":
    # Flaskのアプリケーションを開始
    app.run(host="0.0.0.0", port=5000, debug=True)
