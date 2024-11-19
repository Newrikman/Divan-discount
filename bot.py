
import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

# Подключаем базу данных SQLite
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Создаем таблицу для хранения данных о пользователях
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")
conn.commit()

# Регистрация пользователя в базе данных
def register_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

# Команда /start
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    register_user(user_id)
    update.message.reply_text("Добро пожаловать в систему! Используйте /balance для проверки баланса.")

# Команда /balance
def balance(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance = result[0]
        update.message.reply_text(f"Ваш текущий баланс: {balance} баллов.")
    else:
        update.message.reply_text("Вы не зарегистрированы. Введите /start для регистрации.")

# Команда /addpoints
def add_points(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        points = int(context.args[0])
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (points, user_id))
        conn.commit()
        update.message.reply_text(f"Вам начислено {points} баллов!")
    except (IndexError, ValueError):
        update.message.reply_text("Укажите количество баллов после команды. Пример: /addpoints 10")

# Команда /redeem
def redeem(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    try:
        points = int(context.args[0])
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result and result[0] >= points:
            cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (points, user_id))
            conn.commit()
            update.message.reply_text(f"{points} баллов списано! Спасибо за использование.")
        else:
            update.message.reply_text("Недостаточно баллов на балансе.")
    except (IndexError, ValueError):
        update.message.reply_text("Укажите количество баллов после команды. Пример: /redeem 10")

# Команда /help
def help_command(update: Update, context: CallbackContext):
    commands = "/start - Начать работу
/balance - Проверить баланс
/addpoints [число] - Добавить баллы
/redeem [число] - Списать баллы
/help - Список команд"
    update.message.reply_text(f"Доступные команды:\n{commands}")

# Основной код бота
def main():
    TOKEN = os.getenv("BOT_TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("addpoints", add_points))
    dispatcher.add_handler(CommandHandler("redeem", redeem))
    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
