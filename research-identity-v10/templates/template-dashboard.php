<?php
/**
 * Template Name: Impact Dashboard
 */
get_header();
?>

<div class="container animate" style="margin-top: 4rem;">
  <header style="text-align: center; margin-bottom: 4rem;">
    <h1 data-en="Research Impact Dashboard" data-es="Panel de Impacto de Investigación">Research Impact Dashboard</h1>
    <p class="subtitle" data-en="Visualizing Global Reach & Dataset Distribution" data-es="Visualizando el Alcance Global y la Distribución de Datasets">Visualizing Global Reach & Dataset Distribution</p>
  </header>

  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem;">
    <div class="expertise-card" style="height: 500px; display: flex; flex-direction: column;">
      <h3 data-en="Geographic Interest" data-es="Interés Geográfico">Geographic Interest</h3>
      <div id="map" style="flex-grow: 1; border-radius: 12px; margin-top: 1rem;"></div>
    </div>
    <div class="expertise-card" style="height: 500px; display: flex; flex-direction: column;">
      <h3 data-en="Dataset Categories" data-es="Categorías de Datasets">Dataset Categories</h3>
      <canvas id="impactChart" style="margin-top: 1rem;"></canvas>
    </div>
  </div>
</div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
document.addEventListener('DOMContentLoaded', () => {
    // Map
    const map = L.map('map').setView([20, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    const locations = [
        { lat: 40.4168, lon: -3.7038, city: "Madrid (UNIR HQ)" },
        { lat: 19.4326, lon: -99.1332, city: "Mexico City" },
        { lat: -34.6037, lon: -58.3816, city: "Buenos Aires" },
        { lat: 4.7110, lon: -74.0721, city: "Bogotá" }
    ];

    locations.forEach(loc => {
        L.circle([loc.lat, loc.lon], {
            color: 'var(--primary)',
            fillColor: 'var(--primary)',
            fillOpacity: 0.5,
            radius: 500000
        }).addTo(map).bindPopup(loc.city);
    });

    // Chart
    const ctx = document.getElementById('impactChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Neuroeconomics', 'AI & Ethics', 'Demographics', 'Forensic Science'],
            datasets: [{
                data: [42, 35, 23, 15],
                backgroundColor: ['#0366d6', '#2ea44f', '#f9826c', '#6f42c1'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: getComputedStyle(document.body).getPropertyValue('--text') } }
            }
        }
    });
});
</script>

<?php get_footer(); ?>
