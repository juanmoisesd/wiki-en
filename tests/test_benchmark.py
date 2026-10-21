"""
Pruebas unitarias e integración para la suite Windows Optimization Benchmark.
"""

import os
import tempfile
import pytest
from windows_optimization_benchmark.metrics.boot_time import measure_boot_time
from windows_optimization_benchmark.metrics.cpu_ram import measure_idle_cpu_ram
from windows_optimization_benchmark.metrics.disk import measure_disk_activity
from windows_optimization_benchmark.metrics.startup_apps import get_startup_applications
from windows_optimization_benchmark.metrics.network import measure_ping_latency, measure_network_traffic
from windows_optimization_benchmark.engine.collector import BenchmarkCollector
from windows_optimization_benchmark.engine.stats import calculate_stats, summarize_benchmark_session
from windows_optimization_benchmark.engine.comparator import evaluate_metric_change, BenchmarkComparator
from windows_optimization_benchmark.reports.exporter import (
    export_to_json, load_from_json, export_summary_to_csv, export_comparison_to_csv
)
from windows_optimization_benchmark.reports.reporter import (
    generate_text_comparison_report, generate_html_report
)

def test_metrics_collectors():
    """Verifica que todos los colectores devuelvan estructuras estructuradas válidas."""
    boot = measure_boot_time(use_simulation_fallback=True)
    assert boot["measurable"] is True
    assert "boot_time_ms" in boot

    cpu_ram = measure_idle_cpu_ram(duration_seconds=1, warmup_seconds=0)
    assert len(cpu_ram["cpu_samples"]) >= 1
    assert len(cpu_ram["ram_percent_samples"]) >= 1

    disk = measure_disk_activity(duration_seconds=1, warmup_seconds=0)
    assert len(disk["iops_samples"]) >= 1

    startup = get_startup_applications()
    assert startup["count"] >= 0
    assert isinstance(startup["applications"], list)

    ping = measure_ping_latency(count=2)
    assert ping["pings_received"] >= 1

    net = measure_network_traffic(duration_seconds=1, warmup_seconds=0)
    assert len(net["rx_bytes_sec_samples"]) >= 1

def test_stats_calculations():
    """Verifica el cálculo de mediana, IQR y variabilidad."""
    series = [10.0, 20.0, 30.0, 40.0, 50.0]
    stats = calculate_stats(series)
    assert stats["median"] == 30.0
    assert stats["min"] == 10.0
    assert stats["max"] == 50.0
    assert stats["iqr"] > 0

    empty_stats = calculate_stats([])
    assert empty_stats["median"] == 0.0

def test_noise_threshold_rule():
    """Verifica que cambios menores o iguales al ruido no se declaren como mejoras."""
    before_stats = {"median": 10.0, "iqr": 2.0, "std_dev": 1.5}
    # Cambio de 10.0 a 9.5 (diferencia 0.5) cuando el ruido (IQR) es 2.0 -> NO SIGNIFICATIVO
    after_stats = {"median": 9.5, "iqr": 2.0, "std_dev": 1.5}

    eval_res = evaluate_metric_change(before_stats, after_stats, lower_is_better=True)
    assert eval_res["is_significant"] is False
    assert eval_res["status"] == "NO_SIGNIFICATIVE_CHANGE"
    assert eval_res["is_improvement"] is False

    # Cambio de 10.0 a 5.0 (diferencia -5.0) supera el ruido 2.0 -> MEJORA
    after_better = {"median": 5.0, "iqr": 2.0, "std_dev": 1.5}
    eval_better = evaluate_metric_change(before_stats, after_better, lower_is_better=True)
    assert eval_better["is_significant"] is True
    assert eval_better["status"] == "IMPROVEMENT"
    assert eval_better["is_improvement"] is True

def test_benchmark_collector_and_comparison(tmp_path):
    """Prueba de integración: Muestra -> Resumen -> Comparación -> Exportación."""
    collector1 = BenchmarkCollector(profile_name="P1", repetitions=2, sample_duration_sec=1, warmup_sec=0)
    raw1 = collector1.run_benchmark()
    sum1 = summarize_benchmark_session(raw1)

    collector2 = BenchmarkCollector(profile_name="P2", repetitions=2, sample_duration_sec=1, warmup_sec=0)
    raw2 = collector2.run_benchmark()
    sum2 = summarize_benchmark_session(raw2)

    comparator = BenchmarkComparator(sum1, sum2)
    comp = comparator.compare()

    assert "global_summary" in comp
    assert "metrics_comparison" in comp
    assert "causal_analysis" in comp

    # Exportación
    json_path = tmp_path / "comp.json"
    csv_path = tmp_path / "comp.csv"
    html_path = tmp_path / "comp.html"

    export_to_json(comp, str(json_path))
    assert os.path.exists(json_path)

    loaded = load_from_json(str(json_path))
    assert loaded["before_profile"] == "P1"

    export_comparison_to_csv(comp, str(csv_path))
    assert os.path.exists(csv_path)

    generate_html_report(comp, str(html_path))
    assert os.path.exists(html_path)

    txt_rep = generate_text_comparison_report(comp)
    assert "WINDOWS OPTIMIZATION BENCHMARK" in txt_rep
