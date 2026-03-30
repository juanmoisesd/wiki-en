import os
import json
import re
from pathlib import Path

def load_profile(path="automation/researcher_profile.json"):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def sanitize_text(text):
    # Fix common mojibake/encoding issues
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
    # Placeholder for real template logic
    print(f"Creating professional index.html for {repo_name}...")
    # (Implementation details omitted for brevity in this step)

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
    # Logic to iterate over repositories and apply changes
    print("Research Identity Automator initialized.")

if __name__ == "__main__":
    main()
