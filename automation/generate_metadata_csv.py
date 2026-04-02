import os
import re
import csv

def extract_metadata(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    url = re.search(r'URL: (.*)', content).group(1).strip()
    h1 = re.search(r'H1: (.*)', content).group(1).strip()
    meta_desc = re.search(r'Meta descripción: (.*)', content).group(1).strip()
    keywords = re.search(r'Palabras clave: (.*)', content).group(1).strip()

    # Determine search intention based on filename/title
    search_text = (filepath + " " + h1).lower()
    if "mito" in search_text or "¿" in h1:
        intent = "Desmitificación / Informacional"
    elif any(kw in search_text for kw in ["estrategia", "técnica", "tecnica", "gestión", "gestion", "guía", "guia"]):
        intent = "De Solución / Aplicada"
    else:
        intent = "Informacional / Fundacional"

    return [url, h1, meta_desc, keywords, intent]

def main():
    directory = 'editorial_neurociencia'
    with open('metadata_pilot.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['URL', 'H1', 'Meta descripción', 'Keywords', 'Intención de búsqueda'])

        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.md'):
                writer.writerow(extract_metadata(os.path.join(directory, filename)))

if __name__ == "__main__":
    main()
