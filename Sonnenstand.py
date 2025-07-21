import pvlib
import pytz

def berechne_sonnenstand(latitude, longitude, current_time):
    tz = pytz.timezone('UTC')
    current_time = current_time.astimezone(tz)  # Zeit in UTC konvertieren
    solpos = pvlib.solarposition.get_solarposition(current_time, latitude, longitude)
    azimuth = solpos['azimuth'].values[0]
    elevation = solpos['apparent_elevation'].values[0]
    azimuth=round(azimuth,2)
    elevation=round(elevation,2)
    
    return azimuth, elevation
