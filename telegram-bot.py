import os
import re
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# .envファイルを読み込む
load_dotenv()
bot_token = os.getenv("YOUR_BOT_TOKEN")
chat_id = os.getenv("YOUR_CHAT_ID")

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

# メッセージ受信時に呼ばれる関数
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text

    # "" で囲まれたテキストを検索する正規表現パターン
    matches = re.findall(r'"([^"]*)"', message_text)
    if matches:
        # 最初の一致する部分だけ翻訳（複数ある場合は適宜処理を追加）
        translated_text = translate_text(matches[0])
        await update.message.reply_text(f"translation: {translated_text}")
    # else:
    #     await update.message.reply_text("のメッセージが見つかりませんでした。")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("翻訳したい文章を \"\" で囲んで送信してください。")

if __name__ == "__main__":
    application = ApplicationBuilder().token(bot_token).build()

    # コマンドハンドラー
    application.add_handler(CommandHandler("start", start))

    # メッセージハンドラー
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ボットを開始
    application.run_polling()
