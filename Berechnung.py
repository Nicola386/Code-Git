import numpy as np
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




    #Sonnenhöhe
    #delta=np.radians(23)           #Winkel der Sonne relativ zum Äquator
    #L=np.radians(50.09)            #Breitengrad (52 für Berlin)
    #Uhrzeit=15
    #H=np.radians((Uhrzeit-12)*15)      #Stundenwinkel pro h 15 Grad (0 ,Mittags)
    #gamma=np.arcsin(np.cos(L)*np.cos(delta)*np.cos(H)+np.sin(L)*np.sin(delta))
    beta=np.radians(elevation)


    #Fenster Ausrichtung
    alpha=Fenster_ausr                              #Orientierung Fenster
    gamma=np.radians(azimuth-alpha)                 #Winkel zwischen Fenster und Sonne
    gamma_s=np.sin(np.radians(elevation))
    theta_sun=np.radians(azimuth)                   #Winkel Sonne
    sigma=np.radians(90)                            #Neigung Fenster
    #theta=np.arccos(np.sin(gamma)*np.cos(sigma)+np.cos(gamma)*np.sin(sigma)*np.cos(theta_sun-alpha))

    #Einfallswinkel
    theta_v=np.cos(beta)*np.cos(gamma)

    #Sonneneinstrahlung
    CF=cloudiness
    A=0.75                                          #Atmospähre
    I_0=1361                                        #Sonnenkonstante [W/m²]
    I_HT=I_0*A*(1-CF/100)
    I_VT=I_HT/np.tan(theta_v)
    

    #Luminöse Effizienz
    eta=115*(CF/100)+59.3*gamma_s**(0.1252)*(1-CF/100)
    E_VT=I_VT*eta
    E_HT=I_HT*eta
    


    #Daylightfaktor
    tau=0.7             #Lichttransmission Fenster
    M=0.8               #Wartungsfaktor (wie verschmutzt)
    At=28.7             #28.7 Raumoberflächen [m²]               
    Ag=2                #Fenster Größe [m²]

    DF=(Ag*tau*theta_v*M*I_VT)/(At*(1-R**2)*I_HT*0.396)

    #Einfallendes Licht
    E_i=(DF*I_HT*eta)/100
    E_i=round(E_i,2)
    return E_i,weather_discription,azimuth,elevation

#E_i=einfallendes_Licht()
#print(E_i)
