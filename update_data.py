import json
import os
import csv
import datetime

# Input file
input_file = "report.json"
output_file = "correct_most_recent_report.json"

# Read the content from report.json
with open(input_file, "r") as file:
    lines = file.readlines()

# Parse each line as a JSON object
collections = [json.loads(line) for line in lines]

# Loop through each collection and clean the content
for collection in collections:
    if "content" in collection:
        for item in collection["content"]:
            # For each dictionary in the content list, replace the key
            for key in list(item.keys()):
                    new_key = key.replace("https://personsincontext.org/model#", "").replace("organizationsWO2/", "")
                    item[new_key] = item.pop(key)

# Wrap the collections in a top-level object
result = {"collections": collections}

# Write the result to correct.json
with open(output_file, "w") as file:
    json.dump(result, file, indent=4)

print(f"Cleaned JSON data saved to {output_file}")

with open('correct_most_recent_report.json') as f:
   data = json.load(f)

# Verzamel alle unieke keys uit de `content`-arrays
unique_keys = set()
for collection in data["collections"]:
    for item in collection["content"]:
        unique_keys.update(item.keys())
        
print(unique_keys)

for term in unique_keys:
        filename = f"data/{term}.csv"
        if not os.path.exists(filename):
            print(f"Creating file: {filename}")
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["date"])
        else:
            print(f"File already exists: {filename}")

# Haal alle collectie namen op
collection_names = {collection['collection'] for collection in data['collections']}

# Verkrijg een lijst van alle CSV-bestanden in de 'data' map
csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]

# Doorloop elk CSV-bestand in de map
for filename in csv_files:
    filepath = os.path.join('data', filename)
    
    # Open het CSV-bestand en lees de bestaande gegevens
    with open(filepath, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        existing_columns = reader.fieldnames
        rows = list(reader)  # Lees alle rijen in het geheugen

    # Voeg nieuwe kolommen toe voor collecties die nog niet bestaan in het bestand
    new_columns = collection_names - set(existing_columns)  # Collecties die nog geen kolom hebben
    if new_columns:
        
        # Voeg de nieuwe kolommen toe aan de header
        existing_columns.extend(new_columns)
        
        # Maak een tijdelijke lijst van rijen met lege velden voor de nieuwe kolommen
        for row in rows:
            for new_column in new_columns:
                row[new_column] = ""  # Voeg lege waarde toe voor de nieuwe kolom
        
        # Schrijf de nieuwe CSV met de extra kolommen
        with open(filepath, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=existing_columns)
            writer.writeheader()  # Schrijf de header met de nieuwe kolommen
            for row in rows:
                writer.writerow(row)  # Schrijf de rijen (met de oude gegevens en lege velden voor nieuwe kolommen)
        
print("Nu zijn de nieuwe kolommen toegevoegd aan de CSV")

# Haal de huidige datum op in het gewenste formaat
today_date = datetime.datetime.today().strftime('%Y-%m-%d')

# Doorloop elk CSV-bestand in de map
for filename in csv_files:
    filepath = os.path.join('data', filename)
    
    # Open het CSV-bestand en lees de bestaande gegevens
    with open(filepath, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        existing_columns = reader.fieldnames
        rows = list(reader)  # Lees alle rijen in het geheugen

    # Vind het contenttype die overeenkomt met het csv bestand (bijv. "Photograph.csv" -> "Photograph")
    term = filename.split('.')[0]  # Het is de naam van de contenttype (bijv. "Photograph")

    # Zoek de waarde voor deze term in de JSON
    collection_values = {}
    for collection in data['collections']:
        for content in collection['content']:
            for key, value in content.items():
                if key == term:
                    collection_values[collection['collection']] = value

    # Maak een nieuwe rij aan met de datum en de collectie waarden
    new_row = {column: "" for column in existing_columns}  # Begin met een lege rij
    new_row['date'] = today_date  # Voeg de datum toe

    # Vul de waarden in voor de collecties die in de huidige CSV moeten komen
    for collection_name, value in collection_values.items():
        if collection_name in existing_columns:
            new_row[collection_name] = value  # Vul de waarde voor deze collectie in

    # Voeg de nieuwe rij toe aan de bestaande rijen
    rows.append(new_row)

    # Schrijf de nieuwe data terug naar het CSV-bestand
    with open(filepath, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=existing_columns)
        writer.writeheader()  # Schrijf de header
        for row in rows:
            writer.writerow(row)  # Schrijf elke rij (inclusief de nieuwe rij)
    
    print(f"Nieuwe regel toegevoegd aan {filename} voor datum {today_date}")
