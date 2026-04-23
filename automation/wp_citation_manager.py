import requests
import hashlib
import re
import time
import base64
from requests.auth import HTTPBasicAuth

class WPCitationManager:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def solve_pow(self):
        print("Attempting to bypass Proof-of-Work...")
        response = self.session.get(f"{self.base_url}/wp-login.php", headers=self.headers)
        if "____proof-of-work" not in response.text:
            print("No PoW detected or already bypassed.")
            return True

        # Extract c0
        match = re.search(r'let c0="([a-f0-9]+)"', response.text)
        if not match:
            print("Could not find PoW challenge (c0).")
            return False

        c0 = match.group(1)
        print(f"Solving PoW for c0: {c0}")

        k = 0
        while True:
            hash_result = hashlib.sha256((c0 + str(k)).encode()).hexdigest()
            if hash_result.startswith("0000"):
                break
            k += 1

        print(f"Solved! K = {k}")
        # The URL to validate is /____proof-of-work/validate/{K}/{base64_target}
        target_url_b64 = base64.b64encode(f"{self.base_url}/wp-login.php".encode()).decode()
        validate_url = f"{self.base_url}/____proof-of-work/validate/{k}/{target_url_b64}"

        val_res = self.session.get(validate_url, headers=self.headers)
        if val_res.status_code == 200 or "wordpress_logged_in" in self.session.cookies.get_dict():
             print("PoW validation successful.")
             return True
        else:
            print(f"PoW validation failed. Status: {val_res.status_code}")
            return False

    def test_auth(self):
        # First try REST API Basic Auth
        api_url = f"{self.base_url}/wp-json/wp/v2/users/me"
        response = self.session.get(api_url, auth=HTTPBasicAuth(self.username, self.password), headers=self.headers)
        if response.status_code == 200:
            print("Authentication successful via REST API Basic Auth.")
            return "basic"

        print(f"REST API Basic Auth failed ({response.status_code}). Trying Form Login...")

        # Try form login
        login_url = f"{self.base_url}/wp-login.php"
        data = {
            'log': self.username,
            'pwd': self.password,
            'wp-submit': 'Log In',
            'redirect_to': f"{self.base_url}/wp-admin/",
            'testcookie': 1
        }
        res = self.session.post(login_url, data=data, headers=self.headers)
        if any('wordpress_logged_in' in c.name for c in self.session.cookies):
            print("Authentication successful via Form Login.")
            # Get nonce for REST API
            admin_res = self.session.get(f"{self.base_url}/wp-admin/", headers=self.headers)
            nonce_match = re.search(r'var wpApiSettings = \{.*?\"nonce\":\"([a-f0-9]+)\"', admin_res.text)
            if nonce_match:
                self.nonce = nonce_match.group(1)
                self.headers['X-WP-Nonce'] = self.nonce
                print(f"Acquired REST API Nonce: {self.nonce}")
            return "session"

        print("Authentication failed.")
        return None

    def get_citation_block(self, title, url, slug):
        return f"""
<section class="citation-block" aria-labelledby="cita-heading">
  <h2 id="cita-heading">Cita este artículo</h2>

  <details>
    <summary>APA 7</summary>
    <pre><code>de la Serna, J. M. (2025). {title}. <em>juanmoisesdelaserna.es</em>. {url}</code></pre>
  </details>

  <details>
    <summary>Vancouver</summary>
    <pre><code>1. de la Serna JM. {title}. juanmoisesdelaserna.es. 2025;Disponible en: {url}</code></pre>
  </details>

  <details>
    <summary>BibTeX</summary>
    <pre><code>@article{{{slug}2025,
  author = {{de la Serna, Juan Moisés}},
  title = {{{title}}},
  year = {{2025}},
  url = {{{url}}},
  note = {{Accedido: 2025}}
}}</code></pre>
  </details>
</section>"""

    def process_items(self, endpoint, limit=None, start_page=1):
        page = start_page
        total_updated = 0
        while True:
            print(f"Fetching {endpoint} page {page}...", flush=True)
            res = self.session.get(f"{self.base_url}/wp-json/wp/v2/{endpoint}?page={page}&per_page=100&context=edit", headers=self.headers)
            if res.status_code == 400: # Page not found usually
                print(f"Reached end of {endpoint} at page {page}", flush=True)
                break
            if res.status_code != 200:
                print(f"Error fetching page {page}: {res.status_code}", flush=True)
                break

            items = res.json()
            if not items:
                break

            for item in items:
                content = item.get('content', {}).get('raw', '')
                if not content:
                    content = item.get('content', {}).get('rendered', '')

                if 'class="citation-block"' in content:
                    continue

                title = item['title']['rendered']
                url = item['link']
                slug = item['slug']

                citation = self.get_citation_block(title, url, slug)
                new_content = content + citation

                update_res = self.session.post(
                    f"{self.base_url}/wp-json/wp/v2/{endpoint}/{item['id']}",
                    json={'content': new_content},
                    headers=self.headers
                )

                if update_res.status_code == 200:
                    total_updated += 1
                    print(f"✅ Updated {endpoint} {item['id']}: {title}", flush=True)
                else:
                    print(f"❌ Failed to update {endpoint} {item['id']}: {update_res.status_code}", flush=True)

                if limit and total_updated >= limit:
                    return total_updated

            page += 1
        return total_updated
