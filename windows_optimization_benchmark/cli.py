"""
Interfaz de Línea de Comandos (CLI) en Español para Windows Optimization Benchmark.
Soporta captura de benchmark, comparación de perfiles y exportación a JSON/CSV/HTML.
"""

import sys
import os
import argparse
import json

from windows_optimization_benchmark.engine.collector import BenchmarkCollector
from windows_optimization_benchmark.engine.stats import summarize_benchmark_session
from windows_optimization_benchmark.engine.comparator import BenchmarkComparator
from windows_optimization_benchmark.reports.exporter import (
    export_to_json,
    load_from_json,
    export_summary_to_csv,
    export_comparison_to_csv
)
from windows_optimization_benchmark.reports.reporter import (
    generate_text_comparison_report,
    generate_html_report
)

def main():
    parser = argparse.ArgumentParser(
        description="Windows Optimization Benchmark v1.0.0 — Herramienta científica de medición de rendimiento."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando 'medir' (Run Benchmark)
    parser_run = subparsers.add_parser("medir", help="Ejecuta una sesión estandarizada de medición de rendimiento.")
    parser_run.add_argument("--perfil", type=str, default="Baseline_Antes", help="Nombre descriptivo del perfil de configuración.")
    parser_run.add_argument("--repeticiones", "-n", type=int, default=3, help="Número de repeticiones de muestreo.")
    parser_run.add_argument("--duracion", "-d", type=int, default=10, help="Duración en segundos de cada muestreo en reposo.")
    parser_run.add_argument("--calentamiento", "-w", type=int, default=2, help="Segundos de estabilización previo al muestreo.")
    parser_run.add_argument("--out-json", type=str, help="Ruta para guardar la sesión en JSON.")
    parser_run.add_argument("--out-csv", type=str, help="Ruta para exportar el resumen en CSV.")

    # Comando 'comparar' (Compare two JSON profiles)
    parser_comp = subparsers.add_parser("comparar", help="Compara dos sesiones de benchmark ('Antes' vs 'Después').")
    parser_comp.add_argument("--antes", required=True, help="Ruta al JSON de la sesión 'Antes / Baseline'.")
    parser_comp.add_argument("--despues", required=True, help="Ruta al JSON de la sesión 'Después / Optimizado'.")
    parser_comp.add_argument("--out-json", type=str, help="Ruta para exportar la comparación en JSON.")
    parser_comp.add_argument("--out-csv", type=str, help="Ruta para exportar la comparación en CSV.")
    parser_comp.add_argument("--out-html", type=str, help="Ruta para generar el reporte visor interactivo HTML.")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "medir":
        print(f"[*] Iniciando sesión de medición de benchmark: Perfil '{args.perfil}'...")
        print(f"    • Repeticiones: {args.repeticiones} | Duración: {args.duracion}s | Calentamiento: {args.calentamiento}s")
        collector = BenchmarkCollector(
            profile_name=args.perfil,
            repetitions=args.repeticiones,
            sample_duration_sec=args.duracion,
            warmup_sec=args.calentamiento
        )
        raw_session = collector.run_benchmark()
        summary = summarize_benchmark_session(raw_session)

        # Imprimir resumen rápido en consola
        print("\n[+] Resumen de Mediciones Registradas:")
        metrics = summary.get("metrics_summary", {})
        print(f"    • Uso de CPU (Mediana):  {metrics.get('cpu_usage_pct', {}).get('median')}% (IQR: {metrics.get('cpu_usage_pct', {}).get('iqr')})")
        print(f"    • Uso de RAM (Mediana):  {metrics.get('ram_usage_pct', {}).get('median')}%")
        print(f"    • IOPS Disco (Mediana): {metrics.get('disk_iops', {}).get('median')}")
        print(f"    • Latencia Ping (Mediana): {metrics.get('ping_latency_ms', {}).get('median')} ms")

        # Guardar en JSON si se especifica
        out_j = args.out_json or f"benchmark_{args.perfil.lower().replace(' ', '_')}.json"
        export_to_json(summary, out_j)
        print(f"[+] Sesión guardada en JSON: {out_j}")

        if args.out_csv:
            export_summary_to_csv(summary, args.out_csv)
            print(f"[+] Resumen exportado a CSV: {args.out_csv}")

    elif args.command == "comparar":
        print(f"[*] Cargando sesiones de comparación:")
        print(f"    • Antes:   {args.antes}")
        print(f"    • Después: {args.despues}")

        b_data = load_from_json(args.antes)
        a_data = load_from_json(args.despues)

        comparator = BenchmarkComparator(b_data, a_data)
        comp_result = comparator.compare()

        report_txt = generate_text_comparison_report(comp_result)
        print("\n" + report_txt)

        if args.out_json:
            export_to_json(comp_result, args.out_json)
            print(f"[+] Comparación guardada en JSON: {args.out_json}")

        if args.out_csv:
            export_comparison_to_csv(comp_result, args.out_csv)
            print(f"[+] Comparación exportada a CSV: {args.out_csv}")

        if args.out_html:
            generate_html_report(comp_result, args.out_html)
            print(f"[+] Visor HTML generado en: {args.out_html}")

if __name__ == "__main__":
    main()
