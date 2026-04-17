import requests
import json
import time
import os
import sys

# Configuration from researcher_profile.json
AUTHOR = {
    "name": "De la Serna, Juan Moisés",
    "given_names": "Juan Moisés",
    "family_names": "De la Serna",
    "affiliation": "Universidad Internacional de La Rioja (UNIR)",
    "orcid": "0000-0002-8401-8018"
}

def update_zenodo_metadata(token, deposition_id, current_metadata):
    """Updates Zenodo record creators to match standardized author format.
    Handles both drafts and published records by triggering 'edit' action if needed.
    """
    base_url = "https://zenodo.org/api/deposit/depositions"

    new_creators = [{
        "name": AUTHOR["name"],
        "affiliation": AUTHOR["affiliation"],
        "orcid": AUTHOR["orcid"]
    }]

    # We prune sensitive metadata that shouldn't be re-sent in a PUT update
    metadata = current_metadata.copy()
    metadata['creators'] = new_creators
    # Standard Zenodo best practice: include family/given names if available
    for creator in metadata['creators']:
        creator['family_name'] = AUTHOR['family_names']
        creator['given_name'] = AUTHOR['given_names']

    for field in ['doi', 'conceptdoi', 'prereserve_doi', 'recid']:
        metadata.pop(field, None)

    try:
        # 1. Try to unlock for editing (works if already published, no-op if draft)
        requests.post(f"{base_url}/{deposition_id}/actions/edit", params={'access_token': token}, timeout=10)

        # 2. Perform the update
        r = requests.put(f"{base_url}/{deposition_id}",
                         params={'access_token': token},
                         data=json.dumps({'metadata': metadata}),
                         headers={"Content-Type": "application/json"},
                         timeout=15)

        if r.status_code == 200:
            # 3. Publish the changes if it was already published
            requests.post(f"{base_url}/{deposition_id}/actions/publish", params={'access_token': token}, timeout=10)
            return True, "Success"
        else:
            return False, f"Status {r.status_code}: {r.text}"

    except Exception as e:
        return False, str(e)

def process_all_records(token, records_json_path, start_index=0, limit=1000):
    """Processes Zenodo records from a local JSON cache and updates them via API."""
    with open(records_json_path, 'r') as f:
        records = json.load(f)

    count = 0
    errors = 0
    total_records = len(records)

    print(f"Starting standardization from index {start_index} for {limit} records (Total: {total_records})")

    for i in range(start_index, min(start_index + limit, total_records)):
        r = records[i]
        creators = r.get('metadata', {}).get('creators', [])
        # Check if already standardized
        is_correct = any(AUTHOR["orcid"] == c.get('orcid', '') for c in creators)

        if not is_correct:
            success, msg = update_zenodo_metadata(token, r['id'], r['metadata'])
            if success:
                count += 1
                if count % 10 == 0: print(f"Successfully updated {count} records (Latest ID: {r['id']})...")
            else:
                errors += 1
                print(f"Error updating {r['id']}: {msg}")

            time.sleep(0.3) # Respect rate limits (Zenodo is 5000 req/hour, but let's be safe)
        else:
            # Already correct, skip
            pass

    return count, errors

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 zenodo_standardizer.py <TOKEN> <RECORDS_JSON> [START_INDEX] [LIMIT]")
    else:
        token = sys.argv[1]
        json_path = sys.argv[2]
        start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 1000

        c, e = process_all_records(token, json_path, start, limit)
        print(f"Batch finished. {c} updated, {e} errors.")
