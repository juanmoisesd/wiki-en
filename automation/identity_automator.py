import os
import json
import datetime
import argparse

class IdentityAutomator:
    """
    Research Identity Automator 10.0
    Ensures all 1,273+ repositories maintain a 'Super Visually Attractive'
    and 'Citable Consultation Instrument' status.
    """
    def __init__(self, profile_path="automation/researcher_profile.json"):
        self.profile = self.load_profile(profile_path)
        self.year = datetime.datetime.now().year

    def load_profile(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_citation_apa(self, repo_name):
        return f"{self.profile['name']} ({self.year}). {repo_name.replace('-', ' ').title()}. GitHub. https://github.com/juanmoisesd/{repo_name}"

    def apply_academic_header(self, html_content, repo_name):
        """Injects the global academic nav and visual identity into an existing HTML file."""
        nav_html = f"""
<nav class="global-nav">
  <div class="container">
    <a href="https://juanmoisesd.github.io/wiki-en/index.html" class="brand">
      <img src="https://juanmoisesd.github.io/wiki-en/assets/images/research-logo.svg" width="30" height="30" alt="Logo">
      J.M. DE LA SERNA TUYA
    </a>
    <div class="nav-links">
      <a href="https://juanmoisesd.github.io/wiki-en/catalog.html">Catalog</a>
      <a href="https://juanmoisesd.github.io/wiki-en/dashboard.html">Dashboard</a>
      <button class="lang-toggle" onclick="toggleLanguage()" style="background:none; border:none; color:white; cursor:pointer; font-weight:700">EN/ES</button>
      <button class="theme-toggle" onclick="toggleTheme()">🌓</button>
    </div>
  </div>
</nav>"""
        if "</head>" in html_content:
            style_ref = '<link rel="stylesheet" href="https://juanmoisesd.github.io/wiki-en/assets/css/research-identity.css">'
            html_content = html_content.replace("</head>", f"{style_ref}\n</head>")

        if "<body>" in html_content:
            html_content = html_content.replace("<body>", f"<body>\n{nav_html}")

        return html_content

    def update_readme(self, repo_path):
        """Ensures README has the citation block."""
        repo_name = os.path.basename(repo_path)
        cite_text = self.generate_citation_apa(repo_name)
        readme_path = os.path.join(repo_path, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## 📜 How to Cite\n\n> {cite_text}\n")
            print(f"✅ Updated citation in {repo_name}/README.md")

    def run_full_sync(self, root_dir):
        """Iterates through all subdirectories (repos) and applies identity."""
        for item in os.listdir(root_dir):
            path = os.path.join(root_dir, item)
            if os.path.isdir(path) and not item.startswith('.'):
                self.update_readme(path)

def main():
    parser = argparse.ArgumentParser(description="Research Identity Automator 10.0")
    parser.add_argument("--sync", help="Path to the directory containing all research repos")
    args = parser.parse_args()

    automator = IdentityAutomator()
    if args.sync:
        automator.run_full_sync(args.sync)
    else:
        print("Identity Automator 10.0: Ready to process 1,273+ datasets.")
        print(f"Current Profile: {automator.profile['name']}")

if __name__ == "__main__":
    main()
