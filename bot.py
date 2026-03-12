import os
import requests
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

# --- БЛОК ДЛЯ ОБХОДА ОШИБКИ RENDER ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "I am alive!", 200

def run_flask():
    # Render передает порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Запускаем Flask в отдельном потоке, чтобы он не мешал боту
threading.Thread(target=run_flask, daemon=True).start()
# -------------------------------------

# Теперь код берет токен из настроек Render, а не светит его в интернете
API_TOKEN = os.getenv('BOT_TOKEN')
CURRENCY_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'

async def get_exchange_rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        response = requests.get(CURRENCY_API_URL)
        data = response.json()

        # Запрос курса EUR
        eur_response = requests.get('https://api.exchangerate-api.com/v4/latest/EUR')
        eur_data = eur_response.json()
        
        usd_to_pln = data['rates'].get('PLN')
        eur_to_pln = eur_data['rates'].get('PLN')
        today = datetime.now().strftime("%d.%m.%Y")

        if usd_to_pln and eur_to_pln:
            await update.message.reply_text(
                f'Курс на {today}\n'
                f'USD/PLN: {usd_to_pln}\n'
                f'EUR/PLN: {eur_to_pln}'
            )
        else:
            await update.message.reply_text('Не удалось получить курсы валют.')
    except Exception as e:
        await update.message.reply_text("Ошибка при получении данных. Попробуйте позже.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Используйте команду /rate для получения курсов USD/PLN и EUR/PLN.')

if __name__ == '__main__':
    # Проверка, что токен вообще задан
    if not API_TOKEN:
        print("Ошибка: Переменная BOT_TOKEN не найдена в настройках!")
    else:
        application = ApplicationBuilder().token(API_TOKEN).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('rate', get_exchange_rate))
        print("Бот запущен...")
        application.run_polling()
