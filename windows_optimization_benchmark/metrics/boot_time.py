"""
Módulo para medición del Tiempo de Arranque en Windows 10 x64.
Lee el Visor de Eventos de Windows (Event ID 100 de Diagnostic-Performance) o la hora de inicio del sistema.
"""

import sys
import os
import subprocess
import json
import time
from typing import Dict, Any, Optional

def measure_boot_time(use_simulation_fallback: bool = True) -> Dict[str, Any]:
    """
    Obtiene el tiempo de arranque de Windows 10 x64.
    Busca Event ID 100 de Microsoft-Windows-Diagnostics-Performance/Operational.
    Si no está disponible o no se ejecuta en Windows, utiliza un fallback o simulación.
    """
    result: Dict[str, Any] = {
        "measurable": False,
        "boot_time_ms": None,
        "main_path_boot_time_ms": None,
        "post_boot_time_ms": None,
        "method": "Unknown",
        "details": "",
        "timestamp": time.time()
    }

    if sys.platform == "win32":
        # Intentar obtener el último evento ID 100 de Diagnostic-Performance via PowerShell
        ps_script = (
            "$event = Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Diagnostics-Performance/Operational'; Id=100} -MaxEvents 1 -ErrorAction SilentlyContinue; "
            "if ($event) { "
            "  $xml = [xml]$event.ToXml(); "
            "  $bootTime = $xml.Event.EventData.Data | Where-Object {$_.Name -eq 'BootTime'} | Select-Object -ExpandProperty '#text'; "
            "  $mainPath = $xml.Event.EventData.Data | Where-Object {$_.Name -eq 'MainPathBootTime'} | Select-Object -ExpandProperty '#text'; "
            "  $postBoot = $xml.Event.EventData.Data | Where-Object {$_.Name -eq 'BootPostBootTime'} | Select-Object -ExpandProperty '#text'; "
            "  @{BootTime=$bootTime; MainPathBootTime=$mainPath; BootPostBootTime=$postBoot; TimeCreated=$event.TimeCreated} | ConvertTo-Json "
            "} else { 'null' }"
        )
        try:
            cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script]
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=10).decode("utf-8", errors="ignore").strip()
            if output and output != "null":
                data = json.loads(output)
                boot_ms = float(data.get("BootTime", 0))
                main_ms = float(data.get("MainPathBootTime", 0))
                post_ms = float(data.get("BootPostBootTime", 0))
                if boot_ms > 0:
                    result["measurable"] = True
                    result["boot_time_ms"] = boot_ms
                    result["main_path_boot_time_ms"] = main_ms
                    result["post_boot_time_ms"] = post_ms
                    result["method"] = "EventLog_100"
                    result["details"] = f"Registro Diagnostic-Performance Event 100 ({data.get('TimeCreated', '')})"
                    return result
        except Exception as e:
            result["details"] = f"Error consultando EventLog: {e}"

        # Fallback a tiempo desde último reinicio (System Uptime)
        try:
            ps_uptime = "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime"
            cmd_uptime = ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_uptime]
            out_uptime = subprocess.check_output(cmd_uptime, stderr=subprocess.DEVNULL, timeout=5).decode("utf-8", errors="ignore").strip()
            if out_uptime:
                result["measurable"] = True
                result["method"] = "SystemUptimeReference"
                result["details"] = f"Último inicio registrado: {out_uptime}"
                return result
        except Exception:
            pass

    if use_simulation_fallback:
        # Modo fallback para entornos no-Windows o pruebas de laboratorio
        result["measurable"] = True
        result["boot_time_ms"] = 28500.0  # 28.5 segundos simulados
        result["main_path_boot_time_ms"] = 18200.0
        result["post_boot_time_ms"] = 10300.0
        result["method"] = "Simulated_Fallback"
        result["details"] = "Modo simulado / Entorno de pruebas (No ejecutable en sistema no-Windows sin permisos)"

    return result
