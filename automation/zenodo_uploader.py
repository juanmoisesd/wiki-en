import requests
import json
import os
import re
import sys
import time

# Zenodo API configuration
ACCESS_TOKEN = os.environ.get('ZENODO_ACCESS_TOKEN')
BASE_URL = 'https://zenodo.org/api'

def upload_preprint(pdf_path, md_path):
    if not ACCESS_TOKEN:
        print("Error: ZENODO_ACCESS_TOKEN environment variable not set.")
        sys.exit(1)

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    title_match = re.search(r'Title: (.*)', content)
    title = title_match.group(1) if title_match else "Untitled"

    abstract_match = re.search(r'\*\*Abstract\*\*\n(.*?)\n\n', content, re.DOTALL)
    abstract = abstract_match.group(1).strip() if abstract_match else "Academic preprint by Juan Moisés de la Serna."

    keywords_match = re.search(r'\*\*Keywords\*\*: (.*)', content)
    keywords = keywords_match.group(1).split(', ') if keywords_match else ["education"]

    headers = {"Content-Type": "application/json"}
    params = {'access_token': ACCESS_TOKEN}

    r = requests.post(f"{BASE_URL}/deposit/depositions",
                      params=params,
                      json={},
                      headers=headers)

    if r.status_code != 201:
        print(f"Error creating deposition: {r.json()}")
        return None

    deposition_id = r.json()['id']
    bucket_url = r.json()['links']['bucket']

    filename = os.path.basename(pdf_path)
    with open(pdf_path, "rb") as fp:
        r = requests.put(
            f"{bucket_url}/{filename}",
            data=fp,
            params=params,
        )

    if r.status_code not in [200, 201]:
        print(f"Error uploading file: {r.json()}")
        return None

    data = {
        'metadata': {
            'title': title,
            'upload_type': 'publication',
            'publication_type': 'preprint',
            'description': abstract,
            'access_right': 'open',
            'license': 'cc-by-4.0',
            'creators': [{'name': 'De la Serna, Juan Moisés',
                          'affiliation': 'University International of La Rioja (UNIR)',
                          'orcid': '0000-0002-8401-8018'}],
            'keywords': keywords,
            'communities': [{'identifier': 'education'},
                            {'identifier': 'educational-research'},
                            {'identifier': 'pedagogy'}]
        }
    }

    r = requests.put(f"{BASE_URL}/deposit/depositions/{deposition_id}",
                     params=params,
                     json=data,
                     headers=headers)

    if r.status_code != 200:
        print(f"Error setting metadata: {r.json()}")
        return None

    r = requests.post(f"{BASE_URL}/deposit/depositions/{deposition_id}/actions/publish",
                      params=params)

    if r.status_code != 202:
        print(f"Error publishing: {r.json()}")
        return None

    result = r.json()
    return {
        'title': title,
        'doi': result['doi'],
        'url': result['links']['latest_html']
    }

if __name__ == "__main__":
    pdf_dir = "preprints_pdf"
    src_dir = "preprints_source"
    results_file = "zenodo_results_v2.json"

    results = []
    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            try:
                results = json.load(f)
            except:
                results = []

    uploaded_titles = [r['title'] for r in results]

    files = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf') and 'ExtV2_' in f])
    for filename in files:
        pdf_path = os.path.join(pdf_dir, filename)
        md_path = os.path.join(src_dir, filename.replace('.pdf', '.md'))

        with open(md_path, 'r', encoding='utf-8') as f:
            title_match = re.search(r'Title: (.*)', f.read())
            title = title_match.group(1) if title_match else "Untitled"

        if title in uploaded_titles:
            continue

        print(f"Uploading {filename}...")
        res = upload_preprint(pdf_path, md_path)
        if res:
            print(f"Success! DOI: {res['doi']}")
            results.append(res)
            with open(results_file, "w") as f:
                json.dump(results, f, indent=4)
            time.sleep(1)
        else:
            print(f"Failed to upload {filename}")
