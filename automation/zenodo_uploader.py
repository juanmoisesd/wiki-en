import requests
import json
import os
import re
import sys

# Zenodo API configuration
ACCESS_TOKEN = os.environ.get('ZENODO_ACCESS_TOKEN')
BASE_URL = 'https://zenodo.org/api'

def upload_preprint(pdf_path, md_path):
    if not ACCESS_TOKEN:
        print("Error: ZENODO_ACCESS_TOKEN environment variable not set.")
        sys.exit(1)

    # 1. Read metadata from Markdown source
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    title = re.search(r'Title: (.*)', content).group(1)
    # Be more flexible with abstract extraction
    abstract_match = re.search(r'\*\*Abstract\*\*\n(.*?)\n\n', content, re.DOTALL)
    if abstract_match:
        abstract = abstract_match.group(1).strip()
    else:
        # Fallback
        abstract = "Academic preprint by Juan Moisés de la Serna."

    keywords_match = re.search(r'\*\*Keywords\*\*: (.*)', content)
    keywords = keywords_match.group(1).split(', ') if keywords_match else ["education"]

    # 2. Create deposition
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

    # 3. Upload file
    filename = os.path.basename(pdf_path)
    with open(pdf_path, "rb") as fp:
        # Note: bucket_url already includes deposition id sometimes,
        # but let's follow the Quickstart exactly
        r = requests.put(
            f"{bucket_url}/{filename}",
            data=fp,
            params=params,
        )

    # Zenodo returns 201 for new file creation in bucket
    if r.status_code not in [200, 201]:
        print(f"Error uploading file (Status {r.status_code}): {r.json()}")
        return None

    # 4. Set metadata
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
            # Communities must exist, let's use common ones or omit if unsure
            # 'communities': [{'identifier': 'education'}]
        }
    }

    r = requests.put(f"{BASE_URL}/deposit/depositions/{deposition_id}",
                     params=params,
                     json=data,
                     headers=headers)

    if r.status_code != 200:
        print(f"Error setting metadata: {r.json()}")
        return None

    # 5. Publish
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

    results = []
    for filename in sorted(os.listdir(pdf_dir)):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            md_path = os.path.join(src_dir, filename.replace('.pdf', '.md'))
            print(f"Uploading {filename}...")
            res = upload_preprint(pdf_path, md_path)
            if res:
                print(f"Success! DOI: {res['doi']}")
                results.append(res)
            else:
                print(f"Failed to upload {filename}")

    with open("zenodo_results.json", "w") as f:
        json.dump(results, f, indent=4)
