import requests
import json
import os
import sys

def upload_to_zenodo(filepath, metadata_dict, access_token):
    ACCESS_TOKEN = access_token
    BASE_URL = 'https://zenodo.org/api/deposit/depositions'

    # 1. Create a new deposition
    headers = {"Content-Type": "application/json"}
    params = {'access_token': ACCESS_TOKEN}
    r = requests.post(BASE_URL, params=params, json={}, headers=headers)
    if r.status_code != 201:
        print(f"Error creating deposition: {r.text}")
        return None

    deposition_id = r.json()['id']
    bucket_url = r.json()['links']['bucket']

    # 2. Upload file
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as fp:
        r = requests.put(
            f"{bucket_url}/{filename}",
            data=fp,
            params=params,
        )
    if r.status_code not in [200, 201]:
        print(f"Error uploading file (Status {r.status_code}): {r.text}")
        return None

    # 3. Add metadata
    # Using 'report' as publication_type since 'policybrief' might not be a valid slug in Zenodo API
    data = {
        'metadata': {
            'title': metadata_dict['title'],
            'upload_type': 'publication',
            'publication_type': 'report',
            'description': metadata_dict['description'],
            'creators': [{'name': 'de la Serna, Juan Moisés', 'affiliation': 'Universidad Internacional de La Rioja (UNIR)', 'orcid': '0000-0002-8401-8018'}],
            'access_right': 'open',
            'license': 'cc-by-4.0',
            'keywords': metadata_dict.get('keywords', ['neuroscience', 'policy brief', 'intelligence'])
        }
    }
    r = requests.put(f"{BASE_URL}/{deposition_id}", params=params, data=json.dumps(data), headers=headers)
    if r.status_code != 200:
        print(f"Error adding metadata (Status {r.status_code}): {r.text}")
        return None

    # 4. Publish
    r = requests.post(f"{BASE_URL}/{deposition_id}/actions/publish", params=params)
    if r.status_code != 202:
        print(f"Error publishing (Status {r.status_code}): {r.text}")
        return None

    print(f"Successfully uploaded and published {filename} to Zenodo. Deposition ID: {deposition_id}")
    return deposition_id

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python zenodo_publisher.py <pdf_path> <title> <description> <token>")
    else:
        pdf_path = sys.argv[1]
        title = sys.argv[2]
        description = sys.argv[3]
        token = sys.argv[4]
        upload_to_zenodo(pdf_path, {'title': title, 'description': description}, token)
