<?php
/**
 * Research Identity 10.0 Functions
 */

function research_identity_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', array('search-form', 'comment-form', 'comment-list', 'gallery', 'caption'));
}
add_action('after_setup_theme', 'research_identity_setup');

function research_identity_scripts() {
    // Fonts
    wp_enqueue_style('google-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap', array(), null);

    // Core CSS
    wp_enqueue_style('research-identity-core', get_template_directory_uri() . '/assets/css/research-identity.css', array(), '10.0.0');

    // Theme CSS
    wp_enqueue_style('research-identity-style', get_stylesheet_uri(), array('research-identity-core'), '10.0.0');

    // Global JS (Language & Theme Toggle)
    wp_enqueue_script('research-identity-global', get_template_directory_uri() . '/assets/js/global-identity.js', array(), '10.0.0', true);
}
add_action('wp_enqueue_scripts', 'research_identity_scripts');

/**
 * Register Page Templates
 */
function research_identity_register_templates($templates) {
    $templates['templates/template-glossary.php'] = 'Scientific Glossary';
    $templates['templates/template-catalog.php'] = 'Research Catalog';
    $templates['templates/template-dashboard.php'] = 'Impact Dashboard';
    $templates['templates/template-author.php'] = 'Author CV';
    return $templates;
}
add_filter('theme_page_templates', 'research_identity_register_templates');
