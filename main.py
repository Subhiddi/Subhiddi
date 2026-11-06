import os
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from google import genai

TOKEN = os.environ["BOT_TOKEN"]
AI_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=AI_KEY)


class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"DonoBot is alive!")

def start_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Health).serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Салом! 👋 Ман ДоноБот ҳастам.\n"
        "Саволатро навис, ман ҷавоб медиҳам! 🤖"
    )


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=f"Ҷавобро ба забони тоҷикӣ деҳ: {question}"
        )
        await update.message.reply_text(response.text or "Ҷавоб пайдо нашуд.")
    except Exception:
        await update.message.reply_text(
            "Ҳоло ҷавоб дода натавонистам. Баъдтар кӯшиш кун."
        )


def start_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
    app.run_polling()


if __name__ == "__main__":
    threading.Thread(target=start_bot, daemon=True).start()
    start_server()
