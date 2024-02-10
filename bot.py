import logging
from aiogram import Bot, Dispatcher, executor, types
import httpx
import asyncio
from datetime import datetime, timedelta

API_TOKEN = '6802893919:AAHu7eQN_IHadnX9vJU1wudHTTloaMSYHyY'
EXTERNAL_API_URL = 'https://flowiseai-railway-production-aac7.up.railway.app/api/v1/prediction/216fc9ec-2253-4769-a382-fd1171ba596c'

# Словарь для хранения sessionId и времени последнего обращения по chat_id
session_storage = {}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

SESSION_TIMEOUT = timedelta(minutes=30)  # Время жизни сессии

def is_session_expired(last_interaction):
    """Проверяет, истекло ли время сессии."""
    return datetime.now() - last_interaction > SESSION_TIMEOUT

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Отправь мне вопрос, и я перешлю его во внешний API.")
    # Сброс сессии при начале нового диалога
    session_storage.pop(message.chat.id, None)

@dp.message_handler()
async def send_question_to_external_api(message: types.Message):
    chat_id = message.chat.id
    question_text = message.text

    session_info = session_storage.get(chat_id, {})
    session_id = session_info.get("sessionId")
    last_interaction = session_info.get("last_interaction", datetime.now())

    if not session_id or is_session_expired(last_interaction):
        session_id = None  # Сброс sessionId для получения нового, если сессия истекла

    payload = {
        "question": question_text,
        "sessionId": session_id
    }
    headers = {'Content-Type': 'application/json'}

    await bot.send_chat_action(chat_id, action=types.ChatActions.TYPING)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(EXTERNAL_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Обновление sessionId и времени последнего обращения в хранилище
            session_storage[chat_id] = {
                "sessionId": data.get("sessionId", session_id),
                "last_interaction": datetime.now()
            }

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
