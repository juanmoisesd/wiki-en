"""
Módulo para exportación e importación de datos de Benchmark en formatos JSON y CSV.
"""

import json
import csv
import os
from typing import Dict, Any, List

def export_to_json(data: Dict[str, Any], filepath: str) -> str:
    """
    Guarda una sesión o reporte de comparación de benchmark en formato JSON estructurado.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath

def load_from_json(filepath: str) -> Dict[str, Any]:
    """
    Carga un archivo JSON de sesión o reporte de benchmark.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def export_summary_to_csv(summary_data: Dict[str, Any], filepath: str) -> str:
    """
    Exporta el resumen estadístico de una sesión de benchmark a un archivo CSV.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    metrics = summary_data.get("metrics_summary", {})

    headers = [
        "Metrica_Clave", "Nombre_Metrica", "Mediana", "Media",
        "Desviabilidad_Std", "Rango_Intercuartil_IQR", "Minimo", "Maximo",
        "Variabilidad_Relativa_Pct", "Muestras_N"
    ]

    metric_names = {
        "cpu_usage_pct": "Uso de CPU en Reposo (%)",
        "ram_usage_pct": "Uso de RAM en Reposo (%)",
        "ram_used_mb": "Memoria RAM Usada (MB)",
        "disk_read_bytes_sec": "Lecturas de Disco (Bytes/s)",
        "disk_write_bytes_sec": "Escrituras de Disco (Bytes/s)",
        "disk_iops": "E/S Disco (IOPS)",
        "disk_time_pct": "Tiempo Activo Disco (%)",
        "net_rx_bytes_sec": "Red Recibida (Bytes/s)",
        "net_tx_bytes_sec": "Red Enviada (Bytes/s)",
        "ping_latency_ms": "Latencia Ping (ms)"
    }

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for key, stats in metrics.items():
            name = metric_names.get(key, key)
            writer.writerow([
                key,
                name,
                stats.get("median", 0.0),
                stats.get("mean", 0.0),
                stats.get("std_dev", 0.0),
                stats.get("iqr", 0.0),
                stats.get("min", 0.0),
                stats.get("max", 0.0),
                stats.get("rel_variability_pct", 0.0),
                stats.get("sample_size", 0)
            ])

    return filepath

def export_comparison_to_csv(comparison_data: Dict[str, Any], filepath: str) -> str:
    """
    Exporta una comparación "Antes vs Después" a un archivo CSV plano.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    metrics_comp = comparison_data.get("metrics_comparison", {})

    headers = [
        "Clave_Metrica", "Nombre_Metrica", "Mediana_Antes", "Mediana_Despues",
        "Diferencia_Absoluta", "Cambio_Porcentual", "Umbral_Ruido",
        "Es_Significativo", "Estado", "Veredicto"
    ]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for key, comp in metrics_comp.items():
            writer.writerow([
                key,
                comp.get("name_es", key),
                comp.get("median_before", 0.0),
                comp.get("median_after", 0.0),
                comp.get("absolute_difference", 0.0),
                comp.get("percent_change", 0.0),
                comp.get("noise_threshold", 0.0),
                "SI" if comp.get("is_significant") else "NO",
                comp.get("status", ""),
                comp.get("verdict_es", "")
            ])

    return filepath
