import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import httpx
import uuid

API_TOKEN = '6802893919:AAHu7eQN_IHadnX9vJU1wudHTTloaMSYHyY'
EXTERNAL_API_URL = 'https://flowiseai-railway-production-aac7.up.railway.app/api/v1/prediction/216fc9ec-2253-4769-a382-fd1171ba596c'

# Словарь для хранения sessionId по chat_id
session_storage = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Привет, {user.first_name}! Задай мне вопрос.")
    
    # Генерируем и сохраняем случайный sessionId для нового пользователя, если он ещё не существует
    if update.effective_chat.id not in session_storage:
        session_storage[update.effective_chat.id] = str(uuid.uuid4())

async def send_question_to_external_api(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    question_text = update.message.text

    # Получаем текущий sessionId для данного пользователя
    session_id = session_storage.get(chat_id)

    payload = {
        "question": question_text,
        "overrideConfig": {
            "sessionId": session_id
        }
    }
    headers = {'Content-Type': 'application/json'}

    async with httpx.AsyncClient() as client:
        response = await client.post(EXTERNAL_API_URL, json=payload, headers=headers)
        if response.is_success:
            data = response.json()
            answer_text = data.get('text', 'Извините, не могу обработать ваш запрос.')
            context.bot.send_message(chat_id=chat_id, text=answer_text)
        else:
            logging.error(f"Ошибка ответа от API: {response.status_code} - {response.text}")
            context.bot.send_message(chat_id=chat_id, text='Произошла ошибка при обработке вашего запроса API.')

async def main():
    bot = Bot(token=API_TOKEN)
    updater = Updater(token=API_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, send_question_to_external_api))

    await updater.start_polling()
    await updater.idle()


if __name__ == '__main__':
    main()
