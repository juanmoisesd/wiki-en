import requests
import json
import time
import sys
import os

# Securely get token from environment variable
TOKEN = os.environ.get("ZENODO_ACCESS_TOKEN")
BASE_URL = "https://zenodo.org/api/deposit/depositions"

AUTHOR_YAML = """authors:
  - family-names: De la Serna
    given-names: Juan Moisés
    orcid: https://orcid.org/0000-0002-8401-8018"""

ORCID = "0000-0002-8401-8018"

def generate_cff(title, doi, date_released, url=None):
    cff = [
        'cff-version: 1.2.0',
        'message: "If you use this software or dataset, please cite it as below."',
        'type: dataset',
        AUTHOR_YAML,
        f'title: "{title}"',
        f'date-released: "{date_released}"'
    ]
    if doi:
        cff.append(f'doi: "{doi}"')
    if url:
        cff.append(f'url: "{url}"')
    return "\n".join(cff)

def update_record(depo, cff_content):
    if not TOKEN:
        print("Error: ZENODO_ACCESS_TOKEN not set.")
        return False

    depo_id = depo['id']
    is_published = depo.get('submitted', False)
    metadata = depo['metadata']

    # Update creators in metadata to include ORCID
    updated_creators = []
    for creator in metadata.get('creators', []):
        if "De la Serna" in creator['name']:
            creator['orcid'] = ORCID
        updated_creators.append(creator)
    metadata['creators'] = updated_creators

    target_id = depo_id
    if is_published:
        print(f"Creating new version for {depo_id}...")
        res = requests.post(f"{BASE_URL}/{depo_id}/actions/newversion", params={'access_token': TOKEN})
        if res.status_code != 201:
            print(f"Failed to create new version for {depo_id}: {res.text}")
            return False
        new_version_data = res.json()
        target_id = new_version_data['links']['latest_draft'].split('/')[-1]
        print(f"New draft version created: {target_id}")

    # For new versions, Zenodo assigns a new DOI. We must NOT send the old DOI in metadata.
    metadata_to_send = metadata.copy()
    if 'doi' in metadata_to_send:
        del metadata_to_send['doi']

    # Update metadata
    print(f"Updating metadata for {target_id}...")
    res = requests.put(f"{BASE_URL}/{target_id}", params={'access_token': TOKEN},
                       data=json.dumps({'metadata': metadata_to_send}),
                       headers={"Content-Type": "application/json"})
    if res.status_code != 200:
         print(f"Warning: Failed to update metadata for {target_id}: {res.text}")

    # Upload CITATION.cff
    print(f"Uploading CITATION.cff to {target_id}...")
    files_url = f"{BASE_URL}/{target_id}/files"

    # Check for existing CITATION.cff in draft
    res = requests.get(files_url, params={'access_token': TOKEN})
    if res.status_code == 200:
        for f in res.json():
            if f['filename'] == 'CITATION.cff':
                requests.delete(f"{files_url}/{f['id']}", params={'access_token': TOKEN})
                break

    res = requests.post(files_url, params={'access_token': TOKEN},
                        data={'name': 'CITATION.cff'},
                        files={'file': ('CITATION.cff', cff_content)})
    if res.status_code != 201:
        print(f"Failed to upload file to {target_id}: {res.text}")
        return False

    print(f"Publishing {target_id}...")
    res = requests.post(f"{BASE_URL}/{target_id}/actions/publish", params={'access_token': TOKEN})
    if res.status_code != 202:
        print(f"Failed to publish {target_id}: {res.text}")
        return False

    print(f"Successfully updated {depo_id} -> {target_id}")
    return True

def process_depositions(limit=None):
    if not TOKEN:
        print("Error: ZENODO_ACCESS_TOKEN not set.")
        return

    params = {'access_token': TOKEN, 'size': 50, 'page': 1}
    processed = 0

    while True:
        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            print(f"Error fetching depositions: {response.status_code}")
            break
        depositions = response.json()
        if not depositions:
            break

        for depo in depositions:
            metadata = depo['metadata']
            creators = metadata.get('creators', [])
            has_orcid = any('orcid' in c for c in creators)
            has_cff = any(f['filename'] == 'CITATION.cff' for f in depo.get('files', []))

            if not has_orcid or not has_cff:
                print(f"Processing {depo['id']}: {metadata.get('title')}")
                title = metadata.get('title', 'Untitled')
                doi = depo.get('doi') or metadata.get('prereserve_doi', {}).get('doi')
                date = metadata.get('publication_date', time.strftime('%Y-%m-%d'))
                cff_content = generate_cff(title, doi, date)

                if update_record(depo, cff_content):
                    processed += 1
                    if limit and processed >= limit:
                        return

        params['page'] += 1
        time.sleep(1) # Rate limit

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    process_depositions(limit)
