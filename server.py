from flask import Flask, Response
import requests
from datetime import datetime

app = Flask(__name__)

LAT = 51.4645
LON = -0.1921

# Map Open-Meteo weather codes to icons
WEATHER_ICONS = {
    0: "☀️", 1: "🌤️", 2: "🌤️", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌧️", 53: "🌧️", 55: "🌧️",
    56: "🌧️", 57: "🌧️",
    61: "🌧️", 63: "🌧️", 65: "🌧️",
    66: "🌧️", 67: "🌧️",
    71: "❄️", 73: "❄️", 75: "❄️",
    77: "❄️",
    80: "🌧️", 81: "🌧️", 82: "🌧️",
    95: "⛈️", 96: "⛈️", 99: "⛈️"
}

def get_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m,apparent_temperature,precipitation_probability,weathercode&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset,weathercode&timezone=Europe/London"
    r = requests.get(url)
    return r.json()

def format_time(dt_str):
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%H:%M")

def format_date(dt_str):
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%a %d %b")

@app.route("/forecast")
def forecast():
    data = get_weather()
    output = ""

    # Sunrise & Sunset
    sunrise = format_time(data["daily"]["sunrise"][0])
    sunset = format_time(data["daily"]["sunset"][0])
    output += f"Wandsworth Weather\nSunrise: {sunrise}  |  Sunset: {sunset}\n\n"

    # Next 8 Hours
    output += "Next 8 Hours\nTime  | Temp | Feels | Condition | Rain\n------------------------------------------\n"
    for i in range(8):
        time = format_time(data["hourly"]["time"][i])
        temp = f"{round(data['hourly']['temperature_2m'][i])}°C"
        feels = f"{round(data['hourly']['apparent_temperature'][i])}°C"
        code = data["hourly"]["weathercode"][i]
        condition = WEATHER_ICONS.get(code, "🌤️")
        rain = f"{round(data['hourly']['precipitation_probability'][i])}%"
        output += f"{time} | {temp.ljust(4)} | {feels.ljust(4)} | {condition.ljust(9)} | {rain}\n"

    # Next 3 Days
    output += "\nNext 3 Days\nDate       | High | Low  | Condition | Rain\n---------------------------------------------\n"
    for i in range(1,4):
        date = format_date(data["daily"]["time"][i])
        high = f"{round(data['daily']['temperature_2m_max'][i])}°C"
        low = f"{round(data['daily']['temperature_2m_min'][i])}°C"
        code = data["daily"]["weathercode"][i]
        condition = WEATHER_ICONS.get(code, "🌤️")
        rain = f"{round(data['daily']['precipitation_probability_max'][i])}%"
        output += f"{date.ljust(10)} | {high.ljust(4)} | {low.ljust(4)} | {condition.ljust(9)} | {rain}\n"

    return Response(output, mimetype="text/plain; charset=utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
