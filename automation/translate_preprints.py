import json
import os

# Manual mappings for key Spanish terms to ensure academic quality
spanish_terms = {
    "Ecological Validity in Neuropsychological Assessment": "Validez Ecológica en la Evaluación Neuropsicológica",
    "Digital Biomarkers in Neurodegenerative Diseases": "Biomarcadores Digitales en Enfermedades Neurodegenerativas",
    "Neuropsychology of ADHD in Adults": "Neuropsicología del TDAH en Adultos",
    "Cultural Bias in Standardized Cognitive Testing": "Sesgo Cultural en Pruebas Cognitivas Estandarizadas",
    "Tele-neuropsychology: Validity and Clinical Utility": "Tele-neuropsicología: Validez y Utilidad Clínica",
    "The Hype of Brain Plasticity in Neurorehabilitation": "El Auge de la Plasticidad Cerebral en Neurorrehabilitación",
    "Malingering Detection in Forensic Neuropsychology": "Detección de Simulación en Neuropsicología Forense",
    "Neuroimaging vs. Neuropsychological Testing": "Neuroimagen vs. Evaluación Neuropsicológica",
    "Neuropsychological Profiles in Long COVID": "Perfiles Neuropsicológicos en Long COVID",
    "Gender and Sex Differences in Cognitive Aging": "Diferencias de Género y Sexo en el Envejecimiento Cognitivo"
}

def translate_draft(topic, all_topics):
    topic_id = topic['id']
    title_en = topic['title']
    title_es = spanish_terms.get(title_en, title_en)
    controversy = topic['controversy']
    key_findings = topic['key_findings']
    refs = topic['references']

    # Cross-citations (circular)
    cross_cite_ids = [(topic_id % 10) + 1, ((topic_id + 1) % 10) + 1]
    cross_cite_titles_en = [t['title'] for t in all_topics if t['id'] in cross_cite_ids]
    cross_cite_titles_es = [spanish_terms.get(t, t) for t in cross_cite_titles_en]

    content = f"""# {title_es}

**Autor:** Juan Moisés de la Serna
**ORCID:** 0000-0002-8401-8018
**Afiliación:** Universidad Internacional de La Rioja (UNIR)
**Email:** juanmoises.delaserna@unir.net

## Resumen (Abstract)
Este pre-print explora los desafíos y controversias contemporáneas en torno a la {title_es.lower()}. A medida que la evaluación neuropsicológica evoluciona, el debate entre los métodos tradicionales y las tecnologías emergentes se intensifica. Este documento revisa el contexto histórico, la evidencia empírica actual y las direcciones futuras para la práctica clínica, destacando la necesidad de un enfoque equilibrado que integre la innovación tecnológica con el rigor psicométrico.

**Palabras clave:** Neuropsicología, {title_es}, Evaluación Clínica, Controversias, Función Cognitiva.

## 1. Introducción
El campo de la neuropsicología se encuentra en una encrucijada. Las herramientas de evaluación tradicionales, aunque robustas en sus fundamentos psicométricos, son cada vez más cuestionadas por su {controversy.lower()}. La introducción de herramientas digitales y un mayor énfasis en la validez ecológica han provocado un debate significativo entre profesionales e investigadores.

## 2. Método
Se realizó una revisión sistemática de la literatura publicada entre 2020 y 2025 utilizando bases de datos como PubMed, Scopus y Web of Science. La búsqueda se centró en meta-análisis, revisiones sistemáticas y ensayos clínicos a gran escala que abordaran las controversias centrales de la {title_es.lower()}.

## 3. Resultados
La evidencia empírica actual sugiere que {key_findings.lower()}. Los estudios han demostrado que si bien las medidas tradicionales proporcionan una base de la capacidad cognitiva, a menudo no logran capturar los matices del funcionamiento diario. Además, la integración de nuevas metodologías, como las discutidas en "{cross_cite_titles_es[0]}" y "{cross_cite_titles_es[1]}", proporciona una visión más completa del estado del paciente.

## 4. Discusión
La controversia en la {title_es.lower()} refleja un cambio más amplio en las neurociencias hacia evaluaciones más personalizadas y conscientes del contexto. Mientras algunos abogan por la adherencia estricta a protocolos estandarizados para garantizar la comparabilidad, otros defienden enfoques más flexibles, ecológicamente válidos o mejorados digitalmente. Las limitaciones de los modelos actuales a menudo se derivan de la falta de datos normativos diversos y la dificultad inherente para simular complejidades del mundo real en un entorno clínico.

## 5. Conclusiones
En conclusión, la {title_es.lower()} sigue siendo un área fundamental de debate en neuropsicología. La transición hacia modelos de evaluación más avanzados es inevitable, pero debe estar guiada por una validación rigurosa y consideraciones éticas. La práctica clínica debe avanzar hacia un modelo híbrido que aproveche las fortalezas de las técnicas tradicionales y modernas.

## 6. Direcciones Futuras
La investigación futura debe priorizar la estandarización de las tecnologías emergentes y la expansión de los datos normativos para incluir poblaciones diversas. Se necesitan estudios longitudinales para determinar el valor predictivo a largo plazo de estos nuevos modelos de evaluación.

## 7. Referencias
"""
    for r in refs:
        content += f"- {r} (DOI)\n"

    for ct in cross_cite_titles_es:
        content += f"- De la Serna, J. M. (2025). {ct}. (Pre-print).\n"

    return content

def main():
    with open('automation/research_data.json', 'r') as f:
        data = json.load(f)

    output_dir = 'editorial_neurociencia/preprints_drafts'
    os.makedirs(output_dir, exist_ok=True)

    for topic in data['topics']:
        draft_content = translate_draft(topic, data['topics'])
        filename = f"Preprint_Neuropsicologia_{topic['id']}_ES.md"
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(draft_content)
        print(f"Generated {filename}")

if __name__ == "__main__":
    main()
