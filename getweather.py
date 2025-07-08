import requests
from datetime import datetime


def day(sunrise_str: str, sunset_str: str):
    sunrise = datetime.strptime(sunrise_str, "%I:%M %p")
    sunset = datetime.strptime(sunset_str, "%I:%M %p")
    dur = sunset - sunrise
    hours, rem = divmod(dur.seconds, 3600)
    minutes = rem // 60
    return f'{hours}:{minutes}'


def getw(city):
    time = datetime.now()
    hour = datetime.now().hour
    hours: list = [0, 3, 6, 9, 12, 15, 18, 21, 24]
    out: dict = {}
    URL = f'https://wttr.in/{city}?format=j1&lang=ru'

    responce = requests.get(URL)
    data = responce.json()
    
    current = data['current_condition'][0]
    weather = data['weather'][0]
    hourly = weather['hourly']
    astronomy = weather['astronomy'][0]
    
    out['date'] = time.strftime("%Y-%m-%d %H:%M")
    
    for i in range(len(hours) - 1):
        if hour >= hours[i] and hour < hours[i + 1]:
            out['temperature'] = hourly[i]['tempC']
            out['feels'] = hourly[i]['FeelsLikeC']
            out['sky'] = hourly[i]['lang_ru'][0]['value']
            out['cloudcover'] = hourly[i]['cloudcover']
            out['humidity'] = hourly[i]['humidity']
            out['windspeed'] = hourly[i]['windspeedKmph']
            out['windgust'] = hourly[i]['WindGustKmph']
            pressure = int(hourly[i]['pressure'])
            out['pressure'] = round(pressure * 0.750062, 1)
            
            out['frost'] = hourly[i]['chanceoffrost']
            out['snow'] = hourly[i]['chanceofsnow']
            out['fog'] = hourly[i]['chanceoffog']
            out['rain'] = hourly[i]['chanceofrain']
            out['thunder'] = hourly[i]['chanceofthunder']
            
            break
    
    out['moon'] = astronomy['moon_illumination']
    out['moonrise'] = astronomy['moonrise']
    out['moonset'] = astronomy['moonset']
    out['sunrise'] = astronomy['sunrise']
    out['sunset'] = astronomy['sunset']
    out['daylight'] = day(astronomy['sunrise'], astronomy['sunset'])
    
    #nearest
    out['lat'] = data['nearest_area'][0]['latitude']
    out['lon'] = data['nearest_area'][0]['longitude']
    return out

