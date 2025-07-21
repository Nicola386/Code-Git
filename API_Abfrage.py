import time
import requests
from datetime import timedelta
from datetime import datetime
import pytz
from Sonnenstand import berechne_sonnenstand

def API_Abfrage(city):
    # API-Anfrage
    api_key = "8f42e8ec913bdede3133f96628cad2af"  # API-Schlüssel
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    
    # URL für die Anfrage
    complete_url = f"{base_url}q={city}&appid={api_key}"

    response = requests.get(complete_url)
    data = response.json()

    # Initialisiere Variablen für Sonnenaufgang, Sonnenuntergang und Hemisphäre
    sunrise_local, sunset_local, hemisphaere,cloudiness = None, None, None, None
    
    ############# Zum Debuggen ################
    #print(data)
    ##########################################
    


    # Sonne
    if data["cod"] == 200:
        # Extrahieren des Sonnenaufgangs und Sonnenuntergangs (Unix-Timestamps)
        sunrise_timestamp = data["sys"]["sunrise"]
        sunset_timestamp = data["sys"]["sunset"]

        # Umwandeln in datetime-Objekte (UTC)
        sunrise = datetime.utcfromtimestamp(sunrise_timestamp)
        sunset = datetime.utcfromtimestamp(sunset_timestamp)

        #Zeitzone
        timezone_offset=data["timezone"]
        timezone_offset=timezone_offset/3600    

        # Umwandeln in die lokale Zeitzone (z.B. Berlin)
        local_tz = pytz.timezone('Europe/Berlin')
        sunrise_local = sunrise.astimezone(local_tz)
        sunset_local = sunset.astimezone(local_tz)

        #Wetter
        weather_description = data["weather"][0]["description"] 
        cloudiness = data["clouds"]["all"]# 0 = klarer Himmel, 100 = komplett bewölkt

        # Hemisphäre bestimmen
        longitude= data["coord"]["lon"]
        latitude = data["coord"]["lat"]
        if latitude > 0:
            hemisphaere = "Nordhalbkugel"
        elif latitude < 0:
            hemisphaere = "Südhalbkugel"
        else:
            hemisphaere = "Äquator"

        #Sonnenstandberechnen
        current_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        azimuth, elevation=berechne_sonnenstand(latitude,longitude,current_time)

    else:
        print(f"Fehler bei der API-Abfrage: {data['message']}")

    return sunrise_local, sunset_local, hemisphaere,cloudiness,timezone_offset,azimuth, elevation,weather_description

############ Zum Debuggen#############
#API_Abfrage('Berlin')