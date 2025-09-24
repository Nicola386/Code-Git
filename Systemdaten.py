# Kompletter Inhalt für Systemdaten.py

import subprocess
import datetime as dt
import time
import re
import requests
import platform
from monitorcontrol import get_monitors

def Systemdaten():
    jetzt = dt.datetime.now()
    Datum = jetzt.strftime("%d.%m.%Y")
    Uhrzeit = jetzt.strftime("%H:%M:%S")
    Zeitzone = time.tzname[0]
    offset = -time.altzone / 3600
    return Datum, Uhrzeit, Zeitzone, offset

def monitor():

    def monitor_win():
        helligkeit = None
        kontrast = None
        model = "Kein Monitor gefunden"
        monitors_data = []

        print("Suche nach Monitoren unter Windows...")
        try:
            monitors = list(get_monitors())
        except Exception as e:
            print(f"Fehler bei der Monitorsuche: {e}")
            return helligkeit, kontrast, model, "N/A"

        if not monitors:
            print("Keine Monitore gefunden. Ist DDC/CI im Monitor-Menü aktiviert?")
            return helligkeit, kontrast, model, "N/A"

        print(f"{len(monitors)} Monitor(en) gefunden:\n")

        for i, monitor_obj in enumerate(monitors, 1):
            with monitor_obj:
                try:
                    current_model = monitor_obj.get_vcp_capabilities().get('model', 'Unbekanntes Modell')
                    current_helligkeit = monitor_obj.get_luminance()
                    current_kontrast = monitor_obj.get_contrast()
                    
                    monitors_data.append({
                        "modell": current_model,
                        "helligkeit": current_helligkeit,
                        "kontrast": current_kontrast
                    })
                    print(f"--- Monitor {i} ---")
                    print(f"  Modell:     {current_model}")
                    print(f"  Helligkeit: {current_helligkeit}%")
                    print(f"  Kontrast:   {current_kontrast}%")
                except Exception as e:
                    print(f"Konnte Daten für Monitor {i} nicht abrufen: {e}")
        
        if monitors_data:
            first_monitor = monitors_data[0]
            helligkeit = first_monitor['helligkeit']
            kontrast = first_monitor['kontrast']
            model1 = first_monitor['modell']
            model2 = monitors_data[1]['modell'] if len(monitors_data) > 1 else "N/A"
            return helligkeit, kontrast, model1, model2
        
        return None, None, "Fehler beim Auslesen", "N/A"

    def monitor_linux():
        Helligkeit = {}
        Kontrast = {}
        data = {}
        dis1, dis2 = "N/A", "N/A"

        try:
            result = subprocess.run(["ddcutil", "detect"], capture_output=True, text=True, check=True)
            
            displays = [int(match.group(1)) for match in re.finditer(r"Display\s+(\d+)", result.stdout)]
            
            if not displays:
                print("Keine Monitore via ddcutil gefunden.")
                return {}, {}, dis1, dis2

            for display in displays:
                cap_result = subprocess.run(["ddcutil", "--display", str(display), "capabilities"], capture_output=True, text=True)
                model_match = re.search(r"Model:\s*(.*)", cap_result.stdout)
                data[f"Display{display}"] = {"Model": model_match.group(1).strip() if model_match else "Unbekannt"}

                brightness_proc = subprocess.run(["ddcutil", "-d", str(display), "getvcp", "10"], capture_output=True, text=True)
                contrast_proc = subprocess.run(["ddcutil", "-d", str(display), "getvcp", "12"], capture_output=True, text=True)
                
                bright_val = re.search(r"current value =\s*(\d+)", brightness_proc.stdout)
                cont_val = re.search(r"current value =\s*(\d+)", contrast_proc.stdout)
                
                if bright_val: Helligkeit[display] = bright_val.group(1)
                if cont_val: Kontrast[display] = cont_val.group(1)

            dis1 = data.get("Display1", {}).get("Model", "N/A")
            dis2 = data.get("Display2", {}).get("Model", "N/A")

        except FileNotFoundError:
            print("Fehler: Der Befehl 'ddcutil' wurde nicht gefunden.")
            print("Stelle sicher, dass ddcutil installiert und im System-PATH ist.")
        except subprocess.CalledProcessError as e:
            print(f"Fehler bei der Ausführung von ddcutil: {e.stderr}")
        except Exception as e:
            print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

        return Helligkeit, Kontrast, dis1, dis2
    
    BS = platform.system()
    
    if BS == "Windows":
        return monitor_win()
    elif BS == "Linux":
        return monitor_linux()
    else:
        print("Betriebssystem nicht unterstützt")
        return None, None, None, None

def Standort():
    try:
        data = requests.get("https://ipinfo.io/json", timeout=5).json()
        ip_address = data.get("ip", "Unbekannt")
        stadt = data.get("city", "Unbekannt")
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Standortabfrage: {e}")
        ip_address, stadt = "Fehler", "Fehler"
    return ip_address, stadt