<?php
/**
 * Template Name: Author Profile
 */
get_header();
?>

<div class="container animate" style="margin-top: 4rem; max-width: 900px;">
  <div class="expertise-card" style="display: flex; align-items: center; gap: 3rem; margin-bottom: 4rem; padding: 3rem;">
    <div style="width: 150px; height: 150px; border-radius: 50%; background: var(--primary-glow); display: flex; align-items: center; justify-content: center; font-size: 3rem;">🧠</div>
    <div>
      <h1 style="margin:0">Juan Moisés de la Serna Tuya</h1>
      <p style="font-size: 1.2rem; color: var(--primary); font-weight: 600;">PhD in Psychology | Forensic Neuroeconomist</p>
      <div style="display: flex; gap: 1rem; margin-top: 1rem;">
         <a href="https://orcid.org/0000-0002-8401-8018" target="_blank" class="badge">ORCID</a>
         <a href="https://www.linkedin.com/in/juanmoisesdelaserna/" target="_blank" class="badge">LinkedIn</a>
      </div>
    </div>
  </div>

  <section class="animate" style="animation-delay: 0.2s;">
    <h2 data-en="Academic Trajectory" data-es="Trayectoria Académica">Academic Trajectory</h2>
    <div style="border-left: 2px solid var(--primary); padding-left: 2rem; margin-left: 1rem;">
       <div style="margin-bottom: 2rem; position: relative;">
          <div style="position: absolute; left: -2.4rem; top: 0.5rem; width: 12px; height: 12px; background: var(--primary); border-radius: 50%;"></div>
          <h4 style="margin:0">UNIR - Universidad Internacional de La Rioja</h4>
          <p style="margin: 0.2rem 0; font-weight: 600;">Professor & Researcher</p>
          <p style="font-size: 0.9rem; color: var(--text-muted);">Specializing in Neuropsychology and Economic Behavior.</p>
       </div>
       <div style="margin-bottom: 2rem; position: relative;">
          <div style="position: absolute; left: -2.4rem; top: 0.5rem; width: 12px; height: 12px; background: var(--primary); border-radius: 50%;"></div>
          <h4 style="margin:0">Open Research Movement</h4>
          <p style="margin: 0.2rem 0; font-weight: 600;">Principal Investigator</p>
          <p style="font-size: 0.9rem; color: var(--text-muted);">Managing 1,273+ public datasets for forensic transparency.</p>
       </div>
    </div>
  </section>
</div>

<?php get_footer(); ?>
