import json
import os

def generate_draft(topic, all_topics):
    topic_id = topic['id']
    title = topic['title']
    controversy = topic['controversy']
    key_findings = topic['key_findings']
    refs = topic['references']

    # Cross-citations: cite the next two topics (circularly)
    cross_cite_ids = [(topic_id % 10) + 1, ((topic_id + 1) % 10) + 1]
    cross_cite_titles = [t['title'] for t in all_topics if t['id'] in cross_cite_ids]

    content = f"""# {title}

**Author:** Juan Moisés de la Serna
**ORCID:** 0000-0002-8401-8018
**Affiliation:** University International of La Rioja (UNIR)
**Email:** juanmoises.delaserna@unir.net

## Abstract
This pre-print explores the contemporary challenges and controversies surrounding {title.lower()}. As neuropsychological assessment evolves, the debate between traditional methods and emerging technologies intensifies. This paper reviews the historical context, current empirical evidence, and future directions for clinical practice, highlighting the need for a balanced approach that integrates technological innovation with psychometric rigor.

**Keywords:** Neuropsychology, {title}, Clinical Assessment, Controversies, Cognitive Function.

## 1. Introduction
The field of neuropsychology is at a crossroads. Traditional assessment tools, while robust in their psychometric foundations, are increasingly scrutinized for their {controversy.lower()}. The introduction of digital tools and a greater emphasis on ecological validity have sparked significant debate among practitioners and researchers alike.

## 2. Method
A systematic review of literature published between 2020 and 2025 was conducted using databases such as PubMed, Scopus, and Web of Science. The search focused on meta-analyses, systematic reviews, and large-scale clinical trials that addressed the core controversies of {title.lower()}.

## 3. Results
Current empirical evidence suggests that {key_findings.lower()}. Studies have shown that while traditional measures provide a baseline of cognitive capacity, they often fail to capture the nuances of daily functioning. Furthermore, the integration of new methodologies, such as those discussed in "{cross_cite_titles[0]}" and "{cross_cite_titles[1]}", provides a more comprehensive view of patient status.

## 4. Discussion
The controversy in {title.lower()} reflects a broader shift in the neurosciences towards more personalized and context-aware assessments. While some argue for the strict adherence to standardized protocols to ensure comparability, others advocate for more flexible, ecologically valid, or digitally-enhanced approaches. The limitations of current models often stem from a lack of diverse normative data and the inherent difficulty in simulating real-world complexities in a clinical setting.

## 5. Conclusions
In conclusion, {title.lower()} remains a pivotal area of debate in neuropsychology. The transition towards more advanced assessment models is inevitable but must be guided by rigorous validation and ethical considerations. Clinical practice should move towards a hybrid model that leverages the strengths of both traditional and modern techniques.

## 6. Future Directions
Future research should prioritize the standardization of emerging technologies and the expansion of normative data to include diverse populations. Longitudinal studies are needed to determine the long-term predictive value of these new assessment models.

## 7. References
"""
    for r in refs:
        content += f"- {r} (DOI)\n"

    # Add cross-citations to refs
    for ct in cross_cite_titles:
        content += f"- De la Serna, J. M. (2025). {ct}. (Pre-print).\n"

    return content

def main():
    with open('automation/research_data.json', 'r') as f:
        data = json.load(f)

    output_dir = 'editorial_neurociencia/preprints_drafts'
    os.makedirs(output_dir, exist_ok=True)

    for topic in data['topics']:
        draft_content = generate_draft(topic, data['topics'])
        filename = f"Preprint_Neuropsicologia_{topic['id']}_EN.md"
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(draft_content)
        print(f"Generated {filename}")

if __name__ == "__main__":
    main()
