from flask import Flask, Response
import requests
from datetime import datetime

app = Flask(__name__)

LAT = 51.4645
LON = -0.1921

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
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        # Return debug message if API fails
        return {"error": str(e)}

def format_time(dt_str):
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%H:%M")

def format_date(dt_str):
    dt = datetime.fromisoformat(dt_str)
    return dt.strftime("%a %d")

@app.route("/forecast")
def forecast_debug():
    data = get_weather()
    now = datetime.now().strftime("%H:%M")

    # If API failed, return debug message
    if "error" in data:
        return Response(f"DEBUG: Could not fetch weather data.\nError: {data['error']}", mimetype="text/plain; charset=utf-8")

    # Header
    sunrise = format_time(data["daily"]["sunrise"][0])
    sunset = format_time(data["daily"]["sunset"][0])
    output = f"Wandsworth Weather\nSun: {sunrise}  |  Set: {sunset}\nUpd: {now}\n\n"

    # Next 8 hours
    output += "Next 8h\nTime | T  | F  | C  | R\n" + "-"*25 + "\n"
    for i in range(8):
        time = format_time(data["hourly"]["time"][i])
        temp = f"{round(data['hourly']['temperature_2m'][i])}"
        feels = f"{round(data['hourly']['apparent_temperature'][i])}"
        code = data["hourly"]["weathercode"][i]
        condition = WEATHER_ICONS.get(code, "🌤️")
        rain = f"{round(data['hourly']['precipitation_probability'][i])}"
        output += f"{time} | {temp.rjust(2)} | {feels.rjust(2)} | {condition} | {rain}%\n"

    # Next 3 days
    output += "\nNext 3d\nDate      | H | L | C  | R\n" + "-"*28 + "\n"
    for i in range(1,4):
        date = format_date(data["daily"]["time"][i])
        high = f"{round(data['daily']['temperature_2m_max'][i])}"
        low = f"{round(data['daily']['temperature_2m_min'][i])}"
        code = data["daily"]["weathercode"][i]
        condition = WEATHER_ICONS.get(code, "🌤️")
        rain = f"{round(data['daily']['precipitation_probability_max'][i])}"
        output += f"{date.ljust(9)} |{high.rjust(2)} |{low.rjust(2)} | {condition} | {rain}%\n"

    # Append debug confirmation line for TRMNL
    output += "\nDEBUG: TRMNL can fetch this text!"

    return Response(output, mimetype="text/plain; charset=utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
