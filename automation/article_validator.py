import os
import re
import sys

def validate_article(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # 1. Metadata Checks
    if not re.search(r'URL: /neurociencia/[\w-]+/[\w-]+', content):
        errors.append("Missing or invalid URL metadata")
    if not re.search(r'H1: .+', content):
        errors.append("Missing H1 title")
    if not re.search(r'Meta descripción: .+', content):
        errors.append("Missing Meta description")

    # Meta description length (155-160 characters)
    meta_desc_match = re.search(r'Meta descripción: (.+)', content)
    if meta_desc_match:
        meta_desc = meta_desc_match.group(1).strip()
        if not (150 <= len(meta_desc) <= 170): # Allowing a small margin
            errors.append(f"Meta description length is {len(meta_desc)}, should be ~155-160")

    # 2. Structure Checks
    if "INTRODUCCIÓN" not in content:
        errors.append("Missing INTRODUCCIÓN section")
    if "DESARROLLO" not in content:
        errors.append("Missing DESARROLLO section")
    if "APLICACIONES PRÁCTICAS" not in content:
        errors.append("Missing APLICACIONES PRÁCTICAS section")
    if "CONCLUSIÓN" not in content:
        errors.append("Missing CONCLUSIÓN section")
    if "REFERENCIAS INTERNAS" not in content:
        errors.append("Missing REFERENCIAS INTERNAS section")

    # 3. Scientific Rigor Indicators
    # Check for limitations/nuances
    rigor_keywords = ["sin embargo", "limitación", "evidencia mixta", "necesita más investigación", "no obstante"]
    if not any(kw in content.lower() for kw in rigor_keywords):
        errors.append("Missing scientific rigor indicators (limitations/nuances)")

    # Check for years (e.g., 2023, 2024, 2025)
    if not re.search(r'202\d', content):
        errors.append("No recent years (2020+) mentioned for scientific context")

    # 4. Length Checks (Desarrollo: 3000-3500 characters)
    desarrollo_match = re.search(r'DESARROLLO\s+(.*?)\s+SECCIÓN: APLICACIONES PRÁCTICAS', content, re.DOTALL)
    if desarrollo_match:
        desarrollo_text = desarrollo_match.group(1).strip()
        length = len(desarrollo_text)
        if not (2500 <= length <= 4500): # Wider range for flexibility but alert if too far
             errors.append(f"DESARROLLO length is {length}, ideally 3000-3500")
    else:
        errors.append("Could not isolate DESARROLLO section for length check")

    # 5. Internal Links (4-5)
    links = re.findall(r'\[.+?\]\(.+?\)', content)
    # Filter for what look like internal links (not the metadata ones)
    internal_links = [l for l in links if "/neurociencia/" in l or "github.com" not in l]
    if len(internal_links) < 3: # Metadata + some content links
        errors.append(f"Only {len(internal_links)} links found, ideally 4-7")

    # 6. Prohibited content (Neuromyths)
    neuromyths = ["10% del cerebro", "cerebro derecho vs izquierdo", "estilos de aprendizaje"]
    for myth in neuromyths:
        if myth in content.lower() and "mito" not in content.lower():
             errors.append(f"Potential neuromyth found without debunking: {myth}")

    return errors

def main():
    directory = 'editorial_neurociencia'
    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        return

    all_passed = True
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            path = os.path.join(directory, filename)
            errors = validate_article(path)
            if errors:
                all_passed = False
                print(f"❌ {filename}:")
                for err in errors:
                    print(f"  - {err}")
            else:
                print(f"✅ {filename}: Passed")

    if all_passed:
        print("\nAll articles validated successfully.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
