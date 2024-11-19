import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

# Функция для получения подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect("users.db")
    return conn

# Создание таблицы для хранения данных о пользователях
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

# Регистрация пользователя в базе данных
def register_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

# Проверка регистрации пользователя
def is_registered(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Команда /start
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    register_user(user_id)
    update.message.reply_text("Добро пожаловать в систему! Используйте /balance для проверки баланса.")

# Команда /balance
def balance(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_registered(user_id):
        update.message.reply_text("Вы не зарегистрированы. Введите /start для регистрации.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        balance = result[0]
        update.message.reply_text(f"Ваш текущий баланс: {balance} баллов.")
    else:
        update.message.reply_text("Произошла ошибка. Попробуйте снова.")

# Команда /addpoints
def add_points(update: Update,