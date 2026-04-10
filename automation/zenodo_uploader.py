import os
import json
import requests
import time

def upload_to_zenodo(token, item):
    headers = {"Content-Type": "application/json"}
    params = {'access_token': token}

    # 1. Create Deposition
    r = requests.post('https://zenodo.org/api/deposit/depositions',
                      params=params,
                      json={"metadata": item['metadata']},
                      headers=headers)

    if r.status_code != 201:
        print(f"Error creating deposition for {item['metadata']['title']}: {r.json()}")
        return None

    deposition_id = r.json()['id']
    bucket_url = r.json()['links']['bucket']

    # 2. Upload File
    filename = os.path.basename(item['file_path'])
    with open(item['file_path'], 'rb') as fp:
        r = requests.put(f"{bucket_url}/{filename}",
                         data=fp,
                         params=params)

    if r.status_code != 201:
        print(f"Error uploading file for {deposition_id}: {r.json()}")
        return None

    # 3. Publish (Optional, but usually required for DOI)
    # Note: Using Zenodo sandbox might be better for testing, but token was provided.
    # We will just return the deposition ID and link if publishing is restricted.
    publish_url = r.json()['links'].get('publish')
    # r = requests.post(f"https://zenodo.org/api/deposit/depositions/{deposition_id}/actions/publish", params=params)

    return {
        "title": item['metadata']['title'],
        "id": deposition_id,
        "link": f"https://zenodo.org/record/{deposition_id}"
    }

def main():
    token = "HyK2hi1jydLccpkX1fq72z0huFys9AxRKkfffUxaKCPSODQC4YTjnq9GXtsu"
    manifest_path = 'automation/zenodo_manifest.json'

    if not os.path.exists(manifest_path):
        print("Manifest not found.")
        return

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    results = []
    for item in manifest:
        print(f"Processing {item['metadata']['title']}...")
        res = upload_to_zenodo(token, item)
        if res:
            results.append(res)
            print(f"Successfully prepared deposition: {res['link']}")
        time.sleep(1) # Rate limiting

    with open('automation/zenodo_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Upload results saved to automation/zenodo_results.json")

if __name__ == "__main__":
    main()
