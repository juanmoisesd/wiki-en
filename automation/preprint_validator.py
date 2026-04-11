import os
import re
import sys

def validate_preprint(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    errors = []
    sections = ["Abstract", "Keywords", "1. Introduction", "2. Theoretical Background", "3. Method", "4. Results", "Discussion", "Conclusions", "References"]
    for s in sections:
        if s not in content: errors.append(f"Missing section: {s}")
    if "Juan Moisés de la Serna" not in content: errors.append("Incorrect Author")
    if len(content) < 20000: errors.append(f"Length {len(content)} too short")
    citations = re.findall(r'DOI: 10\.', content)
    if len(citations) < 70: errors.append(f"Citations {len(citations)} too low")
    return errors

def main():
    directory = 'preprints_source'
    all_passed = True
    processed = 0
    for filename in os.listdir(directory):
        if filename.endswith('.md') and ('V3' in filename or 'ExtV3' in filename):
            processed += 1
            errors = validate_preprint(os.path.join(directory, filename))
            if errors:
                all_passed = False
                print(f"❌ {filename}: {', '.join(errors)}")
    print(f"\nValidated {processed} preprints.")
    if all_passed and processed > 0:
        print("Success: All preprints pass rigorous standards.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
