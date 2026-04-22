<?php
/**
 * Template Name: Research Catalog
 */
get_header();
?>

<div class="container animate" style="margin-top: 4rem;">
  <header style="text-align: center; margin-bottom: 4rem;">
    <h1 data-en="Open Research Catalog" data-es="Catálogo de Investigación Abierta">Open Research Catalog</h1>
    <p class="subtitle" data-en="Live Discovery Hub for 1,273+ Forensic & Demographic Datasets" data-es="Centro de Descubrimiento para 1,273+ Datasets Forenses y Demográficos">Live Discovery Hub for 1,273+ Forensic & Demographic Datasets</p>
    <div id="catalogStats" style="font-weight: 600; color: var(--primary); margin-top: 1rem;">Indexing repositories...</div>
  </header>

  <div class="search-box">
    <input type="text" id="catalogSearch" placeholder="Filter repositories..." data-es-placeholder="Filtrar repositorios...">
  </div>

  <div id="catalogGrid" class="expertise-grid"></div>
</div>

<script>
let repos = [];
async function fetchRepos() {
    const stats = document.getElementById('catalogStats');
    try {
        const response = await fetch('https://api.github.com/users/juanmoisesd/repos?per_page=100&sort=updated');
        repos = await response.json();
        stats.innerText = `Displaying ${repos.length} of 1,273+ datasets.`;
        renderCatalog();
    } catch (e) {
        stats.innerText = "Error loading live data. Please try again later.";
    }
}

function renderCatalog() {
    const query = document.getElementById('catalogSearch').value.toLowerCase();
    const filtered = repos.filter(r =>
        (r.name && r.name.toLowerCase().includes(query)) ||
        (r.description && r.description.toLowerCase().includes(query))
    );

    document.getElementById('catalogGrid').innerHTML = filtered.map(r => `
        <div class="expertise-card">
            <h3 style="margin-top:0">${r.name.replace(/-/g, ' ')}</h3>
            <p style="font-size: 0.9rem; margin-bottom: 1.5rem;">${r.description || 'No description available.'}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto;">
                <span class="badge" style="background: var(--primary-glow); color: var(--primary); padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.8rem; font-weight: 700;">${r.language || 'Data'}</span>
                <a href="${r.html_url}" class="btn" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;" target="_blank">View Source</a>
            </div>
        </div>
    `).join('');
}

document.getElementById('catalogSearch').addEventListener('input', renderCatalog);
fetchRepos();
</script>

<?php get_footer(); ?>
