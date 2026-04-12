import os
import requests
import json
import re

ZENODO_TOKEN = os.getenv("ZENODO_ACCESS_TOKEN", "N7VErxvSFds8OrqDAy5zh4HyfDGDsDWe1OROHnmGivrStTOSHSTD54ZH1LFN")
BASE_URL = "https://zenodo.org/api/deposit/depositions"

def extract_metadata(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    title_match = re.search(r'^# (.*)', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(md_path)

    abstract_match = re.search(r'## Resumen \(Abstract\)\n(.*?)\n\n', content, re.DOTALL)
    abstract = abstract_match.group(1).strip() if abstract_match else "Estudio académico sobre " + title

    keywords_match = re.search(r'\*\*Palabras clave \(Keywords\):\*\* (.*)', content)
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
    pdf_dir = 'preprints_pdf'
    md_dir = 'preprints_source'

    if not os.path.exists(pdf_dir):
        print("PDF directory not found.")
        return

    for filename in sorted(os.listdir(pdf_dir)):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            md_path = os.path.join(md_dir, filename.replace('.pdf', '.md'))
            if os.path.exists(md_path):
                print(f"Uploading {pdf_path}...")
                upload_to_zenodo(pdf_path, md_path)

if __name__ == "__main__":
    main()
