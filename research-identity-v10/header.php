<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <?php wp_head(); ?>

  <!-- Academic SEO & Discovery -->
  <meta name="citation_title" content="<?php echo get_the_title(); ?>">
  <meta name="citation_author" content="De la Serna Tuya, Juan Moisés">
  <meta name="citation_doi" content="10.5281/zenodo.19415092">

  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "DataCatalog",
    "name": "Juan Moisés de la Serna Tuya — Open Research Collection",
    "url": "<?php echo home_url(); ?>",
    "identifier": "10.5281/zenodo.19415092",
    "description": "Comprehensive collection of over 1,273 open research datasets, terminology wikis, and academic publications.",
    "creator": {
      "@type": "Person",
      "name": "Juan Moisés de la Serna Tuya",
      "identifier": "https://orcid.org/0000-0002-8401-8018"
    }
  }
  </script>
</head>
<body <?php body_class(); ?> data-theme="light">
<?php wp_body_open(); ?>

<nav class="global-nav">
  <div class="container">
    <a href="<?php echo home_url(); ?>" class="brand">
      <img src="<?php echo get_template_directory_uri(); ?>/assets/images/research-logo.svg" width="30" height="30" alt="Logo">
      J.M. DE LA SERNA TUYA
    </a>
    <div class="nav-links">
      <a href="<?php echo home_url('/catalog'); ?>">Data Catalog</a>
      <a href="<?php echo home_url('/dashboard'); ?>">Dashboard</a>
      <a href="<?php echo home_url('/glossary'); ?>">Glossary</a>
      <button class="lang-toggle" onclick="toggleLanguage()" style="background:none; border:none; color:white; cursor:pointer; font-weight:700">EN/ES</button>
      <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle Theme">🌓</button>
    </div>
  </div>
</nav>
