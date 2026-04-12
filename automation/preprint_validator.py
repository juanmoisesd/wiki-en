import os
import re
import sys

def validate_preprint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []
    warnings = []

    # Detect language based on path
    is_english = "/en/" in filepath or filepath.startswith("en/")

    # 1. Length Check
    char_count = len(content)
    threshold = 20000 if is_english else 15000
    if char_count < threshold:
        errors.append(f"Length is {char_count} characters, which is below the {threshold} threshold.")

    # 2. Citation Check
    # Looking for APA-style citations like (Author, Year) or references list items
    citations = re.findall(r'\([A-Z][a-z]+.*?, \d{4}\)', content)
    reference_items = re.findall(r'\d+\.\s+[A-Z]', content)
    total_refs = max(len(citations), len(reference_items))

    ref_threshold = 50 if is_english else 40
    if total_refs < ref_threshold:
        errors.append(f"Found {total_refs} references/citations, which is below the {ref_threshold} threshold.")

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
    if is_english:
        required_sections = [
            "Abstract", "Keywords", "Introduction", "Literature Review", "Methodology", "Results", "Discussion", "Conclusion", "References"
        ]
    else:
        required_sections = [
            "Resumen", "Abstract", "Keywords", "Introducción", "Marco teórico", "Metodología", "Resultados", "Discusión", "Conclusiones", "Referencias"
        ]

    for section in required_sections:
        if section.lower() not in content.lower():
            errors.append(f"Missing required section: {section}")

    return errors, warnings

def main():
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = 'preprints_source'

    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        return

    all_passed = True
    for root, dirs, files in os.walk(directory):
        for filename in sorted(files):
            if filename.endswith('.md'):
                path = os.path.join(root, filename)
                errors, warnings = validate_preprint(path)
                if errors:
                    all_passed = False
                    print(f"❌ {path}:")
                    for err in errors:
                        print(f"  - {err}")
                else:
                    print(f"✅ {path}: Passed")

                for warn in warnings:
                    print(f"  ⚠️ {warn}")

    if all_passed:
        print("\nAll preprints validated successfully.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
