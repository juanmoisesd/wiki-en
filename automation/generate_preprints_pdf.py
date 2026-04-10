import os
import json
from fpdf import FPDF
import re

class PreprintPDF(FPDF):
    def header(self):
        # Academic Header
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, 'Pre-print Publication - Juan Moisés de la Serna - Open Research Collection', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def create_pdf(markdown_path, output_path):
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pdf = PreprintPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title Page
    title_match = re.search(r'^# (.*)', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Untitled"

    pdf.set_font('helvetica', 'B', 20)
    pdf.multi_cell(190, 15, title, align='C')
    pdf.ln(10)

    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(190, 10, 'Author: Juan Moisés de la Serna', new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.set_font('helvetica', '', 12)
    pdf.cell(190, 7, 'ORCID: 0000-0002-8401-8018', new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.cell(190, 7, 'Affiliation: University International of La Rioja (UNIR)', new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.cell(190, 7, 'Email: juanmoises.delaserna@unir.net', new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.ln(20)

    # Process Content
    lines = content.split('\n')

    pdf.set_font('helvetica', '', 11)
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue

        if line.startswith('# ') or line.startswith('**Author:**') or line.startswith('**ORCID:**') or line.startswith('**Affiliation:**') or line.startswith('**Email:**'):
            continue

        if line.startswith('## '):
            pdf.ln(5)
            pdf.set_font('helvetica', 'B', 14)
            pdf.cell(190, 10, line[3:], new_x="LMARGIN", new_y="NEXT", align='L')
            pdf.set_font('helvetica', '', 11)
            pdf.ln(2)
        elif line.startswith('**Keywords:**') or line.startswith('**Palabras clave:**'):
            pdf.set_font('helvetica', 'B', 11)
            pdf.multi_cell(190, 7, line)
            pdf.set_font('helvetica', '', 11)
        else:
            # Bullet points or normal text
            pdf.multi_cell(190, 7, line)

    pdf.output(output_path)

def main():
    draft_dir = 'editorial_neurociencia/preprints_drafts'
    output_dir = 'editorial_neurociencia/preprints_pdf'
    os.makedirs(output_dir, exist_ok=True)

    with open('automation/research_data.json', 'r') as f:
        data = json.load(f)

    for filename in os.listdir(draft_dir):
        if filename.endswith('.md'):
            match = re.search(r'Preprint_Neuropsicologia_(\d+)_(\w+).md', filename)
            if match:
                tid = match.group(1)
                lang = match.group(2)

                topic = next(t for t in data['topics'] if str(t['id']) == tid)
                title_slug = topic['title'].replace(' ', '_').replace(':', '').replace('.', '')

                pdf_filename = f"Preprint_Neuropsicologia_{title_slug}_{lang}_JuanMoisésdelaSerna.pdf"
                create_pdf(os.path.join(draft_dir, filename), os.path.join(output_dir, pdf_filename))
                print(f"Generated {pdf_filename}")

if __name__ == "__main__":
    main()
