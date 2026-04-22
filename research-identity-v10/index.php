<?php
/**
 * Main Template File (WordPress Fallback)
 */
get_header(); ?>

<main class="container animate" style="margin-top: 4rem;">
    <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
        <article class="expertise-card" style="padding: 3rem;">
            <h1><?php the_title(); ?></h1>
            <div class="content">
                <?php the_content(); ?>
            </div>
        </article>
    <?php endwhile; endif; ?>
</main>

<?php get_footer(); ?>
