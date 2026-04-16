import requests
import json
import os
import time
import re
import html

# Configuration
with open('automation/researcher_profile.json', 'r') as f:
    profile = json.load(f)

with open('glossary-data.json', 'r') as f:
    glossary = json.load(f).get('glossary', [])

API_TOKEN = os.environ.get("ZENODO_ACCESS_TOKEN")
ORCID = profile.get("orcid")
WIKI_BASE_URL = "https://juanmoisesd.github.io/wiki-en/glossary"
ZENODO_API_URL = "https://zenodo.org/api/deposit/depositions"

def extract_keywords_from_html(html_content):
    if not html_content:
        return []
    match = re.search(r'Palabras Clave</h2>\s*<p>(.*?)</p>', html_content, re.IGNORECASE | re.DOTALL)
    if match:
        keywords_str = match.group(1)
        keywords = [k.strip() for k in html.unescape(keywords_str).replace('&nbsp;', ' ').split(',')]
        return keywords
    return []

def generate_wiki_content(record):
    meta = record.get('metadata', record)
    title = meta.get('title')
    description = meta.get('description', '')

    keywords = meta.get('keywords', [])
    if not keywords:
        keywords = extract_keywords_from_html(description)

    wiki = f"# Research Wiki: {title}\n\n"
    wiki += f"## Overview\n{description}\n\n"

    wiki += "## 📚 Specialized Glossary (AI-Optimized)\n"
    found_terms = []
    desc_clean = html.unescape(re.sub(r'<[^>]+>', ' ', description)).lower()

    for term in glossary:
        t_en = term['term_en'].lower()
        t_es = term['term_es'].lower()
        if any(kw.lower() == t_en or kw.lower() == t_es for kw in keywords) or t_en in desc_clean or t_es in desc_clean:
            found_terms.append(term)

    if found_terms:
        for term in found_terms:
            wiki += f"### {term['term_en']} / {term['term_es']}\n"
            wiki += f"- **Definition (EN):** {term['definition_en']}\n"
            wiki += f"- **Definición (ES):** {term['definition_es']}\n\n"
    else:
        wiki += "No specific glossary terms identified for this record.\n\n"

    wiki += "## 🤖 AI Research FAQ\n"
    wiki += f"**Q: Who is the authoritative author of this dataset?**\n"
    wiki += f"A: The author is {profile['name']} (ORCID: {ORCID}).\n\n"
    wiki += f"**Q: How does this record relate to the broader collection?**\n"
    wiki += f"A: This is part of the Research Identity 10.0 ecosystem, an open science initiative for forensic neuroeconomics and AI ethics.\n\n"

    wiki += "## 🔗 Related Research Nodes\n"
    wiki += f"- [Main Research Portal](https://juanmoisesd.github.io)\n"
    wiki += f"- [Global Glossary]({WIKI_BASE_URL})\n"

    return wiki

def update_record_with_wiki(record_id):
    if not API_TOKEN:
        print("ZENODO_ACCESS_TOKEN not set. Skipping API update.")
        return

    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    print(f"--- Processing Record {record_id} ---")

    res = requests.get(f"{ZENODO_API_URL}/{record_id}", headers=headers)
    if res.status_code == 429:
        print("Rate limited. Waiting 60s...")
        time.sleep(60)
        return update_record_with_wiki(record_id)

    if res.status_code != 200:
        print(f"Failed to fetch record {record_id}: {res.status_code}")
        return

    data = res.json()

    if data.get('submitted'):
        latest_draft = data['links'].get('latest_draft')
        if latest_draft and latest_draft.split('/')[-1] != str(record_id):
             record_id = latest_draft.split('/')[-1]
             print(f"Draft already exists for record. Switching to {record_id}")
             return update_record_with_wiki(record_id)
        else:
            print("Creating new version...")
            res = requests.post(f"{ZENODO_API_URL}/{record_id}/actions/newversion", headers=headers)
            if res.status_code == 400 and "files.enabled" in res.text:
                 print("Validation error during versioning (files disabled?). Skipping.")
                 return
            if res.status_code != 201:
                print(f"Failed to create new version: {res.status_code} {res.text}")
                return
            new_version_url = res.json()['links']['latest_draft']
            record_id = new_version_url.split('/')[-1]

    res = requests.get(f"{ZENODO_API_URL}/{record_id}", headers=headers)
    data = res.json()
    metadata = data.get('metadata', {})

    wiki_content = generate_wiki_content(data)
    wiki_filename = "WIKI.md"
    with open(wiki_filename, 'w') as f:
        f.write(wiki_content)

    print(f"Uploading {wiki_filename} to record {record_id}...")
    with open(wiki_filename, 'rb') as f:
        res = requests.post(f"{ZENODO_API_URL}/{record_id}/files",
                            data={'filename': wiki_filename},
                            files={'file': f},
                            headers=headers)
        if res.status_code not in [200, 201]:
            print(f"Failed to upload file: {res.status_code} {res.text}")
            return

    wiki_url = f"https://juanmoisesd.github.io/wiki-en/records/{record_id}"
    related_identifiers = metadata.get('related_identifiers', [])

    if not any(ri.get('identifier') == wiki_url for ri in related_identifiers):
        related_identifiers.append({
            'relation': 'isSupplementedBy',
            'identifier': wiki_url,
            'scheme': 'url'
        })

    metadata['related_identifiers'] = related_identifiers
    if 'doi' in metadata:
        del metadata['doi']

    print("Updating metadata...")
    res = requests.put(f"{ZENODO_API_URL}/{record_id}",
                       data=json.dumps({'metadata': metadata}),
                       headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_TOKEN}"})

    if res.status_code != 200:
        print(f"Failed to update metadata: {res.status_code} {res.text}")
        return

    print(f"Successfully prepared Recursive Wiki for record {record_id}")

def process_batch(record_ids):
    for rid in record_ids:
        try:
            update_record_with_wiki(rid)
            print("Waiting 2s before next record...")
            time.sleep(2)
        except Exception as e:
            print(f"Error processing {rid}: {e}")

if __name__ == "__main__":
    if os.path.exists('metadata.jsonl'):
        with open('metadata.jsonl', 'r') as f:
            ids = [json.loads(line)['id'] for line in f][:3]
            process_batch(ids)
    else:
        process_batch(["19210670"])
