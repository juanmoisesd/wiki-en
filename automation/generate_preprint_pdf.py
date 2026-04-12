import os
import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class PreprintPDF(FPDF):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Attempt to find DejaVuSans in common locations
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
            "assets/fonts/DejaVuSans.ttf"
        ]
        font_bold_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
            "assets/fonts/DejaVuSans-Bold.ttf"
        ]

        found_font = False
        for p in font_paths:
            if os.path.exists(p):
                self.add_font("DejaVu", "", p)
                found_font = True
                break

        if not found_font:
            # Fallback to Helvetica (Built-in)
            self.add_font("DejaVu", "", style="", fname="helvetica")

        found_bold = False
        for p in font_bold_paths:
            if os.path.exists(p):
                self.add_font("DejaVu", "B", p)
                found_bold = True
                break

        if not found_bold:
            self.add_font("DejaVu", "B", style="B", fname="helvetica")

    def header(self):
        if self.page_no() > 1:
            self.set_font('DejaVu', '', 8)
            self.cell(0, 10, 'Preprint - Juan Moisés de la Serna', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')

    def footer(self):
        self.set_y(-15)
        self.set_font('DejaVu', '', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def convert_md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pdf = PreprintPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    for line in lines:
        line = line.strip()

        # Skip horizontal rules or purely symbol lines that cause layout errors
        if re.match(r'^[|\-=\s*]+$', line) and ('|' in line or '-' in line):
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
        elif line.startswith('**') and line.endswith('**') and len(line) < 100:
            pdf.set_font('DejaVu', 'B', 11)
            pdf.multi_cell(0, 8, line.replace('**', ''))
            pdf.ln(2)

        # Normal text
        elif line:
            pdf.set_font('DejaVu', '', 11)
            # Remove MD bold/italic markup
            clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            clean_line = re.sub(r'\*(.*?)\*', r'\1', clean_line)
            # Basic table row cleanup if it leaked through
            if clean_line.startswith('|'):
                clean_line = clean_line.replace('|', ' ').strip()
                if not clean_line: continue
                pdf.set_font('courier', '', 9)

            try:
                pdf.multi_cell(0, 7, clean_line)
                pdf.ln(2)
            except Exception:
                # Last resort for layout errors
                continue

        # Empty line
        else:
            pdf.ln(2)

    pdf.output(pdf_path)

def main():
    source_dirs = ['preprints_source', 'preprints_source/en']

    for source_dir in source_dirs:
        if not os.path.exists(source_dir): continue

        if 'en' in source_dir:
            output_dir = 'preprints_pdf/en'
        else:
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
