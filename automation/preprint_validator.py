import os
import json
import re

def validate_preprint(markdown_path):
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # Structure
    required_sections = ["## Abstract", "## 1. Introduction", "## 2. Method", "## 3. Results", "## 4. Discussion", "## 5. Conclusions", "## 6. Future Directions", "## 7. References"]
    # Adjust for Spanish
    if "_ES.md" in markdown_path:
        required_sections = ["## Resumen (Abstract)", "## 1. Introducción", "## 2. Método", "## 3. Resultados", "## 4. Discusión", "## 5. Conclusiones", "## 6. Direcciones Futuras", "## 7. Referencias"]

    for section in required_sections:
        if section not in content:
            errors.append(f"Missing section: {section}")

    # Length (approximate, academic papers should be substantial)
    if len(content) < 2000:
        errors.append(f"Content too short: {len(content)} characters")

    # Cross-citations (should have at least 2)
    citations = re.findall(r'De la Serna, J\. M\. \(2025\)\.', content)
    if len(citations) < 2:
        errors.append(f"Only {len(citations)} cross-citations found, expected at least 2")

    # Author Info
    if "Juan Moisés de la Serna" not in content:
        errors.append("Author name missing")
    if "0000-0002-8401-8018" not in content:
        errors.append("ORCID missing")

    return errors

def main():
    draft_dir = 'editorial_neurociencia/preprints_drafts'
    pdf_dir = 'editorial_neurociencia/preprints_pdf'

    all_passed = True

    # Validate Drafts
    for filename in os.listdir(draft_dir):
        if filename.endswith('.md'):
            path = os.path.join(draft_dir, filename)
            errors = validate_preprint(path)
            if errors:
                all_passed = False
                print(f"❌ {filename}:")
                for err in errors:
                    print(f"  - {err}")
            else:
                print(f"✅ {filename}: Draft Passed")

    # Validate PDF existence
    manifest_path = 'automation/zenodo_manifest.json'
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        for item in manifest:
            pdf_path = item['file_path']
            if not os.path.exists(pdf_path):
                all_passed = False
                print(f"❌ PDF missing: {pdf_path}")
            else:
                print(f"✅ PDF exists: {os.path.basename(pdf_path)}")

    if all_passed:
        print("\nAll pre-prints validated successfully.")
    else:
        print("\nValidation failed.")
        exit(1)

if __name__ == "__main__":
    main()
