from http.server import BaseHTTPRequestHandler
from flask import Flask, request, jsonify
import json
import os
import re
from telegram.asyncio import Bot
import asyncio

bot_token = os.environ.get("YOUR_BOT_TOKEN")
chat_id = int(os.environ.get("YOUR_CHAT_ID"))
bot = Bot(token=bot_token)

def translate_text(text):
    API_KEY = os.environ.get("YOUR_DEEPL_KEY")
    params = {
        "auth_key": API_KEY,
        "text": text,
        "source_lang": 'RU',
        "target_lang": 'EN'
    }
    
    request = requests.post("https://api-free.deepl.com/v2/translate", data=params)
    return request.json()["translations"][0]["text"] if request.status_code == 200 else "translation failed"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        if "message" in data and "text" in data["message"]:
            message_text = data["message"]["text"]
            matches = re.findall(r'"([^"]*)"', message_text)
            
            if matches:
                translated_text = translate_text(matches[0])
                try:
                    asyncio.run(bot.send_message(
                        chat_id=chat_id,
                        text=f"translation: {translated_text}"
                    ))
                    response = {"status": "Message sent", "translated_text": translated_text}
                except Exception as e:
                    response = {"status": "Failed to send message", "error": str(e)}
            else:
                response = {"status": "No message found"}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
