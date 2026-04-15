import os
import json
import requests
from fpdf import FPDF
import re

class AcademicPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Search for available Unicode fonts in common locations
        self.main_font = "Helvetica"
        font_locations = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf"
        ]
        bold_font_locations = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"
        ]

        for loc, bloc in zip(font_locations, bold_font_locations):
            if os.path.exists(loc) and os.path.exists(bloc):
                self.add_font("DejaVu", "", loc)
                self.add_font("DejaVu", "B", bloc)
                self.main_font = "DejaVu"
                break

    def header(self):
        self.set_font(self.main_font, 'I' if self.main_font == "Helvetica" else "", 8)
        self.cell(0, 10, 'Research Identity 10.0 - Academic Preprint', align='R', new_x='RIGHT', new_y='TOP')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.main_font, 'I' if self.main_font == "Helvetica" else "", 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def clean_markdown(text):
    # Remove bold markdown
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # Remove italic markdown
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove links
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    return text

def generate_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pdf = AcademicPDF()
    pdf.add_page()

    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(4)
            continue

        if line.startswith('###'):
            pdf.set_font(pdf.main_font, 'B', 14)
            text = clean_markdown(line.replace('###', '').strip())
            pdf.multi_cell(0, 10, text)
        elif line.startswith('**') or re.match(r'^\d+\.', line):
            pdf.set_font(pdf.main_font, 'B', 11)
            pdf.multi_cell(0, 8, clean_markdown(line))
        else:
            pdf.set_font(pdf.main_font, '', 10)
            pdf.multi_cell(0, 6, clean_markdown(line))
        pdf.ln(1)

    pdf.output(pdf_path)
    return pdf_path

def upload_to_zenodo(pdf_path, title, token):
    url = "https://zenodo.org/api/deposit/depositions"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": token}

    data = {
        'metadata': {
            'title': title,
            'upload_type': 'publication',
            'publication_type': 'preprint',
            'description': f'Academic preprint for topic: {title}',
            'creators': [{'name': 'de la Serna, Juan Moisés', 'affiliation': 'UNIR', 'orcid': '0000-0002-8401-8018'}],
            'access_right': 'open',
            'license': 'cc-by'
        }
    }

    # 1. Create deposition
    r = requests.post(url, params=params, json=data, headers=headers)
    if r.status_code != 201:
        print(f"Error creating deposition for {title}: {r.status_code} - {r.text}")
        return None

    dep_data = r.json()
    deposition_id = dep_data['id']
    bucket_url = dep_data['links']['bucket']

    # 2. Upload file
    filename = os.path.basename(pdf_path)
    with open(pdf_path, "rb") as fp:
        r = requests.put(f"{bucket_url}/{filename}", data=fp, params=params)

    if r.status_code not in [200, 201]:
        print(f"Error uploading file {filename}: {r.status_code} - {r.text}")
        return None

    # 3. Publish deposition
    r = requests.post(f"{url}/{deposition_id}/actions/publish", params=params)
    if r.status_code != 202:
        print(f"Error publishing deposition {deposition_id}: {r.status_code} - {r.text}")
        return deposition_id

    print(f"Successfully uploaded and published {filename} to Zenodo. Deposition ID: {deposition_id}")
    return deposition_id

import argparse

def main():
    parser = argparse.ArgumentParser(description='Generate PDFs and upload to Zenodo.')
    parser.add_argument('--source', default='preprints_source', help='Source directory for Markdown files')
    parser.add_argument('--output', default='preprints_pdf', help='Output directory for PDF files')
    args = parser.parse_args()

    source_dir = args.source
    output_dir = args.output
    # Use environment variable for token
    token = os.getenv("ZENODO_ACCESS_TOKEN")

    if not token:
        print("Error: ZENODO_ACCESS_TOKEN environment variable not set.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    results = {}

    files = [f for f in os.listdir(source_dir) if f.endswith('.md')]
    for filename in sorted(files):
        md_path = os.path.join(source_dir, filename)
        pdf_filename = filename.replace('.md', '.pdf')
        pdf_path = os.path.join(output_dir, pdf_filename)

        print(f"Generating PDF for {filename}...")
        try:
            generate_pdf(md_path, pdf_path)
        except Exception as e:
            print(f"Failed to generate PDF for {filename}: {e}")
            continue

        with open(md_path, 'r', encoding='utf-8') as f:
            first_lines = f.read(1000)
            title_match = re.search(r'### 1\. \*\*Título\*\*\n(.+)', first_lines)
            title = clean_markdown(title_match.group(1).strip()) if title_match else pdf_filename

        print(f"Uploading {pdf_filename} to Zenodo...")
        dep_id = upload_to_zenodo(pdf_path, title, token)
        results[filename] = dep_id

    # Save results to a file (optional, but useful for logs)
    with open('automation/last_upload_results.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
