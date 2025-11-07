rom telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8454491066:AAEpz_e_jqv-vjWFgTMJDIq6vgN8hKQotoQ"

questions = [
    ("5 + 3 =", "8"),
    ("10 - 4 =", "6"),
    ("7 × 2 =", "14"),
    ("12 ÷ 3 =", "4")
]

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = {"score": 0, "q": 0}
    await update.message.reply_text("МАТЕМАТИКА ВИКТОРИНАСЫНА ҚОШ КЕЛДІҢ!")
    await ask(update, context)

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    q = users[user_id]["q"]
    if q < len(questions):
        await update.message.reply_text(questions[q][0])
    else:
        score = users[user_id]["score"]
        await update.message.reply_text(f"Викторина аяқталды! Ұпай: {score}/{len(questions)}")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message.text
    q = users[user_id]["q"]

    if q < len(questions) and msg == questions[q][1]:
        users[user_id]["score"] += 1
        await update.message.replyText("Дұрыс ✅")
    else:
        await update.message.reply_text("Қате ❌")

    users[user_id]["q"] += 1
    await ask(update, context)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(None, handle_msg))

app.run_polling()
