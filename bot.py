from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import sqlite3
from datetime import datetime
import os

# ТОКЕН-ді дәл мына жерге қой
TOKEN = "8586918388:AAH6_sdfyO7V1B26odqZVnbucnwna8JrmJA"

DB_PATH = "stats.db"

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

# ---- SQLite DB helpers ----
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        total_attempts INTEGER DEFAULT 0,
        total_correct INTEGER DEFAULT 0,
        games_played INTEGER DEFAULT 0,
        best_score INTEGER DEFAULT 0,
        last_score INTEGER DEFAULT 0,
        updated_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def update_stats(user_id: int, username: str, first_name: str, score: int, total_questions: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    # егер жазба жоқ болса – қосу
    cur.execute("SELECT total_attempts, total_correct, games_played, best_score FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row is None:
        cur.execute("""
            INSERT INTO users (user_id, username, first_name, total_attempts, total_correct, games_played, best_score, last_score, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, first_name, total_questions, score, 1, score, score, now))
    else:
        total_attempts, total_correct, games_played, best_score = row
        total_attempts += total_questions
        total_correct += score
        games_played += 1
        best_score = max(best_score, score)
        cur.execute("""
            UPDATE users
            SET username = ?, first_name = ?, total_attempts = ?, total_correct = ?, games_played = ?, best_score = ?, last_score = ?, updated_at = ?
            WHERE user_id = ?
        """, (username, first_name, total_attempts, total_correct, games_played, best_score, score, now, user_id))
    conn.commit()
    conn.close()

def get_user_stats(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT username, first_name, total_attempts, total_correct, games_played, best_score, last_score FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_leaderboard(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT username, first_name, best_score, total_correct, games_played FROM users ORDER BY best_score DESC, total_correct DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---- end DB helpers ----

# флеш-память (қолданушы сессиясы)
# Render сияқты ортада файл жүйесі тұрақты — sqlite файл сақталады
# user session data бот ішінде ғана (context.user_data) сақталады
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["score"] = 0
    context.user_data["q_index"] = 0
    await update.message.reply_text("Математика викторинасына қош келдің! 🚀\nБарлығы 20 сұрақ. /mystats — сенің статистикаң, /leaderboard — үздіктер.")
    await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):

index = context.user_data.get("q_index", 0)
    if index >= len(questions):
        score = context.user_data.get("score", 0)
        await update.message.reply_text(f"✅ Викторина аяқталды!\nСенің нәтижең: {score}/{len(questions)}")
        # Статистикаға сақтау
        user = update.effective_user
        username = user.username or ""
        first_name = user.first_name or ""
        update_stats(user.id, username, first_name, score, len(questions))
        return

    question, answer = questions[index]
    context.user_data["answer"] = answer
    await update.message.reply_text(f"Сұрақ {index+1}/{len(questions)}:\n{question}")

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip()
    correct_answer = context.user_data.get("answer", None)

    if correct_answer is None:
        await update.message.reply_text("Алдымен /start бас 😅")
        return

    # Тексеру (сандық салыстыру)
    try:
        # кейбір жауаптар int, сондықтан салыстырамыз
        if str(int(user_answer)) == str(correct_answer):
            context.user_data["score"] = context.user_data.get("score", 0) + 1
            await update.message.reply_text("✅ Дұрыс!")
        else:
            await update.message.reply_text(f"❌ Қате! Дұрыс жауап: {correct_answer}")
    except Exception:
        # егер қолданушы сан емес нәрсе жазса
        if user_answer == str(correct_answer):
            context.user_data["score"] = context.user_data.get("score", 0) + 1
            await update.message.reply_text("✅ Дұрыс!")
        else:
            await update.message.reply_text(f"❌ Қате! Дұрыс жауап: {correct_answer}")

    context.user_data["q_index"] = context.user_data.get("q_index", 0) + 1
    # Келесі сұрақ
    await ask_question(update, context)

# Пайдаланушы өз статистикасын көру
async def mystats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    row = get_user_stats(user.id)
    if not row:
        await update.message.reply_text("Сіздің статистикаңыз әлі жоқ. Алдымен /start арқылы викторина бастаңыз.")
        return
    username, first_name, total_attempts, total_correct, games_played, best_score, last_score = row
    text = (
        f"📊 Сіздің статистикаңыз:\n"
        f"Пайдаланушы: @{username or ''} {first_name or ''}\n"
        f"Ойындар: {games_played}\n"
        f"Барлық сұрақтар: {total_attempts}\n"
        f"Дұрыс жауаптар: {total_correct}\n"
        f"Жақсы рекорд (best): {best_score}/{len(questions)}\n"
        f"Соңғы нәтиже: {last_score}/{len(questions)}"
    )
    await update.message.reply_text(text)

# Лидерборд — жоғарғы 10
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = get_leaderboard(10)
    if not rows:
        await update.message.reply_text("Әзірше статистика жоқ.")
        return
    text = "🏆 Leaderboard (TOP 10):\n"
    i = 1
    for username, first_name, best_score, total_correct, games_played in rows:
        name = f"@{username}" if username else first_name or "Пайдаланушы"
        text += f"{i}) {name} — best: {best_score}, total_correct: {total_correct}, games: {games_played}\n"
        i += 1
    await update.message.reply_text(text)

# /resetstats — әкімшіге арналған (қосқың келсе)
async def resetstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Бұл командаға қорғаныс қосқалың — тек сен (админ) пайдалана алады.
    owner_id = None  # <-- егер керек болса өз Telegram ID-ңды осында қой
    if owner_id and update.effective_user.id != owner_id:
        await update.message.reply_text("Сіз бұны қолдана алмайсыз.")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    await update.message.reply_text("Статистика өшірілді.")

def main():
    # DB және файл орындарын дайындау
    if not os.path.exists(DB_PATH):
        init_db()

app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mystats", mystats))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("resetstats", resetstats))  # міндетті емес
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), check_answer))
    print("BOT STARTED...")
    app.run_polling()

if __name__ == "__main__":
    main()
