import numpy as np
import json
from datetime import datetime
from Wetterdaten import API_Abfrage
from Systemdaten import Standort
with open("solardaten.json","r") as f:
    solar_data=json.load(f)

#Solardaten aus Datenstruktur entnehmen
monat=datetime.now().strftime("%b")
daten=solar_data.get(monat)
A = daten["A"]
B = daten["B"]
C = daten["C"]

def einfallendes_Licht(moebel,Fenster_ausr,Fenster_pos):
    #Daylightfaktor Parameter
    tau=0.8             #Lichttransmission Fenster
    M=0.8               #Wartungsfaktor (wie verschmutzt)
    At=28.7             #28.7 Raumoberflächen [m²]               
    Ag=3                #Fenster Größe [m²]
    
    ip_address,stadt=Standort()
    city=stadt
    sunrise_local, sunset_local, cloudiness, azimuth, elevation, weather_description = API_Abfrage(city)

    #############################
    #Validierung
    #############################
    #azimuth=211
    #elevation=33
    #cloudiness=50

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
    gamma_rad =(azimuth-180) - psi                    # Winkel zwischen Fenster und Sonne 

    # Einfallswinkel der Sonne auf vertikale Fläche (für I_VT direkte Komponente)
    # Cosinus des Einfallswinkels theta_v auf eine vertikale Fläche
    cos_theta_v = np.cos(gamma_s_rad*(2*np.pi/360)) *np.cos(gamma_rad*(2*np.pi/360))

    # Sicherstellen, dass der Wert im gültigen Bereich für arccos liegt
    cos_theta_v = np.clip(cos_theta_v, -1.0, 1.0) 
    theta_v_rad = np.arccos(cos_theta_v)
    theta_v_deg = np.degrees(theta_v_rad)             # Bogenmaß in Gradmaß umrechnen (nur zur Anzeige)

   
    # E_DN (Direct Normal Irradiance) in W/m^2
    E_DN = A / (np.exp(B / np.sin(gamma_s_rad)))
    E_DN = round(E_DN, 2)

    # Luminöse Effizienz (eta)  
    CF=cloudiness/100
    eta = 115 * (CF) + 59.3 * (gamma_s_rad)**0.1252 * (1 - (CF))
    #Bewölktheit
    F_CF=1-0.75*(CF)**3.4
    
    # Diffuse Beleuchtung (E_d)
    # E_d ist die diffuse BESTRAHLUNGSSTÄRKE in W/m^2 auf einer HORIZONTALEN Fläche
    # Y hängt von cos(theta_v) ab
    if cos_theta_v > -0.2:
        Y=0.55+0.437*cos_theta_v+0.313*(cos_theta_v)**2
    else:
        Y=0.45
    
 
    E_d = C * Y * E_DN
    E_d=round(E_d,2)
    E_DNV=max(0,E_DN*cos_theta_v)
    
    #Direkter Sonneneinfall
    E_dir=E_DNV*tau*M*eta
    a_M=(Fenster_pos+Fenster_ausr) %360
    gamma_M=(azimuth-180) - a_M
    cos_theta_SM=np.cos(gamma_s_rad*(2*np.pi/360))*np.cos(gamma_M*(2*np.pi/360))

    if (cos_theta_v>0) and (cos_theta_SM>0) and (CF<0.8):
        S=1
    else:
        S=0
    E_dir=E_dir*S*0.1
    E_dir=round(E_dir,2)
    #Boden reflektion
    rho=0.2                           
    E_R=E_DN*(C+np.sin(gamma_s_rad))*rho*0.5
    E_R=round(E_R,2)
    E_t = (E_DNV + E_d+E_R)*F_CF
    E_t = round(E_t, 2)
    
  
    theta_F = np.radians(45) 


    # Einfallendes Licht E_i 
    E_i = (Ag * tau * theta_F * M * E_t * eta) / (At * (1 - R**2) * 0.396 * 100)
    E_i = round(E_i, 2)
    
    #print(CF)
    return ip_address,city,E_dir,E_i,weather_description,azimuth,elevation,sunrise_local, sunset_local

def Kontrast(E_mon,R_D,L_max,L_min):
    
    r_soll=50
    L_r=(E_mon*R_D)/ np.pi
    L_r=round(L_r,2)
    # ###################################
    # ist Kontarst übeflüssig
    L_hell=L_max+L_r
    L_dunkel=L_min+L_r
    r_ist=L_hell/L_dunkel
    r_ist=int(r_ist)
    #######################################

    if r_soll != r_ist:
        L_soll= r_soll*(L_min+L_r)-L_r

    L_soll=round(L_soll,2)
    if L_soll <= 100:
        L_soll=100

    return L_r,L_soll,r_ist


################################################
#Debuggen
# if __name__ == "__main__":
#     result = einfallendes_Licht('hell',90, 0)
# if result:
#     (ip_address,city,E_dir,E_i,weather_description,azimuth,elevation,sunrise_local, sunset_local)=result
#     print("Direkte Sonneneinstrahlung W/m²:",E_dir)
#     print("E_i (Einfallendes Licht):", E_i,)
################################################