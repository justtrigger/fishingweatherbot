import os
import datetime as dt
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
LOG_FILE = os.getenv('LOG_FILE')


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    logging.info(f"{message.from_id} connected")
    await go_to_menu(message)


async def get_weather(place, date, message):
    try:
        go_to_menu(message) 
        logging.info(f"{message.from_id} requesting {place}")
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?{place}&lang=ru&units=metric&appid={OPENWEATHERMAP_TOKEN}")
        data = response.json()
        place = data["name"]
        cur_temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]

        sunrise_timestamp = dt.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = dt.datetime.fromtimestamp(data["sys"]["sunset"])

        # продолжительность дня
        length_of_the_day = (dt.datetime.fromtimestamp(data["sys"]["sunset"]) -
                             dt.datetime.fromtimestamp(data["sys"]["sunrise"]))
        await message.reply(f"{date}\n"
                            f"Погода в городе: {place}\nТемпература: {cur_temp}°C\n"
                            f"Влажность: {humidity}%\nДавление: 
                              {round(pressure/1.333)} мм.рт.ст\nВетер: {wind} м/с\n"
                            f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
                            f"Ни хвоста, ни чешуи"
                            )
    except Exception as error:
        logging.exception(error)
     

@dp.message_handler()
async def go_to_menu(message: types.Message):
    global place
    global date
    cities = ["Курск", "Железногорск", "Курчатов", "Льгов", "Щигры",
              "Рыльск", "Обоянь", "Дмитриев", "Суджа", "Фатеж"]
    ponds = ["Стадион"]
    dates = ["Погода сейчас", "Прогноз на сегодня",
             "Прогноз на завтра", "Прогноз на выходные"]
    main_menu = [
        [
            types.KeyboardButton(text="Выбор города"),
            types.KeyboardButton(text="Выбор водоема"),
        ],
        [
            types.KeyboardButton(text="Выбор дня"),
            types.KeyboardButton(text="Выбор API")
        ],
        [
            types.KeyboardButton(text="Главное меню")
        ]
    ]
    city_menu = [
        [types.KeyboardButton(text=city) for city in
         cities + ["Главное меню"]][i:i + 2] for i in
        range(0, len(cities) + 1, 2)
    ]
    pond_menu = [
        [types.KeyboardButton(text=pond) for pond in
         ponds + ["Главное меню"]][i:i + 2] for i in
        range(0, len(ponds) + 1, 2)
    ]
    date_menu = [
        [types.KeyboardButton(text=date) for date in
         dates + ["Главное меню"]][i:i + 2] for i in
        range(0, len(dates) + 1, 2)
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
                place = f"q={message.text}"
                date = dt.datetime.now().strftime('%Y-%m-%d %H:%M')
        if message.text in ponds:
                await message.reply(f"функционала пока нет")
        if message.text in dates:
                await message.reply(f"функционала пока нет")
        await get_weather(place, date, message)


if __name__ == "__main__":
    logging.basicConfig(
            level=logging.INFO,
            filename=LOG_FILE,
            filemode="w",
            format="%(asctime)s %(levelname)s %(message)s"
            )
    place = "Курск"
    date = dt.datetime.now().strftime('%Y-%m-%d %H:%M')
    logging.info(f"Start polling.")
    executor.start_polling(dp)
