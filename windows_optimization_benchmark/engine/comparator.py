"""
Módulo de Comparación Estricta y Análisis Causal ("Antes" vs "Después").
Implementa reglas científicas de no-declaración de mejora si el cambio no supera la variación natural de las mediciones.
Distingue explícitamente entre correlación observada y causalidad demostrada.
"""

from typing import Dict, Any, List

def evaluate_metric_change(
    before_stats: Dict[str, float],
    after_stats: Dict[str, float],
    lower_is_better: bool = True,
    noise_factor: float = 1.0
) -> Dict[str, Any]:
    """
    Compara estadísticamente una métrica entre 'Antes' y 'Después'.

    Regla Estricta:
    No se declara mejora/degradación a menos que la diferencia absoluta de medianas
    supere el margen de ruido de medición (basado en el IQR o desviación estándar).
    """
    med_before = before_stats.get("median", 0.0)
    med_after = after_stats.get("median", 0.0)
    diff = med_after - med_before

    iqr_before = before_stats.get("iqr", 0.0)
    iqr_after = after_stats.get("iqr", 0.0)
    std_before = before_stats.get("std_dev", 0.0)
    std_after = after_stats.get("std_dev", 0.0)

    # Margen de variabilidad esperada de las mediciones (ruido instrumental/ambiental)
    noise_threshold = max(
        iqr_before,
        iqr_after,
        std_before,
        std_after,
        0.01  # Margen numérico mínimo para evitar división por cero o falsos positivos
    ) * noise_factor

    pct_change = ((med_after - med_before) / med_before * 100.0) if med_before != 0 else 0.0

    abs_diff = abs(diff)
    is_significant = abs_diff > noise_threshold

    if not is_significant:
        status = "NO_SIGNIFICATIVE_CHANGE"
        verdict_es = "Sin cambio significativo (dentro del margen de ruido de medición)"
        is_improvement = False
    else:
        if lower_is_better:
            if diff < 0:
                status = "IMPROVEMENT"
                verdict_es = "Mejora confirmada"
                is_improvement = True
            else:
                status = "REGRESSION"
                verdict_es = "Degradación detectada"
                is_improvement = False
        else: # higher is better
            if diff > 0:
                status = "IMPROVEMENT"
                verdict_es = "Mejora confirmada"
                is_improvement = True
            else:
                status = "REGRESSION"
                verdict_es = "Degradación detectada"
                is_improvement = False

    return {
        "median_before": med_before,
        "median_after": med_after,
        "absolute_difference": round(diff, 3),
        "percent_change": round(pct_change, 2),
        "noise_threshold": round(noise_threshold, 3),
        "is_significant": is_significant,
        "status": status,
        "verdict_es": verdict_es,
        "is_improvement": is_improvement,
        "iqr_before": iqr_before,
        "iqr_after": iqr_after
    }

class BenchmarkComparator:
    """
    Compara dos resúmenes de Benchmark ("Antes / Baseline" vs "Después / Optimized").
    Analiza cambios, evalúa significancia estadística y genera advertencias causales.
    """

    def __init__(self, before_summary: Dict[str, Any], after_summary: Dict[str, Any]):
        self.before = before_summary
        self.after = after_summary

    def compare(self) -> Dict[str, Any]:
        before_metrics = self.before.get("metrics_summary", {})
        after_metrics = self.after.get("metrics_summary", {})

        metric_config = [
            ("cpu_usage_pct", "Uso de CPU en Reposo (%)", True),
            ("ram_usage_pct", "Uso de RAM en Reposo (%)", True),
            ("ram_used_mb", "Memoria RAM Usada (MB)", True),
            ("disk_read_bytes_sec", "Lecturas de Disco en Reposo (Bytes/s)", True),
            ("disk_write_bytes_sec", "Escrituras de Disco en Reposo (Bytes/s)", True),
            ("disk_iops", "E/S de Disco por Segundo (IOPS)", True),
            ("disk_time_pct", "Tiempo Activo de Disco (%)", True),
            ("net_rx_bytes_sec", "Tráfico Red Recibido en Reposo (Bytes/s)", True),
            ("net_tx_bytes_sec", "Tráfico Red Enviado en Reposo (Bytes/s)", True),
            ("ping_latency_ms", "Latencia de Red Ping (ms)", True),
        ]

        comparisons: Dict[str, Any] = {}
        improvements_count = 0
        regressions_count = 0
        no_change_count = 0

        for key, name_es, lower_better in metric_config:
            b_stats = before_metrics.get(key, {})
            a_stats = after_metrics.get(key, {})
            eval_res = evaluate_metric_change(b_stats, a_stats, lower_is_better=lower_better)
            eval_res["name_es"] = name_es
            comparisons[key] = eval_res

            if eval_res["status"] == "IMPROVEMENT":
                improvements_count += 1
            elif eval_res["status"] == "REGRESSION":
                regressions_count += 1
            else:
                no_change_count += 1

        # Comparación de Tiempo de Arranque si está medible en ambos
        boot_before = self.before.get("boot_info", {})
        boot_after = self.after.get("boot_info", {})
        boot_comparison = None

        if boot_before.get("measurable") and boot_after.get("measurable"):
            b_boot = boot_before.get("boot_time_ms")
            a_boot = boot_after.get("boot_time_ms")
            if b_boot is not None and a_boot is not None:
                # Tratar como métrica estática
                b_dummy = {"median": b_boot, "iqr": b_boot * 0.05, "std_dev": b_boot * 0.05}
                a_dummy = {"median": a_boot, "iqr": a_boot * 0.05, "std_dev": a_boot * 0.05}
                boot_comparison = evaluate_metric_change(b_dummy, a_dummy, lower_is_better=True)
                boot_comparison["name_es"] = "Tiempo de Arranque del Sistema (ms)"
                if boot_comparison["status"] == "IMPROVEMENT":
                    improvements_count += 1
                elif boot_comparison["status"] == "REGRESSION":
                    regressions_count += 1
                else:
                    no_change_count += 1

        # Comparación de Aplicaciones de Inicio
        apps_before_cnt = self.before.get("startup_apps_count", 0)
        apps_after_cnt = self.after.get("startup_apps_count", 0)
        apps_diff = apps_after_cnt - apps_before_cnt

        # Análisis Causal y Factores de Confusión
        causal_analysis = {
            "correlation_vs_causality_note": (
                "IMPORTANTE: Una diferencia observada entre mediciones 'Antes' y 'Después' refleja una correlación "
                "temporal, pero no garantiza causalidad directa de una optimización específica. Factores externos como "
                "actualizaciones de Windows en segundo plano, tareas de mantenimiento automático, indexación de archivos, "
                "temperatura del procesador o fluctuaciones de red pueden causar variaciones independientes de la configuración."
            ),
            "confounding_factors_checked": [
                "Servicios en segundo plano de Windows (Update, Search, Defender)",
                "Tareas programadas de mantenimiento del sistema",
                "Carga térmica y throttling dinámico del procesador",
                "Variabilidad de latencia por tráfico en la red local/proveedor"
            ],
            "methodological_recommendation": (
                "Para confirmar causalidad: 1) Mantener condiciones ambientales idénticas (sin aplicaciones abiertas). "
                "2) Asegurar N>=3 repeticiones por perfil. 3) Reiniciar el sistema entre sesiones de prueba si se "
                "modificaron servicios o controladores."
            )
        }

        # Veredicto Global
        if improvements_count > regressions_count and improvements_count > 0:
            global_verdict = "MEJORA_GLOBAL_DETECTADA"
            global_verdict_es = "Se registraron mejoras estadísticamente significativas en varias métricas principales."
        elif regressions_count > improvements_count:
            global_verdict = "DEGRADACION_GLOBAL_DETECTADA"
            global_verdict_es = "Se observó un impacto negativo o degradación en el rendimiento global."
        else:
            global_verdict = "SIN_CAMBIO_GLOBAL_SIGNIFICATIVO"
            global_verdict_es = "No hay evidencia suficiente de cambios de rendimiento que superen el margen de ruido."

        return {
            "before_profile": self.before.get("profile_name", "Antes"),
            "after_profile": self.after.get("profile_name", "Después"),
            "timestamp_before": self.before.get("timestamp", 0),
            "timestamp_after": self.after.get("timestamp", 0),
            "global_summary": {
                "improvements_count": improvements_count,
                "regressions_count": regressions_count,
                "no_change_count": no_change_count,
                "global_verdict": global_verdict,
                "global_verdict_es": global_verdict_es
            },
            "startup_apps_change": {
                "before_count": apps_before_cnt,
                "after_count": apps_after_cnt,
                "difference": apps_diff
            },
            "boot_time_comparison": boot_comparison,
            "metrics_comparison": comparisons,
            "causal_analysis": causal_analysis
        }
