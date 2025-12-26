import sys
import subprocess

# تثبيت المكتبة إذا غير موجودة
try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-telegram-bot==20.7"])
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


TOKEN = "8523433966:AAH8PI2gOTuT_PSB7ehxrGAqi1xjjMZdrvU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بيك!\nالبوت شغال ويرد على /start 🚀"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("🤖 Bot is running...")
app.run_polling()
