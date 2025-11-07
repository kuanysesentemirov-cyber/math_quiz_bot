# bot.py
# Қазақша математика викторина боты (python-telegram-bot v20.3)
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# TOKEN-ді .env немесе Render Environment Variables ішінде TOKEN ретінде қой
TOKEN = "8454491066:AAEpz_e_jqv-vjWFgTMJDIq6vgN8hKQotoQ"

# 20 сұрақ — 5-7 сынып деңгейіне арналған (пайдаланушы тек мәтінмен жауап береді)
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

# Қолданушы деректерін сақтау (жеңіл, сервер қайта жүктелсе жоғалады)
users = {}  # user_id -> {"score": int, "q": int}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = {"score": 0, "q": 0}
    await update.message.reply_text(
        "МАТЕМАТИКА ВИКТОРИНАСЫНА ҚОШ КЕЛДІҢ!\n20 сұрақ бар. Әр сұраққа жауапты тек санмен жаз.\nБастау үшін дайын болсаң — жауапты жазыңыз."
    )
    # Бірінші сұрақты шығару
    await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {"score": 0, "q": 0}
    idx = users[user_id]["q"]
    if idx < len(questions):
        q_text = questions[idx][0]
        await update.message.reply_text(f"{idx+1}. {q_text}")
    else:
        score = users[user_id]["score"]
        await update.message.reply_text(f"Викторина аяқталды! Сенің ұпайың: {score}/{len(questions)}")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    # Егер қолданушы бастамаған болса — баста
    if user_id not in users:
        users[user_id] = {"score": 0, "q": 0}
        await update.message.reply_text("Викторина автоматты түрде басталды.")
        await ask_question(update, context)
        return

    idx = users[user_id]["q"]
    # егер викторина аяқталған болса, қайта бастау опциясы ұсыныңыз
    if idx >= len(questions):
        await update.message.reply_text("Викторина аяқталды. Қайта бастау үшін /start жазыңыз.")
        return

    correct = questions[idx][1]
    # Жауап бірдей ме (сан ретінде тексереміз)
    if text == correct:
        users[user_id]["score"] += 1
        await update.message.reply_text("✅ Дұрыс!")
    else:
        await update.message.reply_text(f"❌ Қате! Дұрысы: {correct}")

    users[user_id]["q"] += 1
    # Келесі сұрақты жібереміз (немесе нәтижені)
    if users[user_id]["q"] < len(questions):
        next_q = questions[users[user_id]["q"]][0]
        await update.message.reply_text(f"{users[user_id]['q']+1}. {next_q}")
    else:
        score = users[user_id]["score"]
        await update.message.reply_text(f"Викторина аяқталды! Сенің ұпайың: {score}/{len(questions)}\nҚайта бастау үшін /start жазыңыз.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пайдалану: /start — викторинаны бастау. Сұрақтарға жауапты тек санмен жіберіңіз.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    # Барлық мәтіндік хабарларды қабылдау (командалардан басқасын)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_msg))
    print("Бот іске қосылып жатыр...")
    app.run_polling()

if name == "main":
    main()
app.add_handler(MessageHandler(None, handle_msg))

app.run_polling()
