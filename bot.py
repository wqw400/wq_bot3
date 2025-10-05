from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, CallbackContext
import os

# --- Словарь для хранения очков теста ---
user_scores = {}

# --- Токен из Secrets Replit ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, None)

app = Flask(__name__)

# --- Главное меню ---
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Советы по безопасности", callback_data='tips')],
        [InlineKeyboardButton("Пройти тест", callback_data='quiz')],
        [InlineKeyboardButton("Полезные ссылки", callback_data='links')],
        [InlineKeyboardButton("О боте", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text("Привет! Я бот по защите от мошенников. Выбери опцию:", reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.edit_message_text("Главное меню:", reply_markup=reply_markup)

# --- Обработка кнопок ---
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    # --- Главное меню ---
    if query.data == 'tips':
        keyboard = [
            [InlineKeyboardButton("Как не попасться на уловки", callback_data='tricks')],
            [InlineKeyboardButton("Безопасность онлайн-платежей", callback_data='payments')],
            [InlineKeyboardButton("Назад", callback_data='back')]
        ]
        query.edit_message_text("Советы по безопасности:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'quiz':
        user_scores[user_id] = 0
        keyboard = [
            [InlineKeyboardButton("Начать тест", callback_data='q1')],
            [InlineKeyboardButton("Назад", callback_data='back')]
        ]
        query.edit_message_text("Проверка знаний о мошенниках:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == 'links':
        query.edit_message_text(
            "Полезные ссылки:\n"
            "🔹 [Федеральная служба безопасности](https://www.fsb.ru/)\n"
            "🔹 [Роскомнадзор](https://rkn.gov.ru/)\n"
            "🔹 [ЦБ РФ - советы по безопасности](https://www.cbr.ru/)"
        )

    elif query.data == 'about':
        query.edit_message_text(
            "Я учебный бот, который помогает узнать о мошенниках и защитить себя онлайн.\n"
            "Можно изучать советы, проходить тесты и получать полезные ссылки."
        )

    # --- Подменю Советы ---
    elif query.data == 'tricks':
        keyboard = [[InlineKeyboardButton("Назад", callback_data='tips')]]
        query.edit_message_text(
            "⚠️ Не доверяй неизвестным ссылкам и сообщениям от незнакомцев.\n"
            "⚠️ Проверяй контакты перед переводом денег.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == 'payments':
        keyboard = [[InlineKeyboardButton("Назад", callback_data='tips')]]
        query.edit_message_text(
            "💳 Используй только официальные платёжные системы.\n"
            "💳 Никогда не сообщай PIN-коды и CVV.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # --- Тест с вопросами ---
    elif query.data.startswith('q'):
        questions = {
            'q1': {'text': "Можно ли доверять незнакомому человеку, который обещает быстро заработать?", 'yes': False},
            'q2': {'text': "Стоит ли проверять ссылки перед переходом?", 'yes': True},
            'q3': {'text': "Можно ли сообщать свои пароли друзьям?", 'yes': False}
        }

        if query.data in questions:
            question = questions[query.data]
            keyboard = [
                [InlineKeyboardButton("Да", callback_data=f"{query.data}_yes")],
                [InlineKeyboardButton("Нет", callback_data=f"{query.data}_no")],
                [InlineKeyboardButton("Назад", callback_data='quiz')]
            ]
            query.edit_message_text(question['text'], reply_markup=InlineKeyboardMarkup(keyboard))

        elif query.data.endswith('_yes') or query.data.endswith('_no'):
            q_key = query.data[:-4]
            answer = query.data.endswith('_yes')
            correct = questions[q_key]['yes']
            if answer == correct:
                user_scores[user_id] += 1
                query.edit_message_text("✅ Верно!", reply_markup=None)
            else:
                query.edit_message_text("❌ Неверно!", reply_markup=None)

            next_question = {'q1':'q2', 'q2':'q3', 'q3':None}[q_key]
            if next_question:
                keyboard = [[InlineKeyboardButton("Следующий вопрос", callback_data=next_question)],
                            [InlineKeyboardButton("Назад", callback_data='quiz')]]
                query.message.reply_text("Нажми, чтобы продолжить:", reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                score = user_scores[user_id]
                query.message.reply_text(f"Тест завершён! Ты набрал {score}/3 баллов.",
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Главное меню", callback_data='back')]]))

    elif query.data == 'back':
        start(update, context)

# --- Команда /help ---
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("Нажми /start для открытия главного меню и изучения советов по безопасности.")

# --- Регистрируем обработчики ---
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CallbackQueryHandler(button))

# --- Webhook для Telegram ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dp.process_update(update)
    return "ok"

# --- Главная страница для проверки бота ---
@app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
