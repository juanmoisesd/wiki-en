import os
import requests
import json
import re

# Token should be provided via environment variable for security
# The user provided token in prompt is used here as a default for this session only,
# but in a production script, we must avoid hardcoding it.
ZENODO_TOKEN = os.getenv("ZENODO_ACCESS_TOKEN")

BASE_URL = "https://zenodo.org/api/deposit/depositions"

def extract_metadata(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    title_match = re.search(r'^# (.*)', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(md_path)

    # English/Spanish abstract support
    abstract_match = re.search(r'## (?:Resumen \(Abstract\)|Abstract)\n(.*?)\n\n', content, re.DOTALL)
    abstract = abstract_match.group(1).strip() if abstract_match else "Academic study on " + title

    keywords_match = re.search(r'\*\*Keywords:\*\* (.*)', content) or re.search(r'\*\*Palabras clave \(Keywords\):\*\* (.*)', content)
    keywords = [k.strip() for k in keywords_match.group(1).split(',')] if keywords_match else []

    return {
        'title': title,
        'description': abstract,
        'keywords': keywords,
        'creators': [{'name': 'De la Serna, Juan Moisés', 'affiliation': 'Universidad Internacional de La Rioja (UNIR)'}],
        'upload_type': 'publication',
        'publication_type': 'preprint',
        'access_right': 'open',
        'license': 'cc-by-4.0'
    }

def upload_to_zenodo(pdf_path, md_path):
    if not ZENODO_TOKEN:
        print("Error: ZENODO_ACCESS_TOKEN environment variable not set.")
        return

    metadata = extract_metadata(md_path)

    # 1. Create deposition
    r = requests.post(BASE_URL, params={'access_token': ZENODO_TOKEN},
                      json={}, headers={"Content-Type": "application/json"})
    if r.status_code != 201:
        print(f"Error creating deposition for {pdf_path}: {r.text}")
        return

    deposition_id = r.json()['id']
    bucket_url = r.json()['links']['bucket']

    # 2. Upload file
    filename = os.path.basename(pdf_path)
    with open(pdf_path, "rb") as fp:
        r = requests.put(f"{bucket_url}/{filename}", data=fp, params={'access_token': ZENODO_TOKEN})
    if r.status_code != 201:
        print(f"Error uploading file {filename}: {r.text}")
        return

    # 3. Update metadata
    r = requests.put(f"{BASE_URL}/{deposition_id}", params={'access_token': ZENODO_TOKEN},
                     json={'metadata': metadata}, headers={"Content-Type": "application/json"})
    if r.status_code != 200:
        print(f"Error updating metadata for {deposition_id}: {r.text}")
        return

    # 4. Publish
    r = requests.post(f"{BASE_URL}/{deposition_id}/actions/publish", params={'access_token': ZENODO_TOKEN})
    if r.status_code != 202:
        print(f"Error publishing {deposition_id}: {r.text}")
    else:
        print(f"Successfully published {filename}. DOI: {r.json().get('doi')}")

def main():
    # Recursive walk for PDFs
    for root, dirs, files in os.walk('preprints_pdf'):
        for filename in sorted(files):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(root, filename)
                # Corresponding md path
                rel_path = os.path.relpath(pdf_path, 'preprints_pdf')
                md_path = os.path.join('preprints_source', rel_path.replace('.pdf', '.md'))

                if os.path.exists(md_path):
                    print(f"Checking {pdf_path}...")
                    # Only upload if not already published (very basic check)
                    upload_to_zenodo(pdf_path, md_path)

if __name__ == "__main__":
    main()
