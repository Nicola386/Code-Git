import subprocess
import datetime as dt
import time
from datetime import datetime
import re
import requests
import json

def Systemdaten():
    jetzt= dt.datetime.now()
    Datum=jetzt.strftime("%d.%m.%Y")
    Uhrzeit=jetzt.strftime("%H:%M:%S")
    Zeitzone=time.tzname[0]
    offset=-time.altzone/3600
    
    return Datum,Uhrzeit,Zeitzone,offset


def monitor():
    try:
        # Befehl zur Monitorerkennung ausführen
        result = subprocess.run(["ddcutil", "detect"], capture_output=True, text=True)
        data={}
        Helligkeit={}
        Kontrast={}
        if result.returncode == 0:
            
            # Displays aus der Ausgabe extrahieren
            displays = [int(match.group(1)) for match in (re.search(r"Display\s+(\d+)", line) for line in result.stdout.splitlines()) if match]
            
            #In Dictionary umwandeln
            for display in displays:
                info= {line.split(":")[0].strip(): line.split(":")[1].strip() 
                        for line in result.stdout.splitlines() if ":" in line}
                data[f"Display{display}"]=info

                # Für jedes Display Helligkeit und Kontrast abrufen und anzeigen
                for display in displays:
                    #print(f"\n  Display {display}")
                    brightness = subprocess.run(["ddcutil", "--display", str(display), "getvcp", "10"], capture_output=True, text=True)
                    contrast = subprocess.run(["ddcutil", "--display", str(display), "getvcp", "12"], capture_output=True, text=True)
                    Helligkeit[display]=brightness.stdout.split(":")[-1].strip()
                    Kontrast[display]=contrast.stdout.split(":")[-1].strip()
                    
                    

        else:
            print(f"Fehler bei der Monitorerkennung: {result.stderr}")

    except Exception as e:
        print(f"Ausnahme beim Ausführen von ddcutil: {e}")
    

    
    
    
    #print(result.stdout)
    #print(data)    
    return Helligkeit,Kontrast,data

def Standort():
    response = requests.get('https://api.ipify.org')
    ip_address = response.text

    response = requests.get(f"https://ipinfo.io/{ip_address}/json")
    data = response.json()
    stadt=data["city"]
    return ip_address,stadt

##############Debuggen############
#monitor()
##############Debuggen############