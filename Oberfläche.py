import numpy as np
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QDialog, QGraphicsScene,QLabel
from PyQt5.QtGui import QPixmap
import sys
from Berechnung import einfallendes_Licht
from Systemdaten import Standort
from Systemdaten import monitor


class MyWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("Oberfläche.ui", self)

        self.selected_angle = None  # Speichert den Fensterwinkel
        self.bildpfad = "arbeitsplatz.png"

        # Eingabe-Button verbinden
        self.pushButton_eingabe.clicked.connect(self.eingabe_auswerten)
        
        ###########Läuft nicht gut################
        #Timer alle 10sec
        #self.timer=QTimer(self)
        #self.timer.timeout.connect(self.eingabe_auswerten)
        #self.timer.start(10000)
        #############################################

    def eingabe_auswerten(self):

        grad = self.spinBox.text()
        rollladen = self.comboBox.currentText()
        licht = self.comboBox_2.currentText()
        moebel=self.comboBox_3.currentText()
        winkel=self.dial.value()
        Fenster_pos=(winkel+180)%360
        

        #Eingabe
        Ausgabe1=(
            f"Ausrichtung:{grad}\n"
            f"Rollladen:{rollladen}\n"
            f"Licht:{licht}\n"
            f"Möbel:{moebel}\n"
            f"Fensterwinkel:{Fenster_pos}\n"
    
        )
        Ausgabe = self.findChild(QLabel, 'Ausgabe')
        Ausgabe.setText(Ausgabe1)

        #Berechnung
        Fenster_ausr=int(grad)
        E_i,weather_discription,azimuth,elevation=einfallendes_Licht(moebel,Fenster_ausr,Fenster_pos)

        #Tim Funktion
        if Fenster_pos <=180:
            F=1/180*Fenster_pos  
        elif Fenster_pos>180:
            F=-1/180*Fenster_pos+2
        D_i=E_i*F
        D_i=round(D_i,2)
        
        Ausgabe2=(
            f"Einfallendes Licht: {E_i} Lux\n"
            f"Licht auf Monitor: {D_i} Lux\n"


        )
        LuxWert = self.findChild(QLabel, 'LuxWert')
        LuxWert.setText(Ausgabe2)
        
        #Api_Werte
        
        API=(
            f"Wetter: {weather_discription}\n"
            f"Sonnenposition: {azimuth} in Grad\n"
            f"Sonnenhöhe: {elevation} in Grad\n"

        )

        WetterDaten= self.findChild(QLabel, 'WetterDaten')
        WetterDaten.setText(API)

        #Systemdaten
        ip_adresse,stadt=Standort()
        Helligkeit,Kontrast,data=monitor()
        Dis1=data["Display1"]["Model"]
        Dis2=data["Display2"]["Model"]
        Ausgabe3=(
            f"IP-Adresse:{ip_adresse}\n"
            f"Stadt:{stadt}\n\n"
             f"Monitor1-Model: {Dis1}\n"
            f"Monitor-Helligkeit:{Helligkeit[1]}\n"
            f"Monitor-Kontrast:{Kontrast[1]}\n\n"
            f"Monitor2-Model: {Dis2}\n"
            f"Monitor-Helligkeit:{Helligkeit[2]}\n"
            f"Monitor-Kontrast:{Kontrast[2]}\n"
        )

        Systemdaten = self.findChild(QLabel, 'Systemdaten')
        Systemdaten.setText(Ausgabe3)




        # Bildgröße nur anzeigen, wenn vorhanden
        if hasattr(self, "geladenes_bild"):
            print("Bildgröße (px):", self.geladenes_bild.width(), "x", self.geladenes_bild.height())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
