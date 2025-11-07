from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8454491066:AAGMR9yDX6hQUtgrQQM-6Gaz8pvJ0MWcNOo"

questions = [
    ("5 + 3 =", "8"),
    ("10 - 4 =", "6"),
    ("7 × 2 =", "14"),
    ("12 ÷ 3 =", "4"),
    ("9 + 6 =", "15"),
    ("8 × 3 =", "24"),
    ("15 - 7 =", "8"),
    ("18 ÷ 2 =", "9"),
    ("6 × 6 =", "36"),
    ("14 + 5 =", "19"),
    ("20 - 9 =", "11"),
    ("21 ÷ 7 =", "3"),
    ("11 + 11 =", "22"),
    ("4 × 5 =", "20"),
    ("30 - 12 =", "18"),
    ("9 × 5 =", "45"),
    ("16 ÷ 4 =", "4"),
    ("13 + 6 =", "19"),
    ("7 + 8 =", "15"),
    ("25 - 7 =", "18"),
]

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = {"score": 0, "q": 0}
    await update.message.reply_text(
        "МАТЕМАТИКА ВИКТОРИНАСЫ!\nБарлығы 20 сұрақ.\nЖауапты санмен жазыңыз.\nАлғашқы сұрақ:"
    )
    await ask(update, context)

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    q = users[user_id]["q"]
    if q < len(questions):
        await update.message.reply_text(f"{q+1}. {questions[q][0]}")
    else:
        score = users[user_id]["score"]
        await update.message.reply_text(f"✅ Викторина аяқталды!\nҰпай: {score}/{len(questions)}")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text.strip()

    if user_id not in users:
        users[user_id] = {"score": 0, "q": 0}

    q = users[user_id]["q"]

    if q < len(questions) and msg == questions[q][1]:
        users[user_id]["score"] += 1
        await update.message.reply_text("✅ Дұрыс!")
    else:
        await update.message.reply_text(f"❌ Қате! Дұрысы: {questions[q][1]}")

    users[user_id]["q"] += 1
    await ask(update, context)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))

    print("BOT STARTED...")
    app.run_polling()

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, check_answer))
    app.run_polling()
    main()
