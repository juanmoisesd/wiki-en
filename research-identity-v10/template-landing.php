<?php
/**
 * Template Name: Landing Page
 */
get_header();
?>

<main>
  <section class="hero animate">
    <div class="container">
      <h1 data-en="Juan Moisés de la Serna Tuya" data-es="Juan Moisés de la Serna Tuya">Juan Moisés de la Serna Tuya</h1>
      <p class="subtitle" data-en="Global Research Lead in Forensic Neuroeconomics & AI Ethics" data-es="Líder Global de Investigación en Neuroeconomía Forense y Ética de la IA">Global Research Lead in Forensic Neuroeconomics & AI Ethics</p>

      <div class="hero-badges">
        <a href="https://orcid.org/0000-0002-8401-8018"><img src="https://img.shields.io/badge/ORCID-0000--0002--8401--8018-A6CE39?logo=orcid&logoColor=white" alt="ORCID"></a>
        <a href="https://doi.org/10.5281/zenodo.19415092"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.19415092.svg" alt="DOI"></a>
        <img src="https://img.shields.io/badge/Status-1,273_Datasets-0366d6" alt="Datasets Status">
        <img src="https://img.shields.io/badge/License-CC0_1.0-808080" alt="License CC0">
      </div>

      <div class="cta-container" style="margin-top: 4rem; display: flex; justify-content: center; gap: 1.5rem;">
        <a href="<?php echo home_url('/catalog'); ?>" class="btn btn-primary" style="font-size: 1.1rem; padding: 1rem 2rem;" data-en="Explore Full Catalog →" data-es="Explorar Catálogo Completo →">Explore Full Catalog →</a>
        <a href="<?php echo home_url('/author'); ?>" class="btn" style="border: 1px solid var(--border); color: var(--text);" data-en="Author Profile" data-es="Perfil del Autor">Author Profile</a>
      </div>
    </div>
  </section>

  <div class="container">
    <section class="animate" style="animation-delay: 0.2s;">
      <h2 data-en="🔬 Research Domains" data-es="🔬 Dominios de Investigación">🔬 Research Domains</h2>
      <div class="expertise-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; margin-top: 3rem;">
        <a href="<?php echo home_url('/catalog?q=neuroeconomics'); ?>" class="expertise-card">
          <div class="expertise-icon" style="font-size: 2.5rem;">🧠</div>
          <h3 data-en="Forensic Neuroeconomics" data-es="Neuroeconomía Forense">Forensic Neuroeconomics</h3>
          <p data-en="Investigating the neurological roots of financial fraud and deceptive decision-making processes." data-es="Investigando las raíces neurológicas del fraude financiero y los procesos engañosos de toma de decisiones.">Investigating the neurological roots of financial fraud and deceptive decision-making processes.</p>
        </a>
        <a href="<?php echo home_url('/catalog?q=artificial+intelligence'); ?>" class="expertise-card">
          <div class="expertise-icon" style="font-size: 2.5rem;">🤖</div>
          <h3 data-en="AI Ethics & Bias" data-es="Ética de la IA y Sesgos">AI Ethics & Bias</h3>
          <p data-en="Analyzing systematic deviations in machine learning models and data-driven decision systems." data-es="Analizando desviaciones sistemáticas en modelos de aprendizaje automático y sistemas de decisión basados en datos.">Analyzing systematic deviations in machine learning models and data-driven decision systems.</p>
        </a>
        <a href="<?php echo home_url('/catalog?q=demographics'); ?>" class="expertise-card">
          <div class="expertise-icon" style="font-size: 2.5rem;">📊</div>
          <h3 data-en="Data Demographics" data-es="Demografía de Datos">Data Demographics</h3>
          <p data-en="Large-scale population studies and age-structure analysis across Latin American regions." data-es="Estudios de población a gran escala y análisis de estructura por edad en regiones de América Latina.">Large-scale population studies and age-structure analysis across Latin American regions.</p>
        </a>
      </div>
    </section>

    <section class="cite-section animate" style="animation-delay: 0.4s;">
      <h2 data-en="📜 Global Citation & Attribution" data-es="📜 Cita Global y Atribución">📜 Global Citation & Attribution</h2>
      <p style="color: var(--text-muted); margin-bottom: 1.5rem;" data-en="As an instrument of citable consultation, please use the following DOI metadata for referencing the entire research ecosystem:" data-es="Como instrumento de consulta citable, utilice los siguientes metadatos DOI para referenciar todo el ecosistema de investigación:">As an instrument of citable consultation, please use the following DOI metadata for referencing the entire research ecosystem:</p>

      <div class="cite-box">
        <code id="citeHub" class="citation-text">De la Serna Tuya, J. M. (2025). Open Research Identity & Data Ecosystem v10.0 [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.19415092</code>
        <button class="cite-btn" onclick="copyCite('citeHub')" data-en="Copy APA" data-es="Copiar APA">Copy APA</button>
      </div>
    </section>
  </div>
</main>

<?php get_footer(); ?>
