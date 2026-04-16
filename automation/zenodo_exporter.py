import requests
import json
import time
import os
import sys

# Configuration from researcher_profile.json
with open('automation/researcher_profile.json', 'r') as f:
    profile = json.load(f)

API_TOKEN = os.environ.get("ZENODO_ACCESS_TOKEN")
ORCID = profile.get("orcid", "0000-0002-8401-8018")
BASE_URL = "https://zenodo.org/api/records"

def fetch_all_records():
    records = []
    # Search for creator's ORCID and include all versions
    params = {
        'q': f'creators.orcid:{ORCID}',
        'all_versions': 'true',
        'size': 100,
        'page': 1
    }

    headers = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"

    print(f"Fetching records for ORCID: {ORCID}...")

    while True:
        try:
            response = requests.get(BASE_URL, params=params, headers=headers)
            if response.status_code == 429:
                print("Rate limited. Waiting 60 seconds...")
                time.sleep(60)
                continue

            if response.status_code != 200:
                print(f"Error fetching page {params['page']}: {response.status_code}")
                print(response.text)
                break

            data = response.json()
            hits = data.get('hits', {}).get('hits', [])
            if not hits:
                break

            records.extend(hits)
            total = data['hits']['total']
            print(f"Fetched {len(records)} / {total} records...")

            if len(records) >= total:
                break

            # Zenodo API deep paging limit
            if params['page'] * params['size'] >= 10000:
                print("Reached Zenodo deep paging limit (10,000).")
                break

            params['page'] += 1
            time.sleep(0.5) # More conservative delay
        except Exception as e:
            print(f"Request failed: {e}")
            break

    return records

def generate_bib(records):
    bib_entries = []
    for rec in records:
        meta = rec.get('metadata', {})
        rec_id = rec.get('id')
        title = meta.get('title', 'Untitled').replace('{', '\\{').replace('}', '\\}')
        creators = meta.get('creators', [])
        authors = " and ".join([a.get('name', '') for a in creators])
        year = meta.get('publication_date', 'n.d.')[:4]
        doi = meta.get('doi', '')

        entry = f"""@misc{{zenodo_{rec_id},
  title = {{{title}}},
  author = {{{authors}}},
  year = {{{year}}},
  doi = {{{doi}}},
  url = {{https://doi.org/{doi}}}
}}"""
        bib_entries.append(entry)

    with open('master_citations.bib', 'w', encoding='utf-8') as f:
        f.write("\n\n".join(bib_entries))

def generate_jsonld(records):
    schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": profile.get("name"),
        "givenName": "Juan Moisés",
        "familyName": "de la Serna Tuya",
        "identifier": f"https://orcid.org/{ORCID}",
        "url": "https://juanmoisesd.github.io",
        "sameAs": [
            f"https://www.linkedin.com/in/{profile.get('linkedin')}",
            "https://scholar.google.com/citations?user=YOUR_GOOGLE_SCHOLAR_ID" # Placeholder for user to fill
        ],
        "affiliation": {
            "@type": "Organization",
            "name": profile.get("institution"),
            "url": profile.get("institution_url")
        },
        "mainEntityOfPage": "https://zenodo.org/communities/juanmoisesd-open-data",
        "hasPart": []
    }

    for rec in records:
        meta = rec.get('metadata', {})
        res_type = meta.get('resource_type', {}).get('type')
        item = {
            "@type": "Dataset" if res_type == 'dataset' else "ScholarlyArticle",
            "name": meta.get('title'),
            "description": meta.get('description'),
            "url": f"https://doi.org/{meta.get('doi')}",
            "identifier": meta.get('doi'),
            "datePublished": meta.get('publication_date'),
            "license": meta.get('license', {}).get('id')
        }
        schema["hasPart"].append(item)

    with open('schema.jsonld', 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

def generate_jsonl(records):
    with open('metadata.jsonl', 'w', encoding='utf-8') as f:
        for rec in records:
            meta = rec.get('metadata', {})
            line = {
                "id": rec.get('id'),
                "doi": meta.get('doi'),
                "title": meta.get('title'),
                "description": meta.get('description'),
                "authors": [a.get('name') for a in meta.get('creators', [])],
                "date": meta.get('publication_date'),
                "resource_type": meta.get('resource_type', {}).get('type'),
                "keywords": meta.get('keywords', [])
            }
            f.write(json.dumps(line, ensure_ascii=False) + "\n")

def generate_datapackage(records):
    package = {
        "name": "juan-moises-zenodo-collection",
        "title": "Juan Moisés de la Serna Zenodo Collection",
        "publisher": {
            "name": profile.get("name"),
            "path": "https://juanmoisesd.github.io"
        },
        "resources": [
            {
                "name": "zenodo-metadata",
                "path": "metadata.jsonl",
                "format": "jsonl",
                "profile": "data-resource"
            }
        ]
    }

    with open('datapackage.json', 'w', encoding='utf-8') as f:
        json.dump(package, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if not API_TOKEN:
        print("Warning: ZENODO_ACCESS_TOKEN environment variable not set. Running in limited public mode.")

    records = fetch_all_records()
    if records:
        print(f"Generating files for {len(records)} records...")
        generate_bib(records)
        generate_jsonld(records)
        generate_jsonl(records)
        generate_datapackage(records)
        print("Done!")
    else:
        print("No records found.")
