import os
import datetime
import requests
import math
import logging
from dotenv import load_dotenv
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor 

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENWEATHERMAP_TOKEN = os.getenv('OPENWEATHERMAP_TOKEN')
OPENWEATHERMAP_ENDPOINT = "api.openweathermap.org"
LOG_FILE=os.getenv('LOG_FILE')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    logging.info(f"{message.from_id} подключился к боту")
    await message.reply("Введите название города для получения текущей сводки")

@dp.message_handler()
async def get_weather(message: types.Message):
    try:
        city = message.text
        logging.info(f"{message.from_id} заправшивает {city}")
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&units=metric&appid={OPENWEATHERMAP_TOKEN}")
        data = response.json()
        city = data["name"]
        cur_temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]

        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])

        # продолжительность дня
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) -       datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        await message.reply(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                            f"Погода в городе: {city}\nТемпература: {cur_temp}°C\n"
                            f"Влажность: {humidity}%\nДавление: {math.ceil(pressure/1.333)} мм.рт.ст\nВетер: {wind} м/с \n"
                            f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
                            f"Ни хвоста, ни чешуи"
                            )
    except Exception as error:
        logging.error(f"{error}")
        


if __name__ == "__main__":
    logging.basicConfig(
            level=logging.INFO,
            filename=LOG_FILE,
            filemode="w",
            format="%(asctime)s %(levelname)s %(message)s"
            )
    logging.info(f"Start polling.")
    executor.start_polling(dp)
