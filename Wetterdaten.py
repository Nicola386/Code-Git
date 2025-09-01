import requests
from datetime import datetime, timezone, timedelta
import pvlib


def berechne_sonnenstand(latitude, longitude, current_time):
  
    solpos = pvlib.solarposition.get_solarposition(current_time, latitude, longitude)
    azimuth = solpos['azimuth'].values[0]
    elevation = solpos['apparent_elevation'].values[0]
    azimuth=round(azimuth,2)
    elevation=round(elevation,2)

    return azimuth, elevation

def API_Abfrage(city):
    # API-Anfrage
    api_key = "8f42e8ec913bdede3133f96628cad2af"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"

    response = requests.get(complete_url)
    data = response.json()

    # Prüfen, ob die Anfrage erfolgreich war
    if data["cod"] != 200:
        print(f"Fehler bei der API-Abfrage: {data.get('message', 'Unbekannter Fehler')}")
        return None # Bei einem Fehler None zurückgeben

    #Zeitzone und Zeitstempel aus der API holen ---
    offset_seconds = data['timezone']
    local_tz = timezone(timedelta(seconds=offset_seconds))
    

    #Sonnenaufgang von UTC in die lokale Zeitzone umrechnen ---
    sunrise_utc = datetime.fromtimestamp(data['sys']['sunrise'], tz=timezone.utc)
    sunrise_local = sunrise_utc.astimezone(local_tz)

    #Sonnenuntergang von UTC in die lokale Zeitzone umrechnen ---
    sunset_utc = datetime.fromtimestamp(data['sys']['sunset'], tz=timezone.utc)
    sunset_local = sunset_utc.astimezone(local_tz)
 
    #Wetterdaten extrahieren ---
    weather_description = data["weather"][0]["description"] 
    cloudiness = data["clouds"]["all"] # 0 = klar, 100 = bewölkt

    #Sonnenstand berechnen ---
    latitude = data["coord"]["lat"]
    longitude = data["coord"]["lon"]
    current_time = datetime.now(timezone.utc) # Aktuelle UTC-Zeit verwenden
    azimuth, elevation = berechne_sonnenstand(latitude, longitude, current_time)
    
    
    return (sunrise_local, sunset_local, cloudiness, azimuth, elevation, weather_description)

############ Zum Debuggen#############
# if __name__ == "__main__":
#    result = API_Abfrage('Karlsruhe')
# if result:
#     (sunrise, sunset, cloud, az, el, weather) = result
#     print(f"Stadt: Karlsruhe")
#     print(f"Sonnenaufgang: {sunrise.strftime('%H:%M:%S')}")
#     print(f"Sonnenuntergang: {sunset.strftime('%H:%M:%S')}")
#     print(f"Wetter: {weather}")
#     print(f"Bewölkung: {cloud}%")
#     print(f"Sonnen-Azimut: {round(az, 2)}°")
#     print(f"Sonnenhöhe: {round(el, 2)}°")
########################################