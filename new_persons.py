import requests
import pandas as pd
import os
import time

# --- CONFIGURATIE ---
GEWENSTE_KOLOMMEN = ['dateCreated', 'id', 'name', 'birthDate', 'birthPlace', 'deathDate', 'deathPlace']
FOLDER = 'data'
FILENAME = os.path.join(FOLDER, 'new_persons.csv')
COUNT_PER_PAGE = 100
BASE_URL = "https://rest.spinque.com/4/oorlogsbronnen/api/lod/e/new_persons/resultpage?config=default"

# Zorg dat de map 'data' bestaat
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

def scrape_all():
    offset = 0
    total_rows = 0
    
    print(f"Start met scrapen naar {FILENAME}...")

    while True:
        url = f"{BASE_URL}&count={COUNT_PER_PAGE}&offset={offset}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])

            if not items:
                print("Einde van de data bereikt.")
                break

            # Data uitpakken uit de 'tuple'
            extracted_data = []
            for item in items:
                if 'tuple' in item and len(item['tuple']) > 0:
                    person_info = item['tuple'][0]
                    extracted_data.append(person_info)
            
            # Maak de DataFrame
            df = pd.DataFrame(extracted_data)

            # --- DE CRUCIALE FIX VOOR DE KOLOMMEN ---
            # reindex dwingt de DataFrame om alle GEWENSTE_KOLOMMEN te gebruiken.
            # fillna('') zorgt dat ontbrekende velden echt leeg zijn (geen "NaN").
            df_subset = df.reindex(columns=GEWENSTE_KOLOMMEN).fillna('')

            # Bepaal of de header nodig is
            header_nodig = not os.path.isfile(FILENAME) and offset == 0

            # Opslaan (append mode)
            df_subset.to_csv(FILENAME, mode='a', index=False, header=header_nodig, encoding='utf-8')

            num_added = len(df_subset)
            total_rows += num_added
            print(f"Offset {offset}: {num_added} personen verwerkt.")

            offset += COUNT_PER_PAGE
            time.sleep(0.5)

        except Exception as e:
            print(f"Fout opgetreden bij offset {offset}: {e}")
            break

    print(f"\nKlaar! Totaal aantal rijen verwerkt: {total_rows}")

if __name__ == "__main__":
    scrape_all()
