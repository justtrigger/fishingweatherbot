import os
import datetime
import requests
import logging
from dotenv import load_dotenv
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENWEATHERMAP_TOKEN = os.getenv('OPENWEATHERMAP_TOKEN')
OPENWEATHERMAP_ENDPOINT = "api.openweathermap.org"
LOG_FILE=os.getenv('LOG_FILE')


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    logging.info(f"{message.from_id} connected")
    await go_to_menu(message)


async def get_weather(city, date, message):
    try:
        go_to_menu(message) 
        logging.info(f"{message.from_id} requesting {city}")
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
        await message.reply(f"{date}\n"
                            f"Погода в городе: {city}\nТемпература: {cur_temp}°C\n"
                            f"Влажность: {humidity}%\nДавление: {round(pressure/1.333)} мм.рт.ст\nВетер: {wind} м/с \n"
                            f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
                            f"Ни хвоста, ни чешуи"
                            )
    except Exception as error:
        logging.exception(error)
        

@dp.message_handler()
async def go_to_menu(message: types.Message):
    global city
    global date
    cities = ["Курск", "Курчатов", "Суджа", "Железногорск"]
    ponds = ["Стадион"]
    dates = ["Погода сейчас", "Прогноз на сегодня", "Прогноз на завтра", "Прогноз на выходные"]
    main_menu = [
        [
            types.KeyboardButton(text="Выбор города"),
            types.KeyboardButton(text="Выбор водоема"),
        ],
        [
            types.KeyboardButton(text="Выбор дня"),
            types.KeyboardButton(text="Главное меню")
        ]
    ]
    city_menu = [
       [
           types.KeyboardButton(text="Курск"),
           types.KeyboardButton(text="Курчатов"),
       ],
       [
           types.KeyboardButton(text="Суджа"),
           types.KeyboardButton(text="Железногорск")
       ],
       [
           types.KeyboardButton(text="Главное меню")
       ]
   ]
    pond_menu = [
        [
            types.KeyboardButton(text="Стадион"),
        ],
        [
            types.KeyboardButton(text="Главное меню")
        ]
    ]
    date_menu = [
        [
            types.KeyboardButton(text="Погода сейчас"),
            types.KeyboardButton(text="Прогноз на сегодня"),
        ],
        [
            types.KeyboardButton(text="Прогноз на завтра"),
            types.KeyboardButton(text="Прогноз на выходные"),
        ],
        [
            types.KeyboardButton(text="Главное меню")
        ]
    ]
    menu_levels = {
        "Главное меню": main_menu,
        "Выбор города": city_menu,
        "Выбор водоема": pond_menu,
        "Выбор дня": date_menu,
    }
    try:
        keyboard = types.ReplyKeyboardMarkup(keyboard=menu_levels[message.text])
        await message.reply(f"{message.text}", reply_markup=keyboard)
    except KeyError:
        if message.text in cities:
                city = message.text
                date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        if message.text in ponds:
                await message.reply(f"функционала пока нет")
        if message.text in dates:
                await message.reply(f"функционала пока нет")
        await get_weather(city, date, message)


if __name__ == "__main__":
    logging.basicConfig(
            level=logging.INFO,
            filename=LOG_FILE,
            filemode="w",
            format="%(asctime)s %(levelname)s %(message)s"
            )
    city = "Курск"
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    logging.info(f"Start polling.")
    executor.start_polling(dp)
