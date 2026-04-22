function toggleTheme() {
  const body = document.body;
  const currentTheme = body.getAttribute('data-theme');
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  body.setAttribute('data-theme', newTheme);
  localStorage.setItem('research-theme', newTheme);
}

let currentLang = localStorage.getItem('research-lang') || 'en';
function toggleLanguage() {
  currentLang = currentLang === 'en' ? 'es' : 'en';
  document.querySelectorAll('[data-en]').forEach(el => {
    el.innerText = el.getAttribute(`data-${currentLang}`);
  });
  localStorage.setItem('research-lang', currentLang);
}

document.addEventListener('DOMContentLoaded', () => {
  const savedTheme = localStorage.getItem('research-theme') || 'light';
  document.body.setAttribute('data-theme', savedTheme);
  if(currentLang === 'es') {
     document.querySelectorAll('[data-en]').forEach(el => el.innerText = el.getAttribute(`data-es`));
  }
});

function copyCite(id) {
  const text = document.getElementById(id).innerText;
  navigator.clipboard.writeText(text).then(() => {
    const btn = event.target;
    const originalText = btn.innerText;
    btn.innerText = '✓ Copied';
    setTimeout(() => btn.innerText = originalText, 2000);
  });
}
