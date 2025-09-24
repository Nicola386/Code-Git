from monitorcontrol import get_monitors
from monitorcontrol.vcp import VCPError
import platform

#BS=platform.system()
#print(BS)


def get_monitor_details():
    """
    Sucht alle Monitore und gibt deren Modell, Helligkeit und Kontrast aus.
    """
    print("Suche nach Monitoren...")
    
    try:
        monitors = list(get_monitors())
    except Exception as e:
        print(f"Fehler bei der Monitorsuche: {e}")
        return

    if not monitors:
        print("Keine Monitore gefunden. Ist DDC/CI im Monitor-Menü aktiviert?")
        return

    print(f"{len(monitors)} Monitor(en) gefunden:\n")

    for i, monitor in enumerate(monitors, 1):
        # Der 'with'-Block stellt eine sichere Verbindung zum Monitor her
        with monitor:
            try:
                # 1. Modellname aus den "Capabilities" abrufen
                model = monitor.get_vcp_capabilities().get('model', 'Unbekanntes Modell')

                # 2. Helligkeit abrufen (VCP Code 0x10)
                helligkeit = monitor.get_luminance()

                # 3. Kontrast abrufen (VCP Code 0x12)
                kontrast = monitor.get_contrast()
                
                # Ergebnisse für den aktuellen Monitor ausgeben
                print(f"--- Monitor {i} ---")
                print(f"  Modell:     {model}")
                print(f"  Helligkeit: {helligkeit}%")
                print(f"  Kontrast:   {kontrast}%")
                print() # Leerzeile für bessere Lesbarkeit

            except VCPError as e:
                # Fehlermeldung, falls ein Wert nicht gelesen werden konnte
                print(f"Konnte Daten für Monitor {i} nicht vollständig abrufen: {e}")
            except Exception as e:
                print(f"Ein unerwarteter Fehler ist bei Monitor {i} aufgetreten: {e}")

if __name__ == "__main__":
    get_monitor_details()