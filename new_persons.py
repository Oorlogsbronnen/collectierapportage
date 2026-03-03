import requests
import pandas as pd
import os
import time

# --- CONFIGURATIE ---
# De namen moeten exact overeenkomen met de keys in de JSON 'tuple'
GEWENSTE_KOLOMMEN = ['dateCreated', 'id', 'name', 'birthDate', 'birthPlace', 'deathDate', 'deathPlace']
# We zetten het bestand in de 'data' map
FOLDER = 'data'
FILENAME = os.path.join(FOLDER, 'personen_output.csv')
COUNT_PER_PAGE = 100
BASE_URL = "https://rest.spinque.com/4/oorlogsbronnen/api/lod/e/new_persons/resultpage?config=default"

# Zorg dat de map 'data' bestaat voor we beginnen
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

def scrape_all():
    offset = 0
    total_rows = 0
    
    print(f"Start met scrapen naar {FILENAME}...")

    while True:
        # Bouw de URL met offset en count
        url = f"{BASE_URL}&count={COUNT_PER_PAGE}&offset={offset}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])

            # Stop de loop als er geen items meer zijn
            if not items:
                print("Einde van de data bereikt.")
                break

            # --- DATA UITPAKKEN (FLATTENING) ---
            # Omdat de info in 'tuple' staat, moeten we die eruit halen
            extracted_data = []
            for item in items:
                if 'tuple' in item and len(item['tuple']) > 0:
                    # Pak de eerste dictionary uit de lijst in 'tuple'
                    person_info = item['tuple'][0]
                    extracted_data.append(person_info)
            
            # Maak de DataFrame van de uitgepakte lijst
            df = pd.DataFrame(extracted_data)

            # Filter op de gewenste kolommen (check of ze bestaan in de data)
            aanwezige_kolommen = [col for col in GEWENSTE_KOLOMMEN if col in df.columns]
            df_subset = df[aanwezige_kolommen]

            # Bepaal of we de header (kolomnamen) moeten schrijven
            # Alleen als het bestand nog niet bestaat EN het de allereerste pagina is
            header_nodig = not os.path.isfile(FILENAME) and offset == 0

            # Opslaan in 'append' mode
            df_subset.to_csv(FILENAME, mode='a', index=False, header=header_nodig, encoding='utf-8')

            num_added = len(df_subset)
            total_rows += num_added
            print(f"Offset {offset}: {num_added} personen verwerkt.")

            # Verhoog offset voor de volgende pagina
            offset += COUNT_PER_PAGE
            
            # Korte pauze om de API niet te overbelasten
            time.sleep(0.5)

        except Exception as e:
            print(f"Fout opgetreden bij offset {offset}: {e}")
            break

    print(f"\nKlaar! Totaal aantal rijen toegevoegd: {total_rows}")

if __name__ == "__main__":
    scrape_all()
