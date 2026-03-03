import requests
import pandas as pd
import os
import time

# --- CONFIGURATIE ---
# Pas deze lijst aan naar de velden die je in je CSV wilt zien
GEWENSTE_KOLOMMEN = ['dateCreated', 'id', 'name', 'birthDate', 'birthPlace', 'deathDate', 'deathPlace']
FILENAME = 'personen_output.csv'
COUNT_PER_PAGE = 100
BASE_URL = "https://rest.spinque.com/4/oorlogsbronnen/api/lod/e/new_persons/resultpage?config=default"

def scrape_all():
    offset = 0
    total_rows = 0
    
    print(f"Start met scrapen naar {FILENAME}...")

    while True:
        # Bouw URL
        url = f"{BASE_URL}&count={COUNT_PER_PAGE}&offset={offset}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])

            # Stop als er geen resultaten meer zijn
            if not items:
                print("Einde van de data bereikt.")
                break

            # Maak DataFrame
            df = pd.DataFrame(items)

            # Filter op gewenste kolommen (alleen als ze daadwerkelijk bestaan in de JSON)
            aanwezige_kolommen = [col for col in GEWENSTE_KOLOMMEN if col in df.columns]
            df_subset = df[aanwezige_kolommen]

            # Bepaal of we de kolomnamen (header) moeten schrijven
            # Alleen als het bestand nog niet bestaat én het de eerste pagina is
            header_nodig = not os.path.isfile(FILENAME) and offset == 0

            # Opslaan (append mode)
            df_subset.to_csv(FILENAME, mode='a', index=False, header=header_nodig, encoding='utf-8')

            num_added = len(df_subset)
            total_rows += num_added
            print(f"Offset {offset}: {num_added} rijen toegevoegd.")

            # Volgende pagina
            offset += COUNT_PER_PAGE
            
            # Korte pauze voor de server
            time.sleep(0.5)

        except Exception as e:
            print(f"Er ging iets mis bij offset {offset}: {e}")
            break

    print(f"\nKlaar! Totaal aantal rijen in deze sessie: {total_rows}")

if __name__ == "__main__":
    scrape_all()
