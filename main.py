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
    go_to_menu(message)


async def get_weather(place, date, forecast_type, message):
    try:
        go_to_menu(message, place, forecast_type) 
        logging.info(f"{message.from_id} requesting {place}")
        logging.info(f"http://api.openweathermap.org/data/2.5/{forecast_type}?{place}&lang=ru&units=metric&appid={OPENWEATHERMAP_TOKEN}")
        response = requests.get(f"http://api.openweathermap.org/data/2.5/{forecast_type}?{place}&lang=ru&units=metric&appid={OPENWEATHERMAP_TOKEN}")
        data = response.json()
        logging.info(data)
        place = data["name"]
        cur_temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        wind_gust = round(wind_speed + data["wind"]["gust"], 2)
            winddirections = ("северный", "северо-восточный", "восточный", "юго-восточный", "южный", "юго-западный", "западный", "северо-западный")
            wind_deg = int((data["wind"]["deg"] + 22.5) // 45 % 8)
            wind_dir = winddirections[wind_deg]
        sunrise_timestamp = dt.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M:%S')
        sunset_timestamp = dt.datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M:%S')

        # продолжительность дня
        length_of_the_day = (dt.datetime.fromtimestamp(data["sys"]["sunset"]) -
                             dt.datetime.fromtimestamp(data["sys"]["sunrise"]))
        await message.reply(f"{saved_user_data[message.from_id]['forecast_type']}: {saved_user_data[message.from_id]['place']}\nТемпература: {cur_temp}°C\n"
                            f"Влажность: {humidity}%\nДавление: {round(pressure/1.333)} мм.рт.ст\n"
                            f"Ветер: {wind_dir},\n{wind_speed} м/с, порывы до {wind_gust} м/с\n"
                            f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
                            f"Ни хвоста, ни чешуи"
                            )
    except Exception as error:
        logging.exception(error)
     

@dp.message_handler()
async def go_to_menu(message: types.Message, place="Курск", forecast_type="weather", api="openweather"):
    global saved_user_data
    if message.from_id not in saved_user_data:
         saved_user_data[message.from_id] = {
              "place": "Курск",
              "forecast_type": "Погода сейчас",
              "api" : "openweather"
         }
    else:
        if saved_user_data[message.from_id]["place"] is None:
            saved_user_data[message.from_id]["place"] = "Курск"
        if saved_user_data[message.from_id]["forecast_type"] is None:
            saved_user_data[message.from_id]["forecast_type"] = "weather"
        if saved_user_data[message.from_id]["api"] is None:
            saved_user_data[message.from_id]["api"] = "openweather"
    date = dt.datetime.now().strftime('%Y-%m-%d %H:%M')
    cities = ["Курск", "Железногорск", "Курчатов", "Льгов", "Щигры",
              "Рыльск", "Обоянь", "Суджа", "Фатеж"]
    ponds = {"Стадион": "lat=51.831599&lon=36.010743",
             "Пойменово": "lat=51.961621&lon=36.244221"}
    dates = {"Погода сейчас": "weather",
             "Прогноз на сегодня": "forecast",
             "Прогноз на завтра" : "forecast",
             "Прогноз на выходные": "forecast"}
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
         list(ponds.keys()) + ["Главное меню"]][i:i + 2] for i in
        range(0, len(ponds) + 1, 2)
    ]
    date_menu = [
        [types.KeyboardButton(text=date) for date in
         list(dates.keys()) + ["Главное меню"]][i:i + 2] for i in
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
                saved_user_data[message.from_id]["place"] = message.text
        if message.text in ponds:
                place = ponds[message.text]
                saved_user_data[message.from_id]["place"] = message.text
        if message.text in dates:
                place = f"q={place}"
                forecast_type = dates[message.text]
                saved_user_data[message.from_id]["forecast_type"] = message.text
        await get_weather(place, date, forecast_type, message)


if __name__ == "__main__":
    logging.basicConfig(
            level=logging.INFO,
            filename=LOG_FILE,
            filemode="w",
            format="%(asctime)s %(levelname)s %(message)s"
            ) 
    date = dt.datetime.now().strftime('%Y-%m-%d %H:%M')
    saved_user_data = dict()
    logging.info(f"Start polling.")
    executor.start_polling(dp)
