import os
import re
import sys

def validate_preprint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # 1. Academic Structure Checks
    sections = [
        "Abstract", "Keywords", "1. Introduction", "2. Method", "3. Results",
        "4. Discussion", "5. Conclusions", "6. Future Directions", "7. References"
    ]
    for section in sections:
        if section not in content:
            errors.append(f"Missing section: {section}")

    # 2. Metadata Checks
    if "Author: Juan Moisés de la Serna" not in content:
        errors.append("Missing or incorrect Author")
    if "ORCID: 0000-0002-8401-8018" not in content:
        errors.append("Missing or incorrect ORCID")
    if "Affiliation: University International of La Rioja (UNIR)" not in content:
        errors.append("Missing or incorrect Affiliation")

    # 3. Citation Count (approximate)
    ref_section = content.split("7. References")[-1]
    # Match numbered references like "1. Author (Year)"
    citations = re.findall(r'\d+\.\s+\w+,', ref_section)
    if len(citations) < 20:
        errors.append(f"Only {len(citations)} citations found, expected 20-30")

    # 4. Cross-citations
    # Each paper should cite at least 2 other preprints (which are in the titles)
    cross_cites = re.findall(r'Zenodo Preprint', ref_section)
    if len(cross_cites) < 2:
        errors.append(f"Only {len(cross_cites)} cross-citations found, expected at least 2")

    # 5. Scientific Rigor (Recent Years 2020+)
    recent_years = re.findall(r'202\d', content)
    if len(recent_years) < 10:
        errors.append("Insufficient recent years (2020+) mentioned for academic rigor")

    # 6. Prohibited content (Neuromyths)
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
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            path = os.path.join(directory, filename)
            errors = validate_preprint(path)
            if errors:
                all_passed = False
                print(f"❌ {filename}:")
                for err in errors:
                    print(f"  - {err}")
            else:
                print(f"✅ {filename}: Passed")

    if all_passed:
        print("\nAll preprints validated successfully.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
