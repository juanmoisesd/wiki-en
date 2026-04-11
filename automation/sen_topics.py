SEN_TYPES = [
    "Autism Spectrum Disorder (ASD)", "ADHD", "Dyslexia",
    "Intellectual Disability", "Giftedness", "Hearing Impairment",
    "Visual Impairment", "Physical Disability", "Language Disorders", "Behavioral Disorders"
]

EDU_LEVELS = [
    "Infantil", "Primaria", "Secundaria", "Bachillerato",
    "Undergraduate (Grado)", "Postgraduate (Postgrado)", "Doctoral Research", "Adult Education", "Vocational Training"
]

SEN_TOPICS = []
for sen in SEN_TYPES:
    for level in EDU_LEVELS:
        SEN_TOPICS.append({
            "id": f"SEN_{sen[:3].upper().replace(' ', '')}_{level.split()[0]}",
            "sen": sen,
            "level": level,
            "title": f"Interdisciplinary Approaches to {sen} in {level}: A Comprehensive Review of Evidence-Based Practices (2020-2025)"
        })
