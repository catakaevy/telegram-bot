import os
import re
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# .envファイルを読み込む
load_dotenv()
bot_token = os.getenv("YOUR_BOT_TOKEN")
api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
chat_id = os.getenv("YOUR_CHAT_ID")

app = Flask(__name__)

def translate_text(text):
    # DeepL API キーを取得
    API_KEY = os.getenv("YOUR_DEEPL_KEY")
    params = {
        "auth_key": API_KEY,
        "text": text,
        "source_lang": 'RU',
        "target_lang": 'EN'
    }

    # DeepL APIへのリクエスト
    response = requests.post("https://api-free.deepl.com/v2/translate", data=params)
    if response.status_code == 200:
        result = response.json()
        return result["translations"][0]["text"]
    else:
        return "translation failed"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    # メッセージが存在するかを確認
    if "message" in data and "text" in data["message"]:
        message_text = data["message"]["text"]

        # 正規表現で "" で囲まれたテキストを検索
        matches = re.findall(r'"([^"]*)"', message_text)
        if matches:
            translated_text = translate_text(matches[0])

            # Telegram APIに翻訳結果を送信
            send_message(data["message"]["chat"]["id"], translated_text)
            return jsonify({"status": "Message sent"})
    
    return jsonify({"status": "No valid message found"})

def send_message(chat_id, text):
    params = {
        "chat_id": chat_id,
        "text": f"translation: {text}"
    }
    requests.post(api_url, data=params)

@app.route("/start", methods=["GET"])
def start():
    return "翻訳したい文章を \"\" で囲んで送信してください。"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
