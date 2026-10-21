"""
Motor de recolección de sesiones de Benchmark.
Estandariza duración, condiciones de reposo, calentamiento y repeticiones (N).
"""

import time
import platform
import uuid
from typing import Dict, Any, List, Optional

from windows_optimization_benchmark.metrics.boot_time import measure_boot_time
from windows_optimization_benchmark.metrics.cpu_ram import measure_idle_cpu_ram
from windows_optimization_benchmark.metrics.disk import measure_disk_activity
from windows_optimization_benchmark.metrics.startup_apps import get_startup_applications
from windows_optimization_benchmark.metrics.network import measure_ping_latency, measure_network_traffic

class BenchmarkCollector:
    """
    Ejecuta mediciones estandarizadas repetidas (N iteraciones)
    para capturar la distribución estadística del rendimiento del sistema.
    """

    def __init__(
        self,
        profile_name: str = "Sin_Nombre",
        repetitions: int = 3,
        sample_duration_sec: int = 10,
        warmup_sec: int = 2,
        ping_target: str = "8.8.8.8"
    ):
        self.profile_name = profile_name
        self.repetitions = max(1, repetitions)
        self.sample_duration_sec = sample_duration_sec
        self.warmup_sec = warmup_sec
        self.ping_target = ping_target

    def run_benchmark(self) -> Dict[str, Any]:
        """
        Ejecuta la sesión completa de medición estandarizada.
        """
        session_id = str(uuid.uuid4())
        start_timestamp = time.time()

        # Recolectar metadatos del entorno
        system_info = {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "node": platform.node()
        }

        # Medir aplicaciones de inicio (solo 1 inspección estática necesaria)
        startup_apps_info = get_startup_applications()

        # Medir tiempo de arranque
        boot_info = measure_boot_time()

        # Repeticiones para métricas dinámicas
        runs_data: List[Dict[str, Any]] = []

        for rep in range(1, self.repetitions + 1):
            run_result = {
                "run_index": rep,
                "timestamp": time.time(),
                "cpu_ram": measure_idle_cpu_ram(
                    duration_seconds=self.sample_duration_sec,
                    warmup_seconds=self.warmup_sec
                ),
                "disk": measure_disk_activity(
                    duration_seconds=self.sample_duration_sec,
                    warmup_seconds=self.warmup_sec
                ),
                "network_traffic": measure_network_traffic(
                    duration_seconds=self.sample_duration_sec,
                    warmup_seconds=self.warmup_sec
                ),
                "ping_latency": measure_ping_latency(
                    host=self.ping_target,
                    count=4
                )
            }
            runs_data.append(run_result)

        end_timestamp = time.time()

        return {
            "session_id": session_id,
            "profile_name": self.profile_name,
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "config": {
                "repetitions": self.repetitions,
                "sample_duration_sec": self.sample_duration_sec,
                "warmup_sec": self.warmup_sec,
                "ping_target": self.ping_target
            },
            "system_info": system_info,
            "boot_info": boot_info,
            "startup_apps": startup_apps_info,
            "runs": runs_data
        }
