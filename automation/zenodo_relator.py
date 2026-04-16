import urllib.request
import urllib.parse
import json
import re
import time
import os

# Configuration from environment variables
TOKEN = os.getenv("ZENODO_ACCESS_TOKEN")
ORCID = "0000-0002-8401-8018"
BASE_URL = "https://zenodo.org/api"

def api_request(url, method="GET", data=None):
    if not TOKEN:
        print("Error: ZENODO_ACCESS_TOKEN environment variable is not set.")
        return None

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req.data = json_data

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_all_records(limit_pages=None):
    records = []
    page = 1
    size = 100
    while True:
        print(f"Fetching page {page}...", flush=True)
        # Encode query parameters manually for urllib
        query = urllib.parse.quote(f'creators.orcid:"{ORCID}"')
        url = f"{BASE_URL}/records?q={query}&size={size}&page={page}"
        data = api_request(url)
        if not data or not data.get('hits', {}).get('hits'):
            break
        records.extend(data['hits']['hits'])
        if len(data['hits']['hits']) < size:
            break
        if limit_pages and page >= limit_pages:
            break
        page += 1
    return records

def normalize_title(title):
    # Remove known document type prefixes followed by optional language in parenthesis
    # e.g., "Press Release (English): " or "Policy Brief: "
    # We look for the last colon that follows a known type pattern to handle "Type: Subject: Subtitle"
    types = ["Press Release", "Policy Brief", "Research Brief", "Executive Summary",
             "Visual Summary", "Infographic", "Methodology Sheet", "Data Note", "Teaching Guide"]

    pattern = r'^(' + '|'.join(types) + r')\s*(\([^)]*\))?:\s*(.*)$'
    match = re.search(pattern, title, re.IGNORECASE)
    if match:
        return match.group(3).strip()
    return title.strip()

def group_records(records):
    groups = {}
    for rec in records:
        base_title = normalize_title(rec['metadata']['title'])
        if base_title not in groups:
            groups[base_title] = []
        groups[base_title].append(rec)
    return groups

def update_record_relations(record, related_dois, dry_run=True):
    current_related = record['metadata'].get('related_identifiers', [])
    existing_ids = {item['identifier'] for item in current_related}

    new_related = list(current_related)
    added = False

    for doi in related_dois:
        if doi != record['doi'] and doi not in existing_ids:
            # Determine relation type
            # Default to isVariantFormOf if it's likely a translation
            # Use isSupplementTo if it's a brief/press release
            relation = "isVariantFormOf"
            title = record['metadata']['title'].lower()
            if any(x in title for x in ["press release", "policy brief", "research brief", "executive summary", "visual summary", "infographic"]):
                 relation = "isSupplementTo"

            new_related.append({
                "identifier": doi,
                "relation": relation,
                "resource_type": "publication",
                "scheme": "doi"
            })
            added = True

    if not added:
        return False

    if dry_run:
        print(f"[DRY-RUN] Would update {record['id']} ({record['metadata']['title']}) with {len(new_related) - len(current_related)} new relations.", flush=True)
        return True

    # Real update flow via Deposition API
    print(f"Updating {record['id']}...", flush=True)
    # 1. Edit (creates a draft for the published record)
    edit_url = f"{BASE_URL}/deposit/depositions/{record['id']}/actions/edit"
    resp = api_request(edit_url, method="POST")
    if not resp:
        return False

    # 2. Update metadata
    update_url = f"{BASE_URL}/deposit/depositions/{record['id']}"
    metadata = resp.get('metadata', record['metadata'])
    metadata['related_identifiers'] = new_related

    # Remove problematic fields for update
    for field in ['doi', 'conceptdoi', 'publication_date', 'prereserve_doi']:
        metadata.pop(field, None)

    resp = api_request(update_url, method="PUT", data={"metadata": metadata})
    if not resp:
        return False

    # 3. Publish
    publish_url = f"{BASE_URL}/deposit/depositions/{record['id']}/actions/publish"
    resp = api_request(publish_url, method="POST")
    return resp is not None

def main(dry_run=True, limit_pages=None):
    if not TOKEN:
        print("Error: ZENODO_ACCESS_TOKEN environment variable not found. Please set it before running.")
        return

    records = get_all_records(limit_pages=limit_pages)
    print(f"Found {len(records)} records.", flush=True)
    groups = group_records(records)
    print(f"Grouped into {len(groups)} thematic topics.", flush=True)

    updated_count = 0
    for base_title, group in groups.items():
        if len(group) < 2:
            continue

        print(f"Processing group: {base_title} ({len(group)} records)", flush=True)
        all_dois = [rec['doi'] for rec in group]

        for rec in group:
            if update_record_relations(rec, all_dois, dry_run=dry_run):
                updated_count += 1
                if not dry_run:
                    time.sleep(1) # Rate limiting

    print(f"Finished. Total records {'to be updated' if dry_run else 'updated'}: {updated_count}", flush=True)

if __name__ == "__main__":
    import sys
    dry_run = "--run" not in sys.argv
    # In dry run mode, limit to 2 pages for performance. In run mode, process everything.
    limit_pages = 2 if dry_run else None
    main(dry_run=dry_run, limit_pages=limit_pages)
