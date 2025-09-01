import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QComboBox
# QThread, QObject und pyqtSignal sind für den Hintergrund-Thread notwendig
from PyQt5.QtCore import QTimer, QTime, QThread, QObject, pyqtSignal
from datetime import datetime

# Importieren Sie Ihre bestehenden Module
from Berechnung import einfallendes_Licht, Kontrast
from Systemdaten import Standort, monitor
# Die separate Helligkeit_Regeln Funktion wird nicht mehr benötigt
from Monitor import Monitor_einstellen

richtung_zu_grad = {
    "N": 180, "NO": -135, "O": -90, "SO": -45,
    "S": 0, "SW": 45, "W": 90, "NW": 135
}

# --- WORKER-KLASSE (jetzt für BEIDE Aufgaben zuständig) ---
class Worker(QObject):
    # Signal für die Ergebnisse der Monitor-Regelung
    monitor_results_ready = pyqtSignal(dict)
    # Signal für die Ergebnisse der Lichtberechnung
    licht_results_ready = pyqtSignal(dict)

    def run_monitor_tasks(self, licht_daten, ui_einstellungen, licht_combobox_text, last_set_percent):
        """Regelt die Monitorhelligkeit im Hintergrund."""
        try:
            Lichtwert = 1 if licht_combobox_text == "An" else 0
            if ui_einstellungen.get('auto_modus', False):
                jetzt = QTime.currentTime()
                Lichtwert = 1 if jetzt >= QTime(22, 0) or jetzt < QTime(9, 0) else 0
            #################################################################
            #Lichtwert eventuell mit sonnenaufang und Untergang implementieren
            #
            ##################################################################
            E_k = 500 * Lichtwert
            E_i = licht_daten.get('E_i', 0)

            # Get E_dir from the data dictionary
            E_dir = licht_daten.get('E_dir', 0)

            if ui_einstellungen.get('rollladen') == 'Ja':
                E_i = 0
            
            D_i = round((E_i * 0.535) + (E_k * 0.235)+E_dir)

            R_D = 0.05
            L_max = 250
            L_min = 0.25
            L_r, L_max_neu, r_ist = Kontrast(D_i, R_D, L_max, L_min)
            
            h_neu_percent = max(0, min(100, int(L_max_neu * 100 / L_max)))

            if h_neu_percent != last_set_percent:
                print(f"Änderung erkannt: Helligkeit wird von {last_set_percent}% auf {h_neu_percent}% gesetzt.")
                Monitor_einstellen(1, h_neu_percent)
                Monitor_einstellen(2, h_neu_percent)
            
            aktuelle_helligkeit, aktueller_kontrast, data = monitor()
            
            results = {
                'E_i': E_i, 'E_k': E_k, 'D_i': D_i, 'L_r': L_r,
                'L_max_neu': L_max_neu, 'r_ist': r_ist,
                'aktuelle_helligkeit': aktuelle_helligkeit,
                'aktueller_kontrast': aktueller_kontrast, 'data': data,
                'last_set_percent': h_neu_percent
            }
            self.monitor_results_ready.emit(results)
        except Exception as e:
            print(f"Fehler bei Monitor-Task: {e}")

    def run_licht_berechnung(self, ui_einstellungen):
        """Berechnet das einfallende Licht im Hintergrund."""
        try:
            print(f"Licht- und Wetterdaten werden im Hintergrund berechnet ({datetime.now().strftime('%H:%M:%S')})...")
            moebel = ui_einstellungen.get('moebel', 'Mittel')
            grad = ui_einstellungen.get('grad', 0)
            fenster_pos = ui_einstellungen.get('fenster_pos', 180)
            E_dir,E_i, wetter, azimuth, elevation,sunrise_local, sunset_local = einfallendes_Licht(moebel, grad, fenster_pos)
           
            licht_results = {
                'E_dir':E_dir,'E_i': E_i, 'wetter': wetter, 'azimuth': azimuth, 'elevation': elevation ,'sunrise_local':sunrise_local.strftime('%H:%M:%S'),'sunset_local':sunset_local.strftime('%H:%M:%S')
            }
            self.licht_results_ready.emit(licht_results)
        except Exception as e:
            print(f"Fehler bei Lichtberechnung: {e}")


class MyWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("Oberfläche.ui", self)

        self.standort_daten = None 
        self.licht_und_wetter_daten = None 
        self.ui_einstellungen = {}
        self.last_set_percent = -1 

        self.licht_combobox = self.findChild(QComboBox, 'comboBox_2')
        self.wetter_label = self.findChild(QLabel, 'WetterDaten')
        self.lux_label = self.findChild(QLabel, 'LuxWert')
        self.system_label = self.findChild(QLabel, 'Systemdaten')

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.regel_timer = QTimer(self)
        self.regel_timer.timeout.connect(self.trigger_monitor_update)
        
        self.licht_timer = QTimer(self)
        self.licht_timer.timeout.connect(self.trigger_licht_update)
        
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.trigger_licht_update)

        self.worker.monitor_results_ready.connect(self.update_ui_with_monitor_results)
        self.worker.licht_results_ready.connect(self.update_ui_with_licht_results)

        self.Himmelsrichtung.buttonClicked.connect(self.update_ui_einstellungen)
        self.comboBox.currentIndexChanged.connect(self.update_ui_einstellungen)
        self.comboBox_3.currentIndexChanged.connect(self.update_ui_einstellungen)
        self.dial.valueChanged.connect(self.update_ui_einstellungen)
        self.checkBox.stateChanged.connect(self.update_ui_einstellungen)

        app.aboutToQuit.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.start()

        self.pushButton_eingabe.clicked.connect(self.start_regelung)

    def update_ui_einstellungen(self):
        old_grad = self.ui_einstellungen.get('grad')
        old_fenster_pos = self.ui_einstellungen.get('fenster_pos')
        old_moebel = self.ui_einstellungen.get('moebel')

        checked_button = self.Himmelsrichtung.checkedButton()
        richtung = checked_button.text() if checked_button else "N"
        
        self.ui_einstellungen['grad'] = richtung_zu_grad.get(richtung, 0)
        self.ui_einstellungen['rollladen'] = self.comboBox.currentText()
        self.ui_einstellungen['moebel'] = self.comboBox_3.currentText()
        self.ui_einstellungen['fenster_pos'] = (self.dial.value() + 180) % 360
        self.ui_einstellungen['auto_modus'] = self.checkBox.isChecked()
        
        daylight_setting_changed = (
            self.ui_einstellungen['grad'] != old_grad or
            self.ui_einstellungen['fenster_pos'] != old_fenster_pos or
            self.ui_einstellungen['moebel'] != old_moebel
        )

        if daylight_setting_changed and self.licht_timer.isActive():
            self.debounce_timer.start(400)

    def start_regelung(self):
        if not self.standort_daten:
            print("Standort wird einmalig abgerufen...")
            ip, stadt = Standort()
            self.standort_daten = {'ip': ip, 'stadt': stadt}

        self.update_ui_einstellungen()
        print("Initiale Lichtberechnung wird ausgeführt...")
        self.trigger_licht_update()

        if not self.licht_timer.isActive():
            self.licht_timer.start(3600 * 1000) 
            print("Stündlicher Timer für Lichtberechnung gestartet.")

        if not self.regel_timer.isActive():
            self.regel_timer.start(6000)
            print("Regel-Timer für Helligkeit gestartet (Intervall: 6 Sekunden).")
            
        self.pushButton_eingabe.setEnabled(False)
        self.pushButton_eingabe.setText("Regelung aktiv")

    def trigger_licht_update(self):
        """Gibt dem Worker den Auftrag zur Lichtberechnung."""
        if self.ui_einstellungen:
            self.worker.run_licht_berechnung(self.ui_einstellungen.copy())

    def update_ui_with_licht_results(self, licht_results):
        """Empfängt die Licht-Ergebnisse und aktualisiert die UI."""
        self.licht_und_wetter_daten = licht_results
        self.wetter_label.setText(
            f"Wetter: {licht_results['wetter']}\n"
            f"Sonnenposition: {licht_results['azimuth']}°\n"
            f"Sonnenhöhe: {licht_results['elevation']}°\n"
            f"Sonnenaufgang: {licht_results['sunrise_local']}\n"
            f"Sonnenuntergang: {licht_results['sunset_local']}\n"
        )

    def trigger_monitor_update(self):
        if self.licht_und_wetter_daten and self.ui_einstellungen:
            self.worker.run_monitor_tasks(
                self.licht_und_wetter_daten.copy(),
                self.ui_einstellungen.copy(),
                self.licht_combobox.currentText(),
                self.last_set_percent
            )

    def update_ui_with_monitor_results(self, results):
        self.last_set_percent = results['last_set_percent']

        dis1_modell = results['data'].get("Display1", {}).get("Model", "N/A")
        dis2_modell = results['data'].get("Display2", {}).get("Model", "N/A")

        self.lux_label.setText(
            f"Natürliches Licht: {results['E_i']} Lux\n"
            f"Künstliches Licht: {results['E_k']} Lux\n"
            f"Licht auf Monitor: {results['D_i']} Lux\n"
            f"Reflektiertes Licht: {round(results['L_r'], 2)} cd/m²\n"
            f"Ziel-Helligkeit: {round(results['L_max_neu'], 2)} cd/m²\n"
            f"Ist-Kontrast: {results['r_ist']}\n"
        )

        self.system_label.setText(
            f"IP-Adresse: {self.standort_daten['ip']}\nStadt: {self.standort_daten['stadt']}\n\n"
            f"Monitor 1: {dis1_modell}\n"
            f"  Helligkeit: {results['aktuelle_helligkeit'].get(1, 'N/A')}\n"
            f"  Kontrast: {results['aktueller_kontrast'].get(1, 'N/A')}\n\n"
            f"Monitor 2: {dis2_modell}\n"
            f"  Helligkeit: {results['aktuelle_helligkeit'].get(2, 'N/A')}\n"
            f"  Kontrast: {results['aktueller_kontrast'].get(2, 'N/A')}\n"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
