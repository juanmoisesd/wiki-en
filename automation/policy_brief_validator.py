import os
import re
import sys

def validate_policy_brief(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # 1. Authorship Checks
    author_info = [
        "Juan Moisés de la Serna",
        "Universidad Internacional de La Rioja (UNIR), Logroño, Spain",
        "juanmoises.delaserna@unir.net",
        "ORCID: 0000-0002-8401-8018"
    ]
    for info in author_info:
        if info not in content:
            errors.append(f"Missing authorship info: {info}")

    # 2. Structure Checks
    sections = [
        "1. Título",
        "2. Resumen ejecutivo",
        "3. Contexto y problema",
        "4. Evidencia científica",
        "5. Opciones de política",
        "6. Recomendaciones",
        "7. Implicaciones para la implementación",
        "8. Conclusión",
        "9. Referencias"
    ]
    for section in sections:
        if section not in content:
            # Check for slightly different formatting (e.g. ### 1. Título)
            if not re.search(rf'#+ {re.escape(section)}', content):
                errors.append(f"Missing section: {section}")

    # 3. Word Count Check (1500-2000 words)
    # Removing front matter if any and references for a cleaner count
    clean_text = content
    # Rough estimate of words
    words = clean_text.split()
    word_count = len(words)
    if word_count < 1500: # Enforcing 1500 minimum
        errors.append(f"Word count too low: {word_count} words (Target: 1500-2000)")
    elif word_count > 2200:
        errors.append(f"Word count too high: {word_count} words (Target: 1500-2000)")

    # 4. References Check (DOIs or links)
    if "9. Referencias" in content:
        ref_section = content.split("9. Referencias")[1]
        dois = re.findall(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', ref_section, re.I)
        links = re.findall(r'https?://', ref_section)
        if len(dois) + len(links) < 5:
            errors.append("Too few references with DOIs or links found")

    return errors, word_count

def main():
    directory = 'policy_briefs'
    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        return

    all_passed = True
    files = [f for f in os.listdir(directory) if f.endswith('.md')]
    if not files:
        print("No policy briefs found to validate.")
        return

    for filename in files:
        path = os.path.join(directory, filename)
        errors, wc = validate_policy_brief(path)
        if errors:
            all_passed = False
            print(f"❌ {filename} ({wc} words):")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"✅ {filename}: Passed ({wc} words)")

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    main()
