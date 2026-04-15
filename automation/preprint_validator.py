import os
import re
import sys

def validate_preprint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # 1. Author and Affiliation Check
    if "Juan Moisés de la Serna" not in content:
        errors.append("Missing author: Juan Moisés de la Serna")
    if "Universidad Internacional de La Rioja" not in content and "UNIR" not in content:
        errors.append("Missing affiliation: UNIR")
    if "0000-0002-8401-8018" not in content:
        errors.append("Missing ORCID: 0000-0002-8401-8018")

    # 2. PRISMA Structure Check
    sections = [
        r"Título",
        r"Resumen",
        r"Palabras clave",
        r"Introducción",
        r"Métodos",
        r"Resultados",
        r"Discusión",
        r"Conclusiones",
        r"Referencias"
    ]
    for section in sections:
        if not re.search(fr"### \d+\. \*\*{section}\*\*", content, re.IGNORECASE):
            # Fallback for simple match if numbered heading not found
            if section.lower() not in content.lower():
                errors.append(f"Missing section: {section}")

    # 3. Length Check (15,000+ characters)
    length = len(content)
    if length < 15000:
        errors.append(f"Length is {length} characters, should be at least 15,000")

    # 4. Citation Count Check (40+ in References)
    ref_match = re.search(r"### 9\. \*\*Referencias\*\*.*", content, re.DOTALL | re.IGNORECASE)
    if ref_match:
        ref_text = ref_match.group(0)
        # Matches patterns like "1. ", "2. " or "* " or "[1] "
        citations = len(re.findall(r"\n\d+\.\s", ref_text))
        if citations == 0:
            citations = len(re.findall(r"\n\* ", ref_text))

        if citations < 40:
            errors.append(f"Found {citations} references, should be at least 40")
    else:
        errors.append("Could not find References section to count citations")

    return errors

def main():
    directory = 'preprints_source'
    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        sys.exit(1)

    all_passed = True
    files = [f for f in os.listdir(directory) if f.endswith('.md')]

    if not files:
        print("No markdown files found in preprints_source.")
        sys.exit(1)

    for filename in sorted(files):
        path = os.path.join(directory, filename)
        errors = validate_preprint(path)
        if errors:
            all_passed = False
            print(f"❌ {filename}:")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"✅ {filename}: Passed (Length: {len(open(path, 'r', encoding='utf-8').read())})")

    if all_passed:
        print("\nAll preprints validated successfully.")
    else:
        print("\nValidation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
