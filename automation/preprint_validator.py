import os
import re
import sys

def validate_preprint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # 1. Academic Structure Checks
    sections = [
        "Abstract", "Keywords", "1. Introduction", "2. Literature Review", "3. Method", "4. Results",
        "5. Discussion", "6. Conclusions", "7. Future Directions", "8. References"
    ]
    for section in sections:
        if section not in content:
            errors.append(f"Missing section: {section}")

    # 2. Metadata Checks
    if "Author: Juan Moisés de la Serna" not in content:
        errors.append("Missing or incorrect Author")
    if "ORCID: 0000-0002-8401-8018" not in content:
        errors.append("Missing or incorrect ORCID")

    # 3. Length Checks (Min 15,000 characters for ~6 pages)
    if len(content) < 15000:
        errors.append(f"File too short ({len(content)} chars), expected >15000 for 6+ pages")

    # 4. Citation Count (Target 40+)
    ref_section = content.split("8. References")[-1]
    citations = re.findall(r'\d+\.\s+\w+,', ref_section)
    if len(citations) < 40:
        errors.append(f"Only {len(citations)} citations found, expected 40+")

    # 5. Prohibited content (Neuromyths)
    neuromyths = ["10% brain usage", "learning styles", "right brain vs left brain"]
    for myth in neuromyths:
        if myth in content.lower() and "mito" not in content.lower() and "myth" not in content.lower():
             errors.append(f"Potential neuromyth found without debunking: {myth}")

    return errors

def main():
    directory = 'preprints_source'
    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        return

    all_passed = True
    processed = 0
    # Only validate the 90 new extended ones
    for filename in os.listdir(directory):
        if filename.endswith('.md') and 'Ext_' in filename:
            processed += 1
            path = os.path.join(directory, filename)
            errors = validate_preprint(path)
            if errors:
                all_passed = False
                print(f"❌ {filename}:")
                for err in errors:
                    print(f"  - {err}")

    print(f"\nValidated {processed} extended preprints.")
    if all_passed:
        print("All extended preprints validated successfully.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
