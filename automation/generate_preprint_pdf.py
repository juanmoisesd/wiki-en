import os
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class PreprintPDF(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        self.add_font("DejaVu", "", font_path)
        self.add_font("DejaVu", "B", font_bold_path)

    def header(self):
        if self.page_no() > 1:
            self.set_font('DejaVu', '', 8)
            self.cell(0, 10, 'Preprint - Juan Moisés de la Serna', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def convert_md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pdf = PreprintPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    for line in lines:
        line = line.strip()

        # Skip Markdown table lines because they cause layout issues with multi_cell(0, ...)
        if line.startswith('|'):
            continue

        # Title (H1)
        if line.startswith('# '):
            pdf.set_font('DejaVu', 'B', 16)
            pdf.multi_cell(0, 10, line[2:])
            pdf.ln(5)

        # Subtitles (H2)
        elif line.startswith('## '):
            pdf.set_font('DejaVu', 'B', 14)
            pdf.multi_cell(0, 10, line[3:])
            pdf.ln(3)

        # Subtitles (H3)
        elif line.startswith('### '):
            pdf.set_font('DejaVu', 'B', 12)
            pdf.multi_cell(0, 10, line[4:])
            pdf.ln(2)

        # Bold author / metadata
        elif line.startswith('**'):
            pdf.set_font('DejaVu', 'B', 11)
            pdf.multi_cell(0, 8, line.replace('**', ''))
            pdf.ln(2)

        # Normal text
        elif line:
            pdf.set_font('DejaVu', '', 11)
            clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            clean_line = re.sub(r'\*(.*?)\*', r'\1', clean_line)
            pdf.multi_cell(0, 7, clean_line)
            pdf.ln(2)

        # Empty line
        else:
            pdf.ln(2)

    pdf.output(pdf_path)

def main():
    source_dir = 'preprints_source'
    output_dir = 'preprints_pdf'
    os.makedirs(output_dir, exist_ok=True)

    for filename in sorted(os.listdir(source_dir)):
        if filename.endswith('.md'):
            md_path = os.path.join(source_dir, filename)
            pdf_filename = filename.replace('.md', '.pdf')
            pdf_path = os.path.join(output_dir, pdf_filename)
            print(f"Generating {pdf_path}...")
            try:
                convert_md_to_pdf(md_path, pdf_path)
            except Exception as e:
                print(f"Error generating {pdf_path}: {e}")

if __name__ == "__main__":
    main()
