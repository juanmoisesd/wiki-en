"""
Módulo para generación de informes en texto y HTML interactivo en Español.
Alineado con el estándar 'Research Identity 10.0' del repositorio.
"""

import json
import os
import time
from typing import Dict, Any

def generate_text_comparison_report(comparison: Dict[str, Any]) -> str:
    """
    Genera un informe descriptivo en formato texto/Markdown en español.
    """
    lines = []
    lines.append("==========================================================================")
    lines.append("    WINDOWS OPTIMIZATION BENCHMARK — INFORME DE COMPARACIÓN Y ANÁLISIS")
    lines.append("==========================================================================")
    lines.append(f"Perfil Inicial (Antes):    {comparison.get('before_profile', 'Antes')}")
    lines.append(f"Perfil Optimizado (Después): {comparison.get('after_profile', 'Después')}")
    global_sum = comparison.get("global_summary", {})
    lines.append(f"Veredicto Global:            {global_sum.get('global_verdict_es', 'N/A')}")
    lines.append(f"Mejoras confirmadas:         {global_sum.get('improvements_count', 0)}")
    lines.append(f"Degradaciones detectadas:    {global_sum.get('regressions_count', 0)}")
    lines.append(f"Sin cambio significativo:    {global_sum.get('no_change_count', 0)}")
    lines.append("--------------------------------------------------------------------------")

    # Aplicaciones de inicio
    st_apps = comparison.get("startup_apps_change", {})
    lines.append("\n[APLICACIONES Y TAREAS AL INICIO]")
    lines.append(f"  • Antes:   {st_apps.get('before_count', 0)} elementos")
    lines.append(f"  • Después: {st_apps.get('after_count', 0)} elementos")
    lines.append(f"  • Cambio:  {st_apps.get('difference', 0)} elementos")

    # Tiempo de arranque si aplica
    boot_comp = comparison.get("boot_time_comparison")
    if boot_comp:
        lines.append("\n[TIEMPO DE ARRANQUE DEL SISTEMA]")
        lines.append(f"  • Mediana Antes:   {boot_comp.get('median_before')} ms")
        lines.append(f"  • Mediana Después: {boot_comp.get('median_after')} ms")
        lines.append(f"  • Diferencia:      {boot_comp.get('absolute_difference')} ms ({boot_comp.get('percent_change')}%)")
        lines.append(f"  • Veredicto:       {boot_comp.get('verdict_es')}")

    # Tabla de métricas
    lines.append("\n[DESGLOSE DE MÉTRICAS EN REPOSO]")
    lines.append(f"{'Métrica':<38} | {'Antes':<8} | {'Después':<8} | {'Cambio %':<9} | {'Veredicto'}")
    lines.append("-" * 88)

    metrics_comp = comparison.get("metrics_comparison", {})
    for key, c in metrics_comp.items():
        name = c.get("name_es", key)[:36]
        m_b = str(c.get("median_before", 0.0))
        m_a = str(c.get("median_after", 0.0))
        pct = f"{c.get('percent_change', 0.0):+.1f}%"
        verdict = c.get("verdict_es", "")
        lines.append(f"{name:<38} | {m_b:<8} | {m_a:<8} | {pct:<9} | {verdict}")

    # Nota Metodológica de Causalidad
    causal = comparison.get("causal_analysis", {})
    lines.append("\n" + "=" * 88)
    lines.append(" [ANÁLISIS METODOLÓGICO: CORRELACIÓN VS CAUSALIDAD]")
    lines.append(causal.get("correlation_vs_causality_note", ""))
    lines.append("\n Factores de confusión considerados:")
    for factor in causal.get("confounding_factors_checked", []):
        lines.append(f"  - {factor}")
    lines.append(f"\n Recomendación: {causal.get('methodological_recommendation', '')}")
    lines.append("=" * 88)

    return "\n".join(lines)


def generate_html_report(comparison: Dict[str, Any], filepath: str) -> str:
    """
    Genera un visor interactivo HTML standalone con diseño Research Identity 10.0 en español.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    comp_json_str = json.dumps(comparison, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Windows Optimization Benchmark — Visor Comparativo</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0b0f19;
      --card-bg: rgba(20, 27, 45, 0.75);
      --border: rgba(255, 255, 255, 0.12);
      --primary: #38bdf8;
      --primary-glow: rgba(56, 189, 248, 0.25);
      --accent-green: #34d399;
      --accent-red: #f87171;
      --accent-yellow: #fbbf24;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }}

    body {{
      background-color: var(--bg);
      color: var(--text);
      font-family: var(--font-sans);
      margin: 0;
      padding: 2rem;
      line-height: 1.6;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
    }}

    header {{
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.5rem;
      margin-bottom: 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
    }}

    h1 {{
      font-size: 1.8rem;
      margin: 0;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .badge {{
      background: var(--primary-glow);
      color: var(--primary);
      border: 1px solid var(--primary);
      padding: 0.2rem 0.6rem;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-family: var(--font-mono);
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }}

    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      backdrop-filter: blur(12px);
    }}

    .card h3 {{
      margin-top: 0;
      font-size: 1.1rem;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.5rem;
    }}

    .metric-value {{
      font-size: 1.8rem;
      font-weight: 700;
      font-family: var(--font-mono);
      margin: 0.5rem 0;
    }}

    .verdict-box {{
      padding: 1rem;
      border-radius: 8px;
      font-weight: 600;
      margin-top: 1rem;
      text-align: center;
    }}

    .verdict-IMPROVEMENT {{ background: rgba(52, 211, 153, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }}
    .verdict-REGRESSION {{ background: rgba(248, 113, 113, 0.15); color: var(--accent-red); border: 1px solid var(--accent-red); }}
    .verdict-NO_SIGNIFICATIVE_CHANGE {{ background: rgba(251, 191, 36, 0.15); color: var(--accent-yellow); border: 1px solid var(--accent-yellow); }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 1rem;
      font-size: 0.95rem;
    }}

    th, td {{
      padding: 0.85rem 1rem;
      text-align: left;
      border-bottom: 1px solid var(--border);
    }}

    th {{
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-muted);
      font-weight: 600;
    }}

    td.mono {{
      font-family: var(--font-mono);
    }}

    .causal-section {{
      background: rgba(56, 189, 248, 0.05);
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 12px;
      padding: 1.5rem;
      margin-top: 2rem;
    }}

    .causal-section h3 {{
      color: var(--primary);
      margin-top: 0;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>🖥️ Windows Optimization Benchmark <span class="badge">Windows 10 x64</span></h1>
        <p style="color: var(--text-muted); margin: 0.25rem 0 0 0;">Evaluación Científica de Rendimiento en Reposo y Transiciones</p>
      </div>
      <div>
        <span class="badge">Investigación & Calibración</span>
      </div>
    </header>

    <div class="grid">
      <div class="card">
        <h3>Perfil Inicial ("Antes")</h3>
        <div class="metric-value" id="profBefore">-</div>
      </div>
      <div class="card">
        <h3>Perfil Optimizado ("Después")</h3>
        <div class="metric-value" id="profAfter">-</div>
      </div>
      <div class="card">
        <h3>Veredicto Estadístico Global</h3>
        <div class="verdict-box" id="globalVerdict">-</div>
      </div>
    </div>

    <div class="card">
      <h3>Tabla Comparativa de Métricas (Medianas)</h3>
      <table>
        <thead>
          <tr>
            <th>Métrica de Rendimiento</th>
            <th>Antes (Mediana)</th>
            <th>Después (Mediana)</th>
            <th>Diferencia (%)</th>
            <th>Evaluación Estadísticas</th>
          </tr>
        </thead>
        <tbody id="metricsTableBody">
        </tbody>
      </table>
    </div>

    <div class="causal-section">
      <h3>🔬 Distinción de Correlación vs Causalidad</h3>
      <p id="causalNote"></p>
      <h4>Factores de Confusión Monitoreados:</h4>
      <ul id="confoundingList"></ul>
      <p><strong>Recomendación Metodológica:</strong> <span id="methodRec"></span></p>
    </div>
  </div>

  <script>
    const data = {comp_json_str};

    document.getElementById('profBefore').innerText = data.before_profile || 'Antes';
    document.getElementById('profAfter').innerText = data.after_profile || 'Después';

    const gSum = data.global_summary || {{}};
    const gElem = document.getElementById('globalVerdict');
    gElem.innerText = gSum.global_verdict_es || 'Sin evaluación';
    gElem.className = 'verdict-box verdict-' + (gSum.global_verdict || 'NO_SIGNIFICATIVE_CHANGE');

    const tbody = document.getElementById('metricsTableBody');
    const metrics = data.metrics_comparison || {{}};

    for (const [key, item] of Object.entries(metrics)) {{
      const tr = document.createElement('tr');
      const pctStr = (item.percent_change >= 0 ? '+' : '') + item.percent_change.toFixed(2) + '%';

      let badgeClass = 'verdict-NO_SIGNIFICATIVE_CHANGE';
      if (item.status === 'IMPROVEMENT') badgeClass = 'verdict-IMPROVEMENT';
      if (item.status === 'REGRESSION') badgeClass = 'verdict-REGRESSION';

      tr.innerHTML = `
        <td><strong>${{item.name_es || key}}</strong></td>
        <td class="mono">${{item.median_before}}</td>
        <td class="mono">${{item.median_after}}</td>
        <td class="mono" style="color: ${{item.percent_change < 0 ? 'var(--accent-green)' : 'var(--accent-red)'}}">${{pctStr}}</td>
        <td><span class="badge ${{badgeClass}}">${{item.verdict_es}}</span></td>
      `;
      tbody.appendChild(tr);
    }}

    const cData = data.causal_analysis || {{}};
    document.getElementById('causalNote').innerText = cData.correlation_vs_causality_note || '';
    document.getElementById('methodRec').innerText = cData.methodological_recommendation || '';

    const confList = document.getElementById('confoundingList');
    (cData.confounding_factors_checked || []).forEach(factor => {{
      const li = document.createElement('li');
      li.innerText = factor;
      confList.appendChild(li);
    }});
  </script>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    return filepath
