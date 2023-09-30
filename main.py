import os
import datetime as dt
import requests
import logging
from dotenv import load_dotenv
from prettytable import PrettyTable
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENWEATHERMAP_TOKEN = os.getenv('OPENWEATHERMAP_TOKEN')
OPENWEATHERMAP_ENDPOINT = "api.openweathermap.org"
LOG_FILE = os.getenv('LOG_FILE')


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


WINDDIRECTIONSFULL = ("северный", "северо-восточный", "восточный",
                      "юго-восточный", "южный", "юго-западный",
                      "западный", "северо-западный")
WINDDIRECTIONSSHORT = ("Сев", "С-В", "Вст", "Ю-В", "Южн", "Ю-З", "Зап", "С-З")


def wind_dir(deg, len):
    wind_deg = int((deg + 22.5) // 45 % 8)
    if len == 'full':
        return WINDDIRECTIONSFULL[wind_deg]
    if len == 'short':
        return WINDDIRECTIONSSHORT[wind_deg]


class WeatherMessage:
    def __init__(self, data, message, saved_user_data) -> None:
        self.message = message
        self.saved_user_data = saved_user_data
        self.place = data["name"]
        self.sunrise_timestamp = dt.datetime.fromtimestamp(
            data["sys"]["sunrise"])
        self.sunset_timestamp = dt.datetime.fromtimestamp(
            data["sys"]["sunset"])
        self.weather_main = data["weather"][0]["description"]
        self.cur_temp = data["main"]["temp"]
        self.humidity = data["main"]["humidity"]
        self.pressure = data["main"]["pressure"]
        self.wind_speed = data["wind"]["speed"]
        try:
            self.wind_gust = round(self.wind_speed + data["wind"]["gust"], 2)
        except KeyError:
            self.wind_gust = round(self.wind_speed, 2)
        self.wind_dir = wind_dir(data["wind"]["deg"], 'full')
        self.length_of_the_day = self.sunset_timestamp - self.sunrise_timestamp
        self.sunset_timestamp = self.sunset_timestamp.strftime('%H:%M:%S')
        self.sunrise_timestamp = self.sunrise_timestamp.strftime('%H:%M:%S')

    def readableanswer(self):
        return (f"{saved_user_data[self.message.from_id]['forecast_type']}: "
                f"{self.saved_user_data[self.message.from_id]['place']}\n"
                f"Температура: {self.cur_temp}°C, {self.weather_main}\n"
                f"Влажность: {self.humidity}%\n"
                f"Давление: {round(self.pressure/1.333)} мм.рт.ст\n"
                f"Ветер: {self.wind_dir}, {self.wind_speed} м/с,"
                f" порывы до {self.wind_gust} м/с\n"
                f"Восход/закат солнца: {self.sunrise_timestamp} / "
                f"{self.sunset_timestamp}\n"
                f"Продолжительность дня: {self.length_of_the_day}\n"
                f"Ни хвоста, ни чешуи"
                )


class ForecastMessage:
    def __init__(self, data, message, saved_user_data) -> None:
        self.message = message
        self.saved_user_data = saved_user_data
        self.data = data
        self.place = data["city"]["name"]
        # получение данных о восходе и закате и вычисление
        # продолжительности дня
        self.sunrise_timestamp = dt.datetime.fromtimestamp(
            data["city"]["sunrise"])
        self.sunset_timestamp = dt.datetime.fromtimestamp(
            data["city"]["sunset"])
        self.length_of_the_day = self.sunset_timestamp - self.sunrise_timestamp
        self.sunset_timestamp = self.sunset_timestamp.strftime('%H:%M:%S')
        self.sunrise_timestamp = self.sunrise_timestamp.strftime('%H:%M:%S')

    def readableanswer(self, lp=0, days=1) -> PrettyTable:
        t = [''] * 3 * days
        result_table = ''
        for i in range(0, days + 2):
            t[i] = PrettyTable([''] + [dt.datetime.fromtimestamp(
                self.data["list"][i]["dt"]).strftime('%H:%M')
                for i in range(lp, lp + 3)])
            t[i].add_row(['Погода'] +
                         [self.data["list"][i]["weather"][0]["description"]
                          for i in range(lp, lp + 3)])
            t[i].add_row(['Темп, °C'] +
                         [round(self.data["list"][i]["main"]["temp"])
                          for i in range(lp, lp + 3)])
            t[i].add_row(['Влаж, %'] +
                         [self.data["list"][i]["main"]["humidity"]
                          for i in range(lp, lp + 3)])
            t[i].add_row(['Давл, мм.'] +
                         [round(self.data["list"][i]["main"]["pressure"]/1.333)
                          for i in range(lp, lp + 3)])
            t[i].add_row(['Ветер'] +
                         [wind_dir(self.data["list"][i]["wind"]["deg"], 'short')
                          for i in range(lp, lp + 3)])
            t[i].add_row(['Скор, м/с'] +
                         [round(self.data["list"][i]["wind"]["speed"])
                          for i in range(lp, lp + 3)])
            t[i].add_row(['Порыв, м/с'] +
                         [round(self.data["list"][i]["wind"]["gust"] +
                          self.data["list"][i]["wind"]["speed"])
                          for i in range(lp, lp + 3)])
            lp += 3
            result_table += f"```{t[i]}```\n"
        return (f"{saved_user_data[self.message.from_id]['forecast_type']}: "
                f"{self.saved_user_data[self.message.from_id]['place']}\n"
                f"{result_table}"
                f"Восход/закат солнца: {self.sunrise_timestamp} / "
                f"{self.sunset_timestamp}\n"
                f"Продолжительность дня: {self.length_of_the_day}\n"
                f"Ни хвоста, ни чешуи"
                )

        # return (f"{saved_user_data[self.message.from_id]['forecast_type']}: "
        #        f"{self.saved_user_data[self.message.from_id]['place']}\n"
        #        f"Температура: {self.cur_temp}°C, {self.weather_main}\n"
        #        f"Влажность: {self.humidity}%\n"
        #        f"Давление: {round(self.pressure/1.333)} мм.рт.ст\n"
        #        f"Ветер: {self.wind_dir}, {self.wind_speed} м/с,"
        #        f" порывы до {self.wind_gust} м/с\n"
        #        f"Восход/закат солнца: {self.sunrise_timestamp} / "
        #        f"{self.sunset_timestamp}\n"
        #        f"Продолжительность дня: {self.length_of_the_day}\n"
        #        f"Ни хвоста, ни чешуи"
        #        )


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    logging.info(f"{message.from_id} connected")
    await go_to_menu(message)


async def get_weather(place, date, forecast_type, message):
    try:
        # go_to_menu(message, place, forecast_type)
        logging.info(f"{message.from_id} requesting {place}")
        logging.info(f"http://api.openweathermap.org/data/2.5/{forecast_type}?{place}&lang=ru&units=metric&appid={OPENWEATHERMAP_TOKEN}")
        response = requests.get(f"http://api.openweathermap.org/data/2.5/{forecast_type}?{place}&lang=ru&units=metric&appid={OPENWEATHERMAP_TOKEN}")
        data = response.json()
        logging.info(data)
        if forecast_type == "weather":
            await message.reply(WeatherMessage(
                data, message, saved_user_data).readableanswer())
        if forecast_type == "forecast":
            await message.reply(ForecastMessage(
                data, message, saved_user_data).readableanswer(),
                parse_mode="MarkdownV2")
    except Exception as error:
        logging.exception(error)


@dp.message_handler()
async def go_to_menu(message: types.Message, place="Курск",
                     forecast_type="weather", api="openweather"):
    global saved_user_data
    if message.from_id not in saved_user_data:
        saved_user_data[message.from_id] = {
              "place": "Курск",
              "forecast_type": "Погода сейчас",
              "api": "openweather"
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
             "Прогноз на сутки": "forecast",
             "Прогноз на завтра": "forecast",
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
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=menu_levels[message.text])
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
    logging.info("Start polling.")
    executor.start_polling(dp)
