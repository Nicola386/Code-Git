import numpy as np
import math
from API_Abfrage import API_Abfrage
from Systemdaten import Standort

def einfallendes_Licht(moebel,Fenster_ausr,Fenster_pos):
    ip_address,stadt=Standort()
    city=stadt
    sunrise_local, sunset_local, hemisphaere, cloudiness, timezone_offset, azimuth, elevation,weather_discription = API_Abfrage(city)

    #Reflexionswert
    if moebel=='hell':
        R=0.9
    elif moebel=='mittel':
        R=0.45
    elif moebel=='dunkel':
        R=0.2   

    # Fenster Ausrichtung
    gamma_s_rad = np.radians(elevation)               # Sonnenhöhe (Solar Altitude) in Radiant
    psi = Fenster_ausr                                # Orientierung Fenster (Himmelsrichtung)
    gamma_rad = np.radians(azimuth - psi + 180)       # Winkel zwischen Fenster und Sonne in Radiant

    # Einfallswinkel der Sonne auf vertikale Fläche (für I_VT direkte Komponente)
    # Cosinus des Einfallswinkels theta_v auf eine vertikale Fläche
    cos_theta_v = (np.cos(gamma_s_rad) * np.cos(gamma_rad))
    # Sicherstellen, dass der Wert im gültigen Bereich für arccos liegt
    cos_theta_v = np.clip(cos_theta_v, -1.0, 1.0) 
    theta_v_rad = np.arccos(cos_theta_v)
    theta_v_deg = np.degrees(theta_v_rad)             # Bogenmaß in Gradmaß umrechnen (nur zur Anzeige)

    ######################################################
    # Werte für A und B provisorisch später aus data Datei
    ######################################################
    A=1085
    B=0.207
    # E_DN (Direct Normal Irradiance) in W/m^2
    E_DN = A / (np.exp(B / np.sin(gamma_s_rad)))
    E_DN = round(E_DN, 2)

    # Luminöse Effizienz (eta) 
    CF=cloudiness
    eta = 115 * (CF / 100) + 59.3 * (gamma_s_rad)**0.1252 * (1 - (CF/ 100))
    
    # Diffuse Beleuchtung (E_d)
    # E_d ist die diffuse BESTRAHLUNGSSTÄRKE in W/m^2 auf einer HORIZONTALEN Fläche
    # Y hängt von cos(theta_v) ab
    if cos_theta_v > -0.2:
        Y=0.55+0.437*cos_theta_v+0.313*(cos_theta_v)**2
    else:
        Y=0.45
    
    ######################################################
    # Werte für C provisorisch später aus data Datei
    ######################################################
    C=0.136
    E_d = C * Y * E_DN
    E_d=round(E_d,2)
    # Sonneneinstrahlung (Bestrahlungsstärke in W/m^2)
    # Korrektur der Berechnung von I_HT und I_VT
    # I_HT = Direkte horizontale Bestrahlungsstärke + Diffuse horizontale Bestrahlungsstärke
    # Direkte horizontale Bestrahlungsstärke = E_DN * sin(gamma_s)
    # Diffuse horizontale Bestrahlungsstärke = E_d (wenn E_d tatsächlich die diffuse ist)
    E_DNV=E_DN*cos_theta_v
    I_VT = E_DNV + E_d
    I_VT = round(I_VT, 2)

    #Daylightfaktor Parameter
    tau=0.7             #Lichttransmission Fenster
    M=0.8               #Wartungsfaktor (wie verschmutzt)
    At=28.7             #28.7 Raumoberflächen [m²]               
    Ag=2                #Fenster Größe [m²]
    
    # Der Parameter theta in Formel (13) ist "the vertical angle of visible sky from the center of the window".
    # Dies ist NICHT der Sonnen-Einfallswinkel (theta_v_rad).
    # Ein typischer Wert könnte 30-60 Grad sein, je nach Fenstertyp und -höhe.
    # Angenommen, das Fenster ist so, dass ein bestimmter Winkel des Himmels sichtbar ist.
    # Der Winkel muss im Bogenmaß (Radiant) sein, da er in der Formel nicht mit sin/cos etc. verwendet wird.
    theta_sky_angle_rad = np.radians(45) # Beispielwert: 45 Grad vertikaler Himmelblick vom Fenster


    # Einfallendes Licht E_i 
    E_i = (Ag * tau * theta_sky_angle_rad * M * I_VT * eta) / (At * (1 - R**2) * 0.396 * 100)
    E_i = round(E_i, 2)

    ######################################################
    # Debuggen
    print("Sonnenhöhe (Grad):", elevation)
    print("Sonnenhöhe (Rad):", gamma_s_rad)
    print("azimuth:", azimuth)
    print("cos_theta_v:", cos_theta_v)
    print("theta_v (Grad):", theta_v_deg)
    print("theta_v (Rad):", theta_v_rad)
    print("CF:", CF)
    print("eta:", eta)
    print("Y:", Y)
    print("E_d (Diffuse Horizontale Bestrahlungsstärke W/m^2):", E_d)
    print("E_DN (Direct Normal Irradiance W/m^2):", E_DN)
    print("E_DNV",E_DNV)
    print("I_VT (Vertikale Bestrahlungsstärke W/m^2):", I_VT)
    print("Theta Sky Angle (Rad):", theta_sky_angle_rad)
    print("E_i (Einfallendes Licht):", E_i)
    ######################################################

    return E_i,weather_discription,azimuth,elevation

################################################
#Debuggen
einfallendes_Licht('hell', 230, 0)
################################################