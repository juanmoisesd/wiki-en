"""
Motor de Cálculo Estadístico.
Calcula Mediana, Variabilidad (IQR, Desviación Estándar, Rango Min-Max)
y consolida métricas multiejecución.
"""

import math
from typing import List, Dict, Any

def calculate_stats(series: List[float]) -> Dict[str, float]:
    """
    Calcula resumen estadístico robusto de una serie numérica:
    - Mediana (Medida de tendencia central robusta ante valores atípicos)
    - Media (Mean)
    - Desviación Estándar (StdDev)
    - Rango Intercuartílico (IQR: Q3 - Q1)
    - Mínimo (Min)
    - Máximo (Max)
    - Variabilidad relativa (%)
    """
    if not series:
        return {
            "median": 0.0, "mean": 0.0, "std_dev": 0.0,
            "iqr": 0.0, "min": 0.0, "max": 0.0,
            "q1": 0.0, "q3": 0.0, "rel_variability_pct": 0.0,
            "sample_size": 0
        }

    s_sorted = sorted(series)
    n = len(s_sorted)

    # Mediana
    if n % 2 == 1:
        median = s_sorted[n // 2]
    else:
        median = (s_sorted[n // 2 - 1] + s_sorted[n // 2]) / 2.0

    # Media y Desviación Estándar
    mean = sum(s_sorted) / float(n)
    variance = sum((x - mean) ** 2 for x in s_sorted) / float(n) if n > 1 else 0.0
    std_dev = math.sqrt(variance)

    # Cuartiles Q1 y Q3
    def _percentile(data: List[float], p: float) -> float:
        idx = p * (len(data) - 1)
        i = int(idx)
        f = idx - i
        if i + 1 < len(data):
            return data[i] + f * (data[i + 1] - data[i])
        return data[i]

    q1 = _percentile(s_sorted, 0.25)
    q3 = _percentile(s_sorted, 0.75)
    iqr = q3 - q1

    val_min = s_sorted[0]
    val_max = s_sorted[-1]

    # Variabilidad relativa (Coeficiente de variación o IQR/mediana)
    rel_var = (iqr / median * 100.0) if median != 0 else (std_dev / mean * 100.0 if mean != 0 else 0.0)

    return {
        "median": round(median, 3),
        "mean": round(mean, 3),
        "std_dev": round(std_dev, 3),
        "iqr": round(iqr, 3),
        "min": round(val_min, 3),
        "max": round(val_max, 3),
        "q1": round(q1, 3),
        "q3": round(q3, 3),
        "rel_variability_pct": round(abs(rel_var), 2),
        "sample_size": n
    }

def summarize_benchmark_session(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Consolida las muestras de todas las repeticiones de una sesión
    y extrae el resumen estadístico por categoría de métrica.
    """
    cpu_flat: List[float] = []
    ram_pct_flat: List[float] = []
    ram_mb_flat: List[float] = []

    disk_read_flat: List[float] = []
    disk_write_flat: List[float] = []
    disk_iops_flat: List[float] = []
    disk_time_flat: List[float] = []

    net_rx_flat: List[float] = []
    net_tx_flat: List[float] = []
    ping_lat_flat: List[float] = []

    runs = session_data.get("runs", [])
    for run in runs:
        # CPU / RAM
        cpu_ram = run.get("cpu_ram", {})
        cpu_flat.extend(cpu_ram.get("cpu_samples", []))
        ram_pct_flat.extend(cpu_ram.get("ram_percent_samples", []))
        ram_mb_flat.extend(cpu_ram.get("ram_used_mb_samples", []))

        # Disco
        disk = run.get("disk", {})
        disk_read_flat.extend(disk.get("read_bytes_sec_samples", []))
        disk_write_flat.extend(disk.get("write_bytes_sec_samples", []))
        disk_iops_flat.extend(disk.get("iops_samples", []))
        disk_time_flat.extend(disk.get("disk_time_percent_samples", []))

        # Red
        net = run.get("network_traffic", {})
        net_rx_flat.extend(net.get("rx_bytes_sec_samples", []))
        net_tx_flat.extend(net.get("tx_bytes_sec_samples", []))

        ping = run.get("ping_latency", {})
        ping_lat_flat.extend(ping.get("latencies_ms", []))

    summary = {
        "profile_name": session_data.get("profile_name", "Desconocido"),
        "session_id": session_data.get("session_id", ""),
        "timestamp": session_data.get("start_timestamp", 0),
        "system_info": session_data.get("system_info", {}),
        "startup_apps_count": session_data.get("startup_apps", {}).get("count", 0),
        "boot_info": session_data.get("boot_info", {}),
        "metrics_summary": {
            "cpu_usage_pct": calculate_stats(cpu_flat),
            "ram_usage_pct": calculate_stats(ram_pct_flat),
            "ram_used_mb": calculate_stats(ram_mb_flat),
            "disk_read_bytes_sec": calculate_stats(disk_read_flat),
            "disk_write_bytes_sec": calculate_stats(disk_write_flat),
            "disk_iops": calculate_stats(disk_iops_flat),
            "disk_time_pct": calculate_stats(disk_time_flat),
            "net_rx_bytes_sec": calculate_stats(net_rx_flat),
            "net_tx_bytes_sec": calculate_stats(net_tx_flat),
            "ping_latency_ms": calculate_stats(ping_lat_flat)
        },
        "raw_series": {
            "cpu_usage_pct": cpu_flat,
            "ram_usage_pct": ram_pct_flat,
            "ram_used_mb": ram_mb_flat,
            "disk_read_bytes_sec": disk_read_flat,
            "disk_write_bytes_sec": disk_write_flat,
            "disk_iops": disk_iops_flat,
            "disk_time_pct": disk_time_flat,
            "net_rx_bytes_sec": net_rx_flat,
            "net_tx_bytes_sec": net_tx_flat,
            "ping_latency_ms": ping_lat_flat
        }
    }

    return summary
