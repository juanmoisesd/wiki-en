import json
import os
import re

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def generate_jsonld(record):
    """Generates a Schema.org Dataset object from Zenodo record metadata."""
    metadata = record.get('metadata', {})
    title = metadata.get('title', 'Untitled')
    doi = metadata.get('doi') or metadata.get('prereserve_doi', {}).get('doi')
    description = metadata.get('description', '')
    pub_date = metadata.get('publication_date', '')

    author = {
        "@type": "Person",
        "name": "Juan Moisés de la Serna",
        "givenName": "Juan Moisés",
        "familyName": "De la Serna",
        "identifier": "https://orcid.org/0000-0002-8401-8018",
        "affiliation": {
            "@type": "Organization",
            "name": "Universidad Internacional de La Rioja (UNIR)"
        }
    }

    jsonld = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": title,
        "description": description,
        "url": f"https://zenodo.org/record/{record['id']}",
        "identifier": doi,
        "creator": author,
        "publisher": {
            "@type": "Organization",
            "name": "Zenodo"
        },
        "datePublished": pub_date,
        "license": "https://creativecommons.org/licenses/by/4.0/"
    }
    return jsonld

def generate_all(records_json_path, output_dir='metadata/jsonld'):
    """Bulk generates JSON-LD files for all Zenodo records."""
    os.makedirs(output_dir, exist_ok=True)
    with open(records_json_path, 'r') as f:
        records = json.load(f)

    count = 0
    for r in records:
        title = r.get('metadata', {}).get('title', str(r['id']))
        filename = f"{slugify(title)}.jsonld"
        if len(filename) > 100:
            filename = filename[:90] + "-" + str(r['id']) + ".jsonld"

        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
             filename = f"{slugify(title)}-{r['id']}.jsonld"
             filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(generate_jsonld(r), f, indent=2)
        count += 1

    return count

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 generate_jsonld_bulk.py <RECORDS_JSON>")
    else:
        c = generate_all(sys.argv[1])
        print(f"Generated {c} JSON-LD files.")
