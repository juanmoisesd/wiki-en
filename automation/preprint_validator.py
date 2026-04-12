import os
import re
import sys

def validate_preprint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []
    warnings = []

    # 1. Length Check (15,000+ characters)
    char_count = len(content)
    if char_count < 15000:
        errors.append(f"Length is {char_count} characters, which is below the 15,000 threshold.")

    # 2. Citation Check (40+ citations)
    # Looking for APA-style citations like (Author, Year) or references list items
    citations = re.findall(r'\([A-Z][a-z]+.*?, \d{4}\)', content)
    reference_items = re.findall(r'\d+\.\s+[A-Z]', content)
    total_refs = max(len(citations), len(reference_items))

    if total_refs < 40:
        errors.append(f"Found {total_refs} references/citations, which is below the 40 threshold.")

    # 3. Authorship Block
    required_authorship = [
        "Juan Moisés de la Serna",
        "Universidad Internacional de La Rioja (UNIR)",
        "juanmoises.delaserna@unir.net",
        "ORCID: 0000-0002-8401-8018"
    ]
    for author_info in required_authorship:
        if author_info not in content:
            errors.append(f"Missing required authorship info: {author_info}")

    # 4. Academic Structure
    required_sections = [
        "Resumen", "Abstract", "Keywords", "Introducción", "Marco teórico", "Metodología", "Resultados", "Discusión", "Conclusiones", "Referencias"
    ]
    for section in required_sections:
        if section.lower() not in content.lower():
            errors.append(f"Missing required section: {section}")

    return errors, warnings

def main():
    directory = 'preprints_source'
    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        return

    all_passed = True
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.md'):
            path = os.path.join(directory, filename)
            errors, warnings = validate_preprint(path)
            if errors:
                all_passed = False
                print(f"❌ {filename}:")
                for err in errors:
                    print(f"  - {err}")
            else:
                print(f"✅ {filename}: Passed")

            for warn in warnings:
                print(f"  ⚠️ {warn}")

    if all_passed:
        print("\nAll preprints validated successfully.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
