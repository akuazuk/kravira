import logging
from aiogram import Bot, Dispatcher, executor, types
import httpx
import asyncio

API_TOKEN = '6802893919:AAHu7eQN_IHadnX9vJU1wudHTTloaMSYHyY'
EXTERNAL_API_URL = 'https://flowiseai-railway-production-aac7.up.railway.app/api/v1/prediction/216fc9ec-2253-4769-a382-fd1171ba596c'

# Словарь для хранения sessionId и последнего chatId по sessionId
session_info = {}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Отправь мне вопрос, и я перешлю его во внешний API.")

@dp.message_handler()
async def send_question_to_external_api(message: types.Message):
    chat_id = message.chat.id
    question_text = message.text

    # Извлечение текущего sessionId ассоциированного с chat_id пользователя, если он существует
    session_id = None
    for sid, info in session_info.items():
        if info.get('chatId') == str(chat_id):
            session_id = sid
            break

    payload = {
        "question": question_text,
        **({"sessionId": session_id} if session_id else {})
    }
    headers = {'Content-Type': 'application/json'}

    await bot.send_chat_action(chat_id, action=types.ChatActions.TYPING)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(EXTERNAL_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Обновление или установка sessionId и chatId на основе ответа от API
            new_session_id = data.get("sessionId")
            if new_session_id:
                session_info[new_session_id] = {"chatId": str(chat_id)}

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
