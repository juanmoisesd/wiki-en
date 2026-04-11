import os
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class PreprintPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Times", "I", 8)
            self.cell(0, 10, "Juan Moisés de la Serna - Educational Preprints 2025", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def markdown_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract metadata
    title_match = re.search(r'Title: (.*)', content)
    title = title_match.group(1) if title_match else "Untitled Preprint"
    author = "Juan Moisés de la Serna"
    orcid = "0000-0002-8401-8018"
    affiliation = "University International of La Rioja (UNIR)"
    email = "juanmoises.delaserna@unir.net"

    pdf = PreprintPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(25, 25, 25)

    # Title Page
    pdf.add_page()
    pdf.set_font("Times", "B", 24)
    pdf.ln(60)
    pdf.multi_cell(0, 15, title, align="C")
    pdf.ln(20)
    pdf.set_font("Times", "B", 16)
    pdf.cell(0, 10, author, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", "", 12)
    pdf.cell(0, 10, f"ORCID: {orcid}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, affiliation, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, email, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(40)
    pdf.set_font("Times", "I", 10)
    pdf.cell(0, 10, "Academic Preprint - Published via Zenodo", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Main Content
    pdf.add_page()
    pdf.set_font("Times", "", 12)

    # Skip YAML header
    if content.startswith('---'):
        end_yaml = content.find('---', 3)
        if end_yaml != -1:
            content = content[end_yaml+3:].strip()

    # Sanitize content for non-latin characters before splitting
    content = content.replace('ó', 'o').replace('í', 'i').replace('é', 'e').replace('á', 'a').replace('ú', 'u')
    content = content.replace('ñ', 'n').replace('Ü', 'U').replace('ü', 'u')

    sections = content.split('\n')
    for line in sections:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue

        if line.startswith('# '):
            pdf.set_font("Times", "B", 18)
            text = line[2:]
        elif line.startswith('## '):
            pdf.ln(2)
            pdf.set_font("Times", "B", 14)
            text = line[3:]
        elif line.startswith('### '):
            pdf.set_font("Times", "B", 12)
            text = line[4:]
        elif line.startswith('**'):
            pdf.set_font("Times", "B", 12)
            text = line.replace('**', '')
        else:
            pdf.set_font("Times", "", 12)
            text = line.replace('*', '')

        # Final encoding check
        clean_text = text.encode('latin-1', 'replace').decode('latin-1')

        try:
            pdf.multi_cell(w=0, h=8, text=clean_text)
        except:
            pdf.write(h=8, text=clean_text)
            pdf.ln(8)

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    pdf.output(pdf_path)

if __name__ == "__main__":
    src_dir = "preprints_source"
    out_dir = "preprints_pdf"
    for filename in sorted(os.listdir(src_dir)):
        if filename.endswith('.md'):
            md_path = os.path.join(src_dir, filename)
            pdf_path = os.path.join(out_dir, filename.replace('.md', '.pdf'))
            markdown_to_pdf(md_path, pdf_path)
            print(f"Generated {pdf_path}")
