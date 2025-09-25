import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton
from Berechnung import einfallendes_Licht ,Kontrast
from Systemdaten import Standort, monitor
from Monitor import Helligkeit_Regeln,Buckets_Regelung
from datetime import datetime ,time

richtung_zu_grad = {
    "N": 180, 
    "NO": -135, 
    "O": -90, 
    "SO": -45,
    "S": 0, 
    "SW": 45, 
    "W": 90, 
    "NW": 135
}
richtung_zu_winkel={
    "vorne":180,
    "vr":-135,
    "rechts":-90,
    "rh":-45,
    "hinten":0,
    "lh":45,
    "links":90,
    "vl":135

}
Entfernung_zu_Fenster={
    "Nah am Fenster (<2m)":1,
    "Mitte des Raumes (2m-4m)":0.5,
    "entfernt vom Fenster (>4m)":0.2

}
class MyWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("Oberfläche.ui", self)
        
        self.pushButton_eingabe.clicked.connect(self.eingabe_auswerten)

    def eingabe_auswerten(self):
        # Aktiver Button aus ButtonGroup "Himmelsrichtung"
        checked_button = self.Himmelsrichtung.checkedButton()
        richtung = checked_button.text() if checked_button else "N"
        grad = richtung_zu_grad.get(richtung, 0)
        #Button aus ButtonGroup "Fenster_pos"
        fenster=self.Fenster_pos.checkedButton()
        fenster_pos=fenster.text() if fenster else "vorne"
        winkel=richtung_zu_winkel.get(fenster_pos,0)

        Entfernung=self.comboBox_4.currentText()
        d_f=Entfernung_zu_Fenster.get(Entfernung,0)

        SK=self.spinBox_2.value()
        L_max=self.spinBox.value()
        Kein_Fenster=self.checkBox_2.isChecked()
        rollladen = self.comboBox.currentText()
        Licht = self.comboBox_2.currentText()
        moebel = self.comboBox_3.currentText()
        Auto_Modus=self.checkBox.isChecked()
        Buckets=self.checkBox_3.isChecked()

        

        K = 1 if self.comboBox_2.currentText() == "An" else 0
        Licht = "An" if K else "Aus"

        J=0 if (self.comboBox.currentText()== "Ja") or (Kein_Fenster==True)else 1
        rollladen="Nein" if J else "Ja"

        if Auto_Modus:
            jetzt = datetime.now().time()
            K = int(jetzt >= time(22, 0) or jetzt < time(9, 0))
            Licht = "An" if K else "Aus"
        
        L_min=L_max/SK

        # Ausgabe
        self.findChild(QLabel, 'Ausgabe').setText(
            f"Himmelsrichtung: {grad}°\n"
            f"Rollladen: {rollladen}\n"
            f"Licht: {Licht}\n"
            f"Möbel: {moebel}\n"
            f"Monitorausrichtung: {winkel}\n"
            f"Max. Monitor Helligkeit: {L_max}\n"
            f"Min. Monitor Helligkeit: {L_min}\n"
            f"Entfernung zu Fenster: {Entfernung}"
        )

        ip,stadt,E_dir,E_i,weather_description,azimuth,elevation,sunrise_local, sunset_local = einfallendes_Licht(moebel, grad, winkel)
        E_k=500
        E_k=E_k*K
        E_i=E_i*J*d_f
        E_dir=E_dir*J

        E_mon = round((E_i*0.535)+(E_k*0.235)+(E_dir))
        E_s=round(E_i+E_k+E_dir)

        R_D=0.05

     
        L_r,L_max_neu,r_ist=Kontrast(E_mon,R_D,L_max,L_min)

        helligkeit, kontrast, dis1,dis2 = monitor()
        

        if Buckets:
            Buckets_Regelung(E_mon,helligkeit)
        else:
            Helligkeit_Regeln(helligkeit,L_max,L_max_neu)

        self.findChild(QLabel, 'LuxWert').setText(
            f"natürliches Licht: {E_i} Lux\n"
            f"Künstliches Licht: {E_k} Lux\n"
            f"Direkte Sonneneinstrahlung: {E_dir} Lux\n"
            f"Licht auf Monitor: {E_mon} Lux\n"
            f"Licht auf Schreibtisch: {E_s}\n"
            f"Reflektiertes Licht: {L_r} cd/m²\n"
            f"neue max Heligkeit: {L_max_neu} cd/m²\n"
            f"ist Kontrast: {r_ist}\n"
        )

        self.findChild(QLabel, 'WetterDaten').setText(
            f"Wetter: {weather_description}\n"
            f"Sonnenposition: {azimuth}°\n"
            f"Sonnenhöhe: {elevation}°\n"
            f"Sonnenaufgang: {sunrise_local.strftime('%H:%M:%S')}\n"
            f"Sonnenuntergang: {sunset_local.strftime('%H:%M:%S')}\n"
        )

        self.findChild(QLabel, 'Systemdaten').setText(
            f"IP-Adresse: {ip}\nStadt: {stadt}\n\n"
            f"Monitor1: {dis1}, \nHelligkeit: {helligkeit[1]}, \nKontrast: {kontrast[1]}\n\n"
            f"Monitor2: {dis2}, \nHelligkeit: {helligkeit[2]}, \nKontrast: {kontrast[2]}\n"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
