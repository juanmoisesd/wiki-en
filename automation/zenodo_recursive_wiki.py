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

    # Glossary Section
    wiki += "## 📚 Specialized Glossary (AI-Optimized)\n"
    found_terms = []

    desc_clean = html.unescape(re.sub(r'<[^>]+>', ' ', description)).lower()

    for term in glossary:
        t_en = term['term_en'].lower()
        t_es = term['term_es'].lower()

        in_keywords = any(kw.lower() == t_en or kw.lower() == t_es for kw in keywords)
        in_desc = t_en in desc_clean or t_es in desc_clean

        if in_keywords or in_desc:
            found_terms.append(term)

    if found_terms:
        for term in found_terms:
            wiki += f"### {term['term_en']} / {term['term_es']}\n"
            wiki += f"- **Definition (EN):** {term['definition_en']}\n"
            wiki += f"- **Definición (ES):** {term['definition_es']}\n\n"
    else:
        wiki += "No specific glossary terms identified for this record.\n\n"

    # AI FAQ Section
    wiki += "## 🤖 AI Research FAQ\n"
    wiki += f"**Q: Who is the authoritative author of this dataset?**\n"
    wiki += f"A: The author is {profile['name']} (ORCID: {ORCID}).\n\n"
    wiki += f"**Q: How does this record relate to the broader collection?**\n"
    wiki += f"A: This is part of the Research Identity 10.0 ecosystem, an open science initiative for forensic neuroeconomics and AI ethics.\n\n"

    # Internal Links
    wiki += "## 🔗 Related Research Nodes\n"
    wiki += f"- [Main Research Portal](https://juanmoisesd.github.io)\n"
    wiki += f"- [Global Glossary]({WIKI_BASE_URL})\n"

    return wiki

def generate_expanded_schema(records):
    schema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": profile.get("name"),
        "identifier": f"https://orcid.org/{ORCID}",
        "hasPart": []
    }

    for rec in records:
        meta = rec.get('metadata', rec)
        description = meta.get('description', '')
        desc_clean = html.unescape(re.sub(r'<[^>]+>', ' ', description)).lower()

        keywords = meta.get('keywords', [])
        if not keywords:
            keywords = extract_keywords_from_html(description)

        item = {
            "@type": "ScholarlyArticle",
            "name": meta.get('title'),
            "url": f"https://doi.org/{meta.get('doi')}",
            "keywords": keywords,
            "definedTerm": []
        }

        # LINKING LOGIC
        for term in glossary:
            t_en = term['term_en'].lower()
            t_es = term['term_es'].lower()

            # More inclusive substring match for common research terms
            if any(kw.lower() in t_en or kw.lower() in t_es for kw in keywords) or t_en in desc_clean or t_es in desc_clean:
                item["definedTerm"].append({
                    "@type": "DefinedTerm",
                    "name": term['term_en'],
                    "description": term['definition_en'],
                    "url": f"{WIKI_BASE_URL}#{term['id']}"
                })

        schema["hasPart"].append(item)

    with open('schema.jsonld', 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if os.path.exists('metadata.jsonl'):
        with open('metadata.jsonl', 'r') as f:
            records = [json.loads(line) for line in f]

        if records:
            print(f"Generating Wiki for: {records[0]['title']}")
            wiki_md = generate_wiki_content(records[0])
            with open('SAMPLE_WIKI.md', 'w') as w:
                w.write(wiki_md)
            print("Sample Wiki generated in SAMPLE_WIKI.md")

            print("Expanding schema with Recursive Knowledge Structure...")
            generate_expanded_schema(records[:1000])
            print("Expanded schema.jsonld generated.")
    else:
        print("metadata.jsonl not found.")
