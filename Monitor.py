import subprocess
#from monitorcontrol import get_monitors

def Monitor_einstellen(display, h_neu):

    subprocess.run([
         "ddcutil", "--display", str(display), "setvcp", "10", str(h_neu)
    ])
    # monitor=[]
    # monitor.set_luminance(h_neu)
    return

def Helligkeit_Regeln(helligkeit,L_max,L_soll):
    
    display=2
    if L_soll > L_max:
        h_neu=100
    else:
        h_neu=L_soll*100/L_max

    h_neu=int(h_neu)
    if h_neu != helligkeit:
        while display > 0:
            Monitor_einstellen(display,h_neu)
            display -=1
    return

def Buckets_Regelung(E_mon,helligkeit):
    
    if E_mon <= 10:
        h_neu= 10
    elif E_mon <= 50:
        h_neu= 25
    elif E_mon <= 100:
        h_neu= 40
    elif E_mon<= 300:
        h_neu= 55
    elif E_mon <= 400:
        h_neu= 70
    elif E_mon <= 650:
        h_neu= 85
    elif E_mon <= 2000:
        h_neu= 100
    else:
        h_neu=100

    display=2
    if h_neu != helligkeit:
        while display > 0:
            Monitor_einstellen(display,h_neu)
            display -=1
    return 

