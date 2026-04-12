import os
import sys
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import re

class PolicyBriefPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Policy Brief - Juan Moisés de la Serna', align='R')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def clean_text_for_pdf(text):
    replacements = {
        '\u2014': '-',
        '\u2013': '-',
        '\u201c': '"',
        '\u201d': '"',
        '\u2018': "'",
        '\u2019': "'",
        '\u2026': '...',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

def render_markdown_line(pdf, line, width):
    line = clean_text_for_pdf(line)

    # Check for Headers
    if line.startswith('# '):
        pdf.set_font('helvetica', 'B', 16)
        pdf.multi_cell(width, 10, line[2:])
        pdf.ln(5)
        return
    elif line.startswith('## ') or line.startswith('### '):
        text = line.lstrip('# ')
        pdf.set_font('helvetica', 'B', 12)
        pdf.multi_cell(width, 10, text)
        pdf.ln(2)
        return

    # Handle inline bold and italics using write_html for simplicity if available,
    # but we will use a manual approach for better control over multi_cell behavior.

    # Manual approach: split by markdown markers
    # This is a bit complex for multi-cell.
    # fpdf2 has a 'write' method that handles flow but not easily for justified text in multi_cell.
    # We will use write_html or a simplified multi-style approach.

    # Let's try write_html which is built into fpdf2 for basic tags
    html_line = line
    # Convert **bold** to <b>bold</b>
    html_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html_line)
    # Convert *italic* to <i>italic</i>
    html_line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', html_line)

    pdf.set_font('helvetica', '', 10)
    # write_html does not support alignment='J' easily in all versions,
    # but we can use multi_cell with markdown=True if using newer fpdf2 versions!
    try:
        pdf.multi_cell(width, 7, html_line, markdown=True)
    except:
        # Fallback to simple text if markdown=True fails
        clean_line = line.replace('**', '').replace('*', '')
        pdf.multi_cell(width, 7, clean_line)

def create_pdf(markdown_path, output_path):
    with open(markdown_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pdf = PolicyBriefPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    effective_width = pdf.w - 2 * pdf.l_margin

    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue

        render_markdown_line(pdf, line, effective_width)

    pdf.output(output_path)
    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_pdf.py <input.md> <output.pdf>")
    else:
        create_pdf(sys.argv[1], sys.argv[2])
