import requests
WEATHER_API_CODE = "b469c21bf19e0eebe6ba6442ad1235c4"
def grab_weather_details(city_name):
    weather_url = "http://api.openweathermap.org/data/2.5/weather"
    parameters = {
        "q": city_name,
        "appid": WEATHER_API_CODE,
        "units": "metric"
    }
    try:
        result = requests.get(weather_url, params=parameters)
        data = result.json()
        if data.get("cod") == 200:
            return {
                "city": data["name"],
                "weather": data["weather"][0]["description"].title(),
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }
        else:
            return None
    except:
        return None
def show_weather_info(info):
    if not info:
        return None
    report = f"""
=== WEATHER UPDATE ===
Location    : {info['city']}
Weather     : {info['weather']}
Temperature : {info['temp']} °C
Humidity    : {info['humidity']}%
Wind        : {info['wind_speed']} m/s
======================
"""
    print(report)
    return report
def store_weather_file(report, city_name):
    if not report:
        return
    file_name = f"{city_name}_weather_report.txt"
    with open(file_name, "w") as f:
        f.write(report)
    print(f"Saved weather info in {file_name}")
if __name__ == "__main__":
    print("WEATHER CHECKER PROGRAM")
    print("=======================")
    city = input("Which city weather you want? : ").strip()
    if city:
        weather_result = grab_weather_details(city)
        if weather_result:
            report = show_weather_info(weather_result)
            store_weather_file(report, city)
        else:
            print(f"Sorry, couldn't find weather for '{city}'. Check spelling or try another city.")
    else:
        print("No city entered.")
