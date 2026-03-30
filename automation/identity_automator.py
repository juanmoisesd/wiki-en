import os
import json
import re
from pathlib import Path

def load_profile(path="automation/researcher_profile.json"):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def sanitize_text(text):
    replaces = {
        'ð¬ð§': '🇬🇧',
        'ð': '📁',
        'ð': '📋',
        'ð¤': '👤',
        'ð': '📚',
        'ð': '🔗',
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú', 'Ã±': 'ñ',
        'Ã\x81': 'Á', 'Ã\x89': 'É', 'Ã\x8d': 'Í', 'Ã\x93': 'Ó', 'Ã\x9a': 'Ú', 'Ã\x91': 'Ñ'
    }
    for old, new in replaces.items():
        text = text.replace(old, new)
    return text

def create_index_html(repo_dir, profile):
    repo_name = os.path.basename(repo_dir)
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{repo_name} | {profile['name']} | Open Research</title>
  <meta name="description" content="Research repository: {repo_name} managed by {profile['name']} · ORCID {profile['orcid']}">
  <meta name="author" content="{profile['name']}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/research-identity.css">
</head>
<body>
<div class="container">
  <header>
    <h1>📁 {repo_name}</h1>
    <p class="subtitle">Research Hub — {profile['name']} · ORCID {profile['orcid']}</p>
  </header>
  <main>
    <section>
      <h2>📋 Project Overview</h2>
      <p>This repository is part of a larger collection of over 1,273 datasets managed by <strong>{profile['name']}</strong>.</p>
      <nav class="nav-links">
        <a href="README.html">↗ Read Documentation</a>
        <a href="GLOSSARY.html">↗ Technical Glossary</a>
      </nav>
    </section>
  </main>
  <footer>
    <p>© 2025 {profile['name']} · <a href="https://orcid.org/{profile['orcid']}">ORCID: {profile['orcid']}</a></p>
  </footer>
</div>
</body>
</html>"""
    with open(os.path.join(repo_dir, "index.html"), 'w', encoding='utf-8') as f:
        f.write(template)

def setup_jekyll_config(repo_dir, profile):
    config_path = os.path.join(repo_dir, "_config.yml")
    repo_name = os.path.basename(repo_dir)
    config_content = f"""# Professional Jekyll Configuration
title: "{repo_name}"
description: "Research repository managed by {profile['name']} · ORCID {profile['orcid']}"
url: "https://juanmoisesd.github.io"
baseurl: "/{repo_name}"

author:
  name: "{profile['name']}"
  orcid: "{profile['orcid']}"
  linkedin: "https://www.linkedin.com/in/{profile['linkedin']}/"
  institution: "{profile['institution']}"

plugins:
  - jekyll-seo-tag
  - jekyll-sitemap
  - jekyll-feed

include:
  - README.md
  - GLOSSARY.md
  - ABOUT_THE_AUTHOR.md
  - CITATION_GUIDE.md
  - CONTRIBUTING.md
  - DATA_MANAGEMENT_PLAN.md
  - LICENSE
  - robots.txt
  - sitemap.xml
  - seo.json

exclude:
  - Gemfile
  - Gemfile.lock
  - node_modules
  - vendor
  - .github
"""
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)

def main():
    profile = load_profile()
    print("Research Identity Automator initialized.")
    # Here you would add logic to scan and update repositories

if __name__ == "__main__":
    main()
