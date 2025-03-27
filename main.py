import os
from dotenv import load_dotenv
import aiohttp
from deep_translator import GoogleTranslator
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio

# Загружаем переменные окружения из файла .env
load_dotenv()

# Токен вашего бота
TOKEN = "7838326957:AAHbDvhPpQi249l1KTqU6aTTr4ajg3i70e4"
API_KEY = "a0345e5799a9303b6e5cc457d54bafa8"

# Проверка, что токен загружен
if not TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что файл .env настроен правильно.")

# Инициализация бота с использованием DefaultBotProperties
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Инициализация переводчика
translator = GoogleTranslator(source='auto', target='ru')

# Функция для перевода текста
def translate_text(text):
    try:
        return translator.translate(text)
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return text  # Возвращаем оригинальный текст в случае ошибки

# Функция для форматирования вложенных данных
def format_data(data, indent=0):
    message_text = ""
    if isinstance(data, dict):  # Если данные — это словарь
        for key, value in data.items():
            translated_key = translate_text(key)  # Переводим ключ
            if translated_key.lower() == "успех":  # Пропускаем поле "успех"
                continue
            if isinstance(value, (dict, list)):  # Если значение — это словарь или список
                message_text += " " * indent + f"<b>{translated_key}:</b>\n"
                message_text += format_data(value, indent + 4)  # Рекурсивно обрабатываем значение
            else:  # Если значение — это строка или число
                translated_value = translate_text(str(value))  # Переводим значение
                message_text += " " * indent + f"<b>{translated_key}:</b> {translated_value}\n"
    elif isinstance(data, list):  # Если данные — это список
        for item in data:
            message_text += format_data(item, indent)  # Рекурсивно обрабатываем каждый элемент
    else:  # Если данные — это строка или число
        translated_value = translate_text(str(data))  # Переводим значение
        message_text += " " * indent + f"{translated_value}\n"
    return message_text



# Функция для обработки команды /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Отправь мне VIN-код, и я покажу информацию о машине."
    )

# Функция для обработки VIN-кода
@dp.message()
async def handle_vin(message: Message):
    vin = message.text.strip()
    api_url = f'https://parser-api.com/parser/gibdd_api/history?key={API_KEY}&vin={vin}'

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers={'X-Api-Key': API_KEY}) as response:
            if response.status == 200:
                data = await response.json()

                # Формируем сообщение для отправки
                message_text = "<b>Информация о машине:</b>\n\n"
                message_text += format_data(data)  # Форматируем и переводим данные

                # Добавляем завершающее сообщение
                message_text += "\n<i>Отчет сформирован и завершен!</i>"

                await message.answer(message_text)
            else:
                await message.answer(f"Ошибка: {response.status}. Не удалось получить данные.")

# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())