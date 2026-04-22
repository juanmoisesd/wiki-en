<?php
/**
 * Template Name: Scientific Glossary
 */
get_header();
?>

<div class="container animate" style="margin-top: 4rem;">
  <header style="text-align: center; margin-bottom: 4rem;">
    <h1 data-en="Scientific Glossary" data-es="Glosario Científico">Scientific Glossary</h1>
    <p class="subtitle" data-en="Standardized Terminology for Neuroeconomics & Open Science" data-es="Terminología Estandarizada para Neuroeconomía y Ciencia Abierta">Standardized Terminology for Neuroeconomics & Open Science</p>
  </header>

  <div class="search-box">
    <input type="text" id="glossarySearch" placeholder="Search 1,968 terms..." data-en-placeholder="Search 1,968 terms..." data-es-placeholder="Buscar 1.968 términos...">
  </div>

  <div id="glossaryContainer" class="expertise-grid"></div>

  <div id="pagination" class="pagination" style="margin-top: 4rem; display: flex; justify-content: center; gap: 1rem;"></div>
</div>

<script>
const GLOSSARY_URL = "<?php echo get_template_directory_uri(); ?>/assets/data/glossary.json";
let glossaryData = [];
let currentPage = 1;
const itemsPerPage = 20;

async function loadGlossary() {
  const resp = await fetch(GLOSSARY_URL);
  glossaryData = await resp.json();
  renderGlossary();
}

function renderGlossary() {
  const query = document.getElementById('glossarySearch').value.toLowerCase();
  const filtered = glossaryData.filter(item =>
    item.term.toLowerCase().includes(query) ||
    item.definition.toLowerCase().includes(query)
  );

  const start = (currentPage - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const paginated = filtered.slice(start, end);

  const container = document.getElementById('glossaryContainer');
  container.innerHTML = paginated.map(item => `
    <div class="expertise-card">
      <h3 style="margin-top:0">${item.term}</h3>
      <p style="font-size: 0.95rem; line-height: 1.6;">${item.definition}</p>
    </div>
  `).join('');

  renderPagination(filtered.length);
}

function renderPagination(totalItems) {
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const nav = document.getElementById('pagination');
  nav.innerHTML = '';

  if (totalPages <= 1) return;

  for (let i = 1; i <= Math.min(totalPages, 10); i++) {
    const btn = document.createElement('button');
    btn.innerText = i;
    btn.className = `btn ${i === currentPage ? 'btn-primary' : ''}`;
    btn.style.padding = '0.5rem 1rem';
    btn.onclick = () => { currentPage = i; renderGlossary(); window.scrollTo(0, 400); };
    nav.appendChild(btn);
  }
}

document.getElementById('glossarySearch').addEventListener('input', () => {
  currentPage = 1;
  renderGlossary();
});

loadGlossary();
</script>

<?php get_footer(); ?>
