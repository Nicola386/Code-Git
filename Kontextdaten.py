import os
import time
import pandas as pd
from datetime import timedelta, datetime
from API_Abfrage import API_Abfrage
from Lux_berechnung import berechne_lux

# Pfad des aktuellen Skriptverzeichnisses
script_dir = os.path.dirname(os.path.abspath(__file__))

# Vollständiger Pfad zur CSV-Datei im Skriptordner
csv_path = os.path.join(script_dir, 'context_data.csv')

# Funktion zum Abrufen der Systemdaten und API-Daten
def collect_data(city, last_api_call_time, last_data, window_orientation, api_data_cache):
    current_time = datetime.now().replace(microsecond=0)

    # API-Daten nur alle 10 Sekunden pro Stadt abrufen
    if city not in api_data_cache or (current_time - last_api_call_time).seconds >= 10:
        sunrise_local, sunset_local, hemisphaere, cloudiness, timezone_offset, azimuth, elevation = API_Abfrage(city)
        api_data_cache[city] = {
            'sunrise_local': sunrise_local,
            'sunset_local': sunset_local,
            'hemisphaere': hemisphaere,
            'cloudiness': cloudiness,
            'timezone_offset': timezone_offset,
            'azimuth': azimuth,
            'elevation': elevation
        }
        last_api_call_time = current_time
    else:
        sunrise_local = api_data_cache[city]['sunrise_local']
        sunset_local = api_data_cache[city]['sunset_local']
        hemisphaere = api_data_cache[city]['hemisphaere']
        cloudiness = api_data_cache[city]['cloudiness']
        timezone_offset = api_data_cache[city]['timezone_offset']
        azimuth = api_data_cache[city]['azimuth']
        elevation = api_data_cache[city]['elevation']

    # Umwandeln von Sonnenauf- und -untergang in dezimale Stunden
    Sonnenaufgang = (sunrise_local + timedelta(hours=timezone_offset)).strftime("%H:%M:%S")
    Sonnenuntergang = (sunset_local + timedelta(hours=timezone_offset)).strftime("%H:%M:%S")
    h, m, s = map(int, Sonnenaufgang.split(":"))
    Sonnenaufgang = round(h + m / 60 + s / 3600, 2)
    h, m, s = map(int, Sonnenuntergang.split(":"))
    Sonnenuntergang = round(h + m / 60 + s / 3600, 2)

    # Lux-Berechnung mit der gegebenen Fensterorientierung
    lux, azimuth, elevation = berechne_lux(
        sunrise_local, sunset_local, current_time, cloudiness, hemisphaere, window_orientation, azimuth, elevation
    )

    # Speichern der neuen Daten in last_data
    last_data = {
        'sunrise': Sonnenaufgang,
        'sunset': Sonnenuntergang,
        'azimuth': azimuth,
        'elevation': elevation,
        'cloudiness': cloudiness,
        'window': window_orientation,
        'lux': lux
    }

    # Datensatz zum Speichern
    data = {
        'timestamp': current_time,
        'city': city,
        'sunrise': Sonnenaufgang,
        'sunset': Sonnenuntergang,
        'azimuth': azimuth,
        'elevation': elevation,
        'cloudiness': cloudiness,
        'window': window_orientation,
        'lux': lux
    }

    return data, last_api_call_time, last_data


# Speichern der Daten in einer CSV-Datei
def save_data_to_csv(data):
    df = pd.DataFrame([data])
    df.to_csv(csv_path, mode='a', header=False, index=False)


# Funktion zum Sammeln von Daten für eine Stunde
def collect_data_for_one_hour(cities, window_orientations, interval_seconds=1):
    start_time = time.time()
    end_time = start_time + 260000  # 1 Stunde

    last_api_call_time_dict = {city: datetime.min for city in cities}
    last_data_dict = {city: {} for city in cities}
    api_data_cache = {}

    while time.time() < end_time:
        for city in cities:
            for orientation in window_orientations:
                data, last_api_call_time, last_data = collect_data(
                    city,
                    last_api_call_time_dict[city],
                    last_data_dict[city],
                    orientation,
                    api_data_cache
                )
                last_api_call_time_dict[city] = last_api_call_time
                last_data_dict[city] = last_data
                save_data_to_csv(data)
                time.sleep(interval_seconds)  # Pause zwischen Fensterorientierungen (z.B. 1 Sekunde)
            time.sleep(5)  # Pause zwischen Städten (optional, hier 5 Sekunden)


# Beispiel-Aufruf
window_orientations = [330, 230, 140, 70]
cities = ["Karlsruhe", "Berlin", "Hamburg", "München", "Köln", "Frankfurt"]

collect_data_for_one_hour(cities, window_orientations)
