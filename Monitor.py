import subprocess
import requests
from bs4 import BeautifulSoup

def Monitor_einstellen(display, h_neu):

    subprocess.run([
        "ddcutil", "--display", str(display), "setvcp", "10", str(h_neu)
    ])
    return

def Helligkeit_Regeln(helligkeit,L_max,L_max_neu):
    
    display=2
    h_neu=L_max_neu*100/L_max
    h_neu=int(h_neu)
    if h_neu != helligkeit:
        while display > 0:
            Monitor_einstellen(display,h_neu)
            display -=1
    return



# def search_monitor(model_name):
#     # 1. Suche nach dem Modell und extrahiere die ID
#     search_url = f"https://www.displayspecifications.com/en/search?query={model_name}"
#     headers = {"User-Agent": "Mozilla/5.0"}
    
#     try:
#         # Suche durchführen
#         search_response = requests.get(search_url, headers=headers)
#         search_soup = BeautifulSoup(search_response.text, 'html.parser')
        
#         # Ersten Treffer auswählen (Annahme: erstes Ergebnis ist korrekt)
#         first_result = search_soup.find("a", class_="model-listing-container")
#         if not first_result:
#             return {"error": "Modell nicht gefunden"}
        
#         model_url = first_result["href"]  # URL wie /en/model/9536166d
#         model_id = model_url.split("/")[-1]  # Extrahiere ID (9536166d)

#         # 2. Lade die Spezifikationsseite
#         spec_url = f"https://www.displayspecifications.com{model_url}"
#         spec_response = requests.get(spec_url, headers=headers)
#         spec_soup = BeautifulSoup(spec_response.text, 'html.parser')

#         #Helligkeit und Coating
#         brightness = spec_soup.find("td", string="Brightness").find_next("td").get_text(strip=True)
#         coating = spec_soup.find("td", string="Coating").find_next("td").get_text(strip=True)

#         return {
#             "Model": model_name,
#             "Max Brightness": brightness,
#             "Coating": coating,
#             "Source URL": spec_url
#         }

#     except Exception as e:
#         return {"error": f"Fehler: {str(e)}"}


# print(search_monitor("241B8QJEB"))  