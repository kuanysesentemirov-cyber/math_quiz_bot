from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# БОТ ТОКЕН ДӘЛ ОСЫ ЖЕРГЕ ЖАЗ
TOKEN = "8454491066:AAEpz_e_jqv-vjWFgTMJDIq6vgN8hKQotoQ"

# 20 сұрақ (5-6-7 сыныпқа арналған)
questions = [
    ("5 + 7 = ?", 12),
    ("9 × 3 = ?", 27),
    ("15 - 8 = ?", 7),
    ("6 × 6 = ?", 36),
    ("28 ÷ 4 = ?", 7),
    ("49 ÷ 7 = ?", 7),
    ("12 + 14 = ?", 26),
    ("8 × 7 = ?", 56),
    ("120 ÷ 10 = ?", 12),
    ("25 × 3 = ?", 75),
    ("35 - 19 = ?", 16),
    ("15 + 45 = ?", 60),
    ("100 ÷ 20 = ?", 5),
    ("9 × 8 = ?", 72),
    ("7 × 7 = ?", 49),
    ("18 + 17 = ?", 35),
    ("63 ÷ 9 = ?", 7),
    ("2³ = ?", 8),
    ("3² = ?", 9),
    ("10² = ?", 100)
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["score"] = 0
    context.user_data["q_index"] = 0
    await update.message.reply_text("Математика викторинасына қош келдің! 🚀")
    await ask_question(update, context)


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data["q_index"]

    if index >= len(questions):
        score = context.user_data["score"]
        await update.message.reply_text(f"✅ Викторина аяқталды!\nСенің нәтижең: {score}/20")
        return

    question, answer = questions[index]
    context.user_data["answer"] = answer
    await update.message.reply_text(f"Сұрақ {index+1}/20:\n{question}")


async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip()

    correct_answer = context.user_data.get("answer", None)

    if correct_answer is None:
        await update.message.reply_text("Алдымен /start бас 😅")
        return

    if user_answer == str(correct_answer):
        context.user_data["score"] += 1
        await update.message.reply_text("✅ Дұрыс!")
    else:
        await update.message.reply_text(f"❌ Қате! Дұрыс жауап: {correct_answer}")

    context.user_data["q_index"] += 1
    await ask_question(update, context)


if name == "main":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, check_answer))
    app.run_polling()
