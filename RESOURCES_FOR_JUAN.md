# 🚀 Research Identity Automation System

This system provides "100 Improvements" (technical, visual, and documentation) for your research repositories. It automates the process of transforming a basic repository into a professional, academic landing page.

---

## 🛠️ Components

1.  **`automation/identity_automator.py`**: The core Python engine that:
    - Fixes character encoding (mojibake) in `index.html` and metadata.
    - Injects a modern, responsive 'Research Identity' template into `index.html`.
    - Synchronizes professional documentation (`ABOUT_THE_AUTHOR.md`, `LICENSE`, `CONTRIBUTING.md`).
    - Optimizes Jekyll (`_config.yml`), `sitemap.xml`, and `seo.json` for academic indexing.
2.  **`automation/researcher_profile.json`**: A centralized configuration file for all your professional IDs (ORCID, Scopus, ResearcherID) and institution details.
3.  **`automation/templates/`**: Modular templates for the visual theme and standard documentation.

---

## 🚀 How to Use

To apply these improvements to any of your 71+ repositories, simply:

1.  **Clone** the repository.
2.  **Run** the automator: `python3 automation/identity_automator.py --repo /path/to/repo`
3.  **Push** the changes to GitHub.

---

## ✅ What it Improves

- **Visual Identity:** Modern, responsive, academic design using the Inter font and card-based UI.
- **SEO & Discoverability:** Highwire Press citation metatags, Schema.org (JSON-LD), and professional sitemaps.
- **Content Completeness:** Automatically adds missing `LICENSE`, `CONTRIBUTING.md`, and `ABOUT_THE_AUTHOR.md`.
- **Technical Integrity:** Fixes all character encoding errors and ensures correct GitHub Pages resolution for internal links.

---

[![ORCID](https://img.shields.io/badge/ORCID-0000--0002--8401--8018-green?logo=orcid)](https://orcid.org/0000-0002-8401-8018) [![LinkedIn](https://img.shields.io/badge/LinkedIn-juanmoisesdelaserna-blue?logo=linkedin)](https://www.linkedin.com/in/juanmoisesdelaserna/) [![License: CC0](https://img.shields.io/badge/License-CC0_1.0-lightgrey)](https://creativecommons.org/publicdomain/zero/1.0/)
