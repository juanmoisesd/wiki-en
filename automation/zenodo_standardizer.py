import requests
import json
import time
import os

# Configuration from researcher_profile.json
AUTHOR = {
    "name": "De la Serna, Juan Moisés",
    "given_names": "Juan Moisés",
    "family_names": "De la Serna",
    "affiliation": "Universidad Internacional de La Rioja (UNIR)",
    "orcid": "0000-0002-8401-8018"
}

def update_zenodo_metadata(token, deposition_id, current_metadata):
    """Updates Zenodo record creators to match standardized author format."""
    base_url = "https://zenodo.org/api/deposit/depositions"

    new_creators = [{
        "name": AUTHOR["name"],
        "affiliation": AUTHOR["affiliation"],
        "orcid": AUTHOR["orcid"]
    }]

    # We prune sensitive metadata that shouldn't be re-sent in a PUT update
    metadata = current_metadata.copy()
    metadata['creators'] = new_creators
    for field in ['doi', 'conceptdoi', 'prereserve_doi', 'recid']:
        metadata.pop(field, None)

    try:
        r = requests.put(f"{base_url}/{deposition_id}",
                         params={'access_token': token},
                         data=json.dumps({'metadata': metadata}),
                         headers={"Content-Type": "application/json"},
                         timeout=15)
        return r.status_code == 200, r.text
    except Exception as e:
        return False, str(e)

def process_all_records(token, records_json_path, limit=1000):
    """Processes Zenodo records from a local JSON cache and updates them via API."""
    with open(records_json_path, 'r') as f:
        records = json.load(f)

    count = 0
    errors = 0
    for r in records:
        creators = r.get('metadata', {}).get('creators', [])
        is_correct = any(AUTHOR["orcid"] in str(c.get('orcid', '')) for c in creators)

        if not is_correct:
            success, msg = update_zenodo_metadata(token, r['id'], r['metadata'])
            if success:
                count += 1
                if count % 20 == 0: print(f"Successfully updated {count} records...")
            else:
                errors += 1
                print(f"Error updating {r['id']}: {msg}")

            if count >= limit: break
            time.sleep(0.2) # Rate limit awareness

    return count, errors

if __name__ == "__main__":
    # Example usage:
    # python3 zenodo_standardizer.py <token> <records_cache.json>
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 zenodo_standardizer.py <TOKEN> <RECORDS_JSON>")
    else:
        c, e = process_all_records(sys.argv[1], sys.argv[2])
        print(f"Update finished. {c} updated, {e} errors.")
