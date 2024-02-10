import logging
from aiogram import Bot, Dispatcher, executor, types
import httpx
import asyncio
import uuid

API_TOKEN = '6802893919:AAHu7eQN_IHadnX9vJU1wudHTTloaMSYHyY'
EXTERNAL_API_URL = 'https://flowiseai-railway-production-aac7.up.railway.app/api/v1/prediction/216fc9ec-2253-4769-a382-fd1171ba596c' # Замените {your-chatflowid} на ваш реальный chatflowid

# Словарь для хранения sessionId по chat_id
session_storage = {}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Отправь мне вопрос, и я перешлю его во внешний API.")
    # Генерируем и сохраняем случайный sessionId для нового пользователя, если он ещё не существует
    if message.chat.id not in session_storage:
        session_storage[message.chat.id] = str(uuid.uuid4())

@dp.message_handler()
async def send_question_to_external_api(message: types.Message):
    chat_id = message.chat.id
    question_text = message.text

    # Получаем текущий sessionId для данного пользователя
    session_id = session_storage.get(chat_id)

    payload = {
        "question": question_text,
        "overrideConfig": {
            "sessionId": session_id
        }
    }
    headers = {'Content-Type': 'application/json'}

    await bot.send_chat_action(chat_id, action=types.ChatActions.TYPING)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(EXTERNAL_API_URL.format(your-chatflowid='216fc9ec-2253-4769-a382-fd1171ba596c'), json=payload, headers=headers) # Замените 'your_actual_chatflowid' на ваш реальный chatflowid
            response.raise_for_status()
            data = response.json()

            answer_text = data.get('text', 'Извините, не могу обработать ваш запрос.')
            await message.answer(answer_text)

        except httpx.HTTPStatusError as e:
            logging.error(f"Ошибка ответа от API: {e.response.status_code} - {e.response.text}")
            await message.answer('Произошла ошибка при обработке вашего запроса API.')

        except httpx.RequestError as e:
            logging.error(f"Ошибка запроса к API: {str(e)}")
            await message.answer('Произошла ошибка при отправке запроса к API.')

        except Exception as e:
            logging.error(f"Неизвестная ошибка: {str(e)}")
            await message.answer('Произошла неизвестная ошибка.')

async def on_startup(dp: Dispatcher):
    await bot.delete_webhook()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
