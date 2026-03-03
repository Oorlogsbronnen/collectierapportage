import requests
import pandas as pd
import os
import time

def scrape_all_new_persons(base_url, filename='data/personen_output.csv', count=100):
    offset = 0
    total_added = 0
    file_exists = os.path.isfile(filename)

    print(f"Start met ophalen van data...")

    while True:
        # Bouw de URL op met de huidige offset en gewenste count
        url = f"{base_url}&count={count}&offset={offset}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Pak de lijst met personen uit de 'items' key
            items = data.get('items', [])
            
            # Stop de loop als er geen items meer zijn
            if not items:
                print("Geen nieuwe resultaten meer gevonden. Klaar!")
                break
            
            # Zet om naar DataFrame
            df_page = pd.DataFrame(items)
            
            # Schrijf weg naar CSV (append mode)
            # Header wordt alleen geschreven als het bestand nog niet bestond EN het de eerste pagina is
            should_write_header = not file_exists and offset == 0
            df_page.to_csv(filename, mode='a', index=False, header=should_write_header, encoding='utf-8')
            
            num_items = len(items)
            total_added += num_items
            print(f"Pagina verwerkt (offset {offset}): {num_items} personen toegevoegd.")
            
            # Verhoog de offset voor de volgende ronde
            offset += count
            
            # Optioneel: korte pauze om de server niet te overbelasten
            time.sleep(0.5)

        except Exception as e:
            print(f"Fout bij offset {offset}: {e}")
            break

    print(f"Klaar! In totaal {total_added} rijen verwerkt in {filename}.")

# De basis URL (zonder count en offset parameters, die voegen we zelf toe)
base_api_url = "https://rest.spinque.com/4/oorlogsbronnen/api/lod/e/new_persons/resultpage?config=default"

# Start het proces
scrape_all_new_persons(base_api_url, count=100)
