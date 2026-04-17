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

def api_request(url, method="GET", data=None, max_retries=3):
    if not TOKEN:
        print("Error: ZENODO_ACCESS_TOKEN environment variable is not set.")
        return None

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    for attempt in range(max_retries):
        req = urllib.request.Request(url, method=method, headers=headers)
        if data:
            json_data = json.dumps(data).encode('utf-8')
            req.data = json_data

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code in [429, 500, 502, 503, 504]:
            wait_time = (attempt + 1) * 5
            print(f"HTTP Error {e.code} on {method} {url}. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
            time.sleep(wait_time)
            # return api_request(url, method, data, max_retries-1) # Simplified retry
        else:
            print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    return None

def get_all_records(start_page=1, end_page=None, custom_query=None):
    records = []
    page = start_page
    size = 100
    while True:
        print(f"Fetching page {page}...", flush=True)
        # Encode query parameters manually for urllib
        query_str = custom_query if custom_query else f'creators.orcid:"{ORCID}"'
        query = urllib.parse.quote(query_str)
        url = f"{BASE_URL}/records?q={query}&size={size}&page={page}"
        data = api_request(url)
        if not data or not data.get('hits', {}).get('hits'):
            break
        records.extend(data['hits']['hits'])
        if len(data['hits']['hits']) < size:
            break
        if end_page and page >= end_page:
            break
        page += 1
    return records

def normalize_title(title):
    # Remove known document type prefixes followed by optional language in parenthesis
    # e.g., "Press Release (English): " or "Policy Brief: "
    types = ["Press Release", "Policy Brief", "Research Brief", "Executive Summary",
             "Visual Summary", "Infographic", "Methodology Sheet", "Data Note", "Teaching Guide",
             "Registered Report", "Dataset", "Taxonomía Completa", "Academic Preprint"]

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
    existing_ids = {item['identifier'].lower() for item in current_related}

    new_related = list(current_related)
    added = False

    for doi in related_dois:
        if doi.lower() != record['doi'].lower() and doi.lower() not in existing_ids:
            # Determine relation type
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

def main(dry_run=True, start_page=1, end_page=None, custom_query=None):
    if not TOKEN:
        print("Error: ZENODO_ACCESS_TOKEN environment variable not found.")
        return

    records = get_all_records(start_page=start_page, end_page=end_page, custom_query=custom_query)
    print(f"Found {len(records)} records.", flush=True)
    groups = group_records(records)
    print(f"Grouped into {len(groups)} thematic topics.", flush=True)

    updated_count = 0
    for base_title, group in groups.items():
        if len(group) < 2:
            continue

        all_dois = [rec['doi'] for rec in group if 'doi' in rec]
        if not all_dois: continue

        for rec in group:
            if update_record_relations(rec, all_dois, dry_run=dry_run):
                updated_count += 1
                if not dry_run:
                    time.sleep(0.5) # Rate limiting

    print(f"Finished. Total records {'to be updated' if dry_run else 'updated'}: {updated_count}", flush=True)

if __name__ == "__main__":
    import sys
    dry_run = "--run" not in sys.argv

    # Parse arguments
    start_page = 1
    end_page = None
    custom_query = None

    if "--start" in sys.argv:
        start_page = int(sys.argv[sys.argv.index("--start") + 1])
    if "--end" in sys.argv:
        end_page = int(sys.argv[sys.argv.index("--end") + 1])
    if "--query" in sys.argv:
        custom_query = sys.argv[sys.argv.index("--query") + 1]

    main(dry_run=dry_run, start_page=start_page, end_page=end_page, custom_query=custom_query)
