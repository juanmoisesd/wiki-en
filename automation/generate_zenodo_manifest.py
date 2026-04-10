import os
import json
import requests
import re

def get_metadata(markdown_path, pdf_path):
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    title_match = re.search(r'^# (.*)', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Untitled"

    abstract_match = re.search(r'## (?:Abstract|Resumen \(Abstract\))\n(.*?)\n\n', content, re.DOTALL)
    abstract = abstract_match.group(1) if abstract_match else ""

    keywords_match = re.search(r'\*\*Keywords:\*\* (.*)', content) or re.search(r'\*\*Palabras clave:\*\* (.*)', content)
    keywords = keywords_match.group(1).split(', ') if keywords_match else []

    return {
        "metadata": {
            "title": title,
            "upload_type": "publication",
            "publication_type": "preprint",
            "description": abstract,
            "creators": [{"name": "De la Serna, Juan Moisés", "affiliation": "UNIR", "orcid": "0000-0002-8401-8018"}],
            "keywords": keywords,
            "license": "CC-BY-4.0",
            "communities": [{"identifier": "neuropsychology"}, {"identifier": "clinical-neuroscience"}]
        },
        "file_path": pdf_path
    }

def main():
    draft_dir = 'editorial_neurociencia/preprints_drafts'
    pdf_dir = 'editorial_neurociencia/preprints_pdf'

    manifest = []

    for filename in os.listdir(draft_dir):
        if filename.endswith('.md'):
            # Find corresponding PDF
            match = re.search(r'Preprint_Neuropsicologia_(\d+)_(\w+).md', filename)
            if match:
                tid = match.group(1)
                lang = match.group(2)

                # Logic to find the PDF name
                with open('automation/research_data.json', 'r') as f:
                    data = json.load(f)
                topic = next(t for t in data['topics'] if str(t['id']) == tid)
                title_slug = topic['title'].replace(' ', '_').replace(':', '').replace('.', '')
                pdf_filename = f"Preprint_Neuropsicologia_{title_slug}_{lang}_JuanMoisésdelaSerna.pdf"
                pdf_path = os.path.join(pdf_dir, pdf_filename)

                metadata = get_metadata(os.path.join(draft_dir, filename), pdf_path)
                manifest.append(metadata)

    with open('automation/zenodo_manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print("Generated automation/zenodo_manifest.json")

if __name__ == "__main__":
    main()
