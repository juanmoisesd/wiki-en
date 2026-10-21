# Network Traffic Observatory para Windows 10 x64

**Network Traffic Observatory** es una utilidad ligera, local y autónoma desarrollada en Python para monitorizar conexiones de red en tiempo real e históricas en **Windows 10 x64**, utilizando únicamente **APIs nativas del sistema operativo Windows y registros oficiales**.

---

## 🛡️ Principios de Diseño, Seguridad y Privacidad Local

1. **APIs Nativas de Windows**:
   Utiliza `iphlpapi.dll` (`GetExtendedTcpTable`, `GetExtendedUdpTable`, `GetIfTable2`), `kernel32.dll` y `psapi.dll` (`OpenProcess`, `QueryFullProcessImageNameW`).
2. **Sin Controladores ni Certificados de Terceros**:
   No requiere ni instala WinPcap, Npcap, Wireshark, ni certificados de inspección SSL/TLS o CA.
3. **Cero Captura de Contenido Privado o Contraseñas**:
   Opera estrictamente a nivel de **metadatos de red** (direcciones IP, puertos, protocolos, PIDs, duraciones y contadores de bytes). No examina ni almacena el payload de los paquetes.
4. **Diferenciación Clara de Estados**:
   - **Conexiones Activas**: Conexiones presentes actualmente en las tablas MIB de Windows.
   - **Conexiones Históricas**: Conexiones cerradas o finalizadas durante la sesión de monitoreo.
5. **Precisión en Métricas de Tráfico**:
   Diferencia explícitamente entre **Bytes Observados** (extraídos mediante contadores de interfaz MIB_IF_ROW2 / TCP EStats) e **Bytes Estimados** (calculados en fallback).
6. **Clasificación No Juiciosa de Destinos**:
   Un destino remoto desconocido no se etiquetará jamás como "malicioso" o "amenaza" por el mero hecho de no estar resuelto o no ser reconocido. Se clasifica de forma objetiva (p. ej. *Public Destination*, *Private LAN Network*, *Loopback*).

---

## 🚀 Requisitos de Sistema e Instalación

- **Sistema Operativo**: Windows 10 x64 (compatible con Windows 11 / Windows Server 2016+).
- **Python**: Python 3.8+ (64-bit recomendado).
- **Dependencias**: Dependencias estándar de Python (`ctypes`, `socket`, `csv`, `json`, `argparse`, `wintypes`). No requiere bibliotecas externas de `pip`.

---

## 📖 Guía de Uso

### 1. Monitoreo Interactivo en Tiempo Real
Ejecuta la herramienta directamente para iniciar el escaneo de conexiones:
```cmd
python network_traffic_observatory.py
```

### 2. Modo Pasivo (Monitoreo en Segundo Plano)
Inicia la herramienta en modo pasivo sin bloquear la pantalla con salidas detalladas:
```cmd
python network_traffic_observatory.py --passive --interval 2.0
```

### 3. Filtrado de Consultas por Parámetros
Puedes filtrar las conexiones registradas por protocolo, proceso, IP remota, puerto o estado:
```cmd
python network_traffic_observatory.py --protocol TCP --app chrome.exe --status ACTIVE
python network_traffic_observatory.py --remote-ip 192.168.1 --port 443
```

### 4. Exportación de Datos (CSV y JSON) con Anonimización Opcional
Para guardar el registro completo y el resumen agrupado por aplicación:
```cmd
python network_traffic_observatory.py --duration 30 --export-csv reporte_red.csv --export-json reporte_red.json --anonymize
```

---

## 📊 Parámetros de Línea de Comandos (CLI)

| Opción | Descripción |
| :--- | :--- |
| `--passive` | Ejecuta en modo observación pasiva. |
| `--interval SEC` | Intervalo de muestreo en segundos (por defecto: 2.0s). |
| `--duration SEC` | Duración total de ejecución en segundos (0 = indefinido). |
| `--protocol {TCP,UDP}` | Filtra por protocolo de transporte. |
| `--app SUBSTRING` | Filtra por nombre o ruta de proceso propietario (ej: `chrome.exe`). |
| `--status {ACTIVE,HISTORICAL,ALL}` | Filtra por conexiones activas, históricas o todas. |
| `--remote-ip SUBSTRING` | Filtra por dirección IP remota. |
| `--port PORT` | Filtra por puerto local o remoto. |
| `--export-csv PATH` | Exporta resultados en formato CSV. |
| `--export-json PATH` | Exporta resultados en formato JSON. |
| `--anonymize` | Máscara las direcciones IP para privacidad local adicional. |

---

## ⚙️ Registro de Windows Consultado (`HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters`)

La herramienta lee las configuraciones nativas del registro de red de Windows al iniciar:
- `SynAttackProtect`: Nivel de protección contra ataques SYN.
- `TcpTimedWaitDelay`: Tiempo de espera en estado TIME_WAIT.
- `MaxUserPort`: Puerto máximo para conexiones salientes dinámicas.
- `EnableICMPRedirect`: Configuración de redirección ICMP.

---

## 🧪 Verificación y Suite de Pruebas Unitarias

Para ejecutar la suite de pruebas automáticas en cualquier entorno:
```bash
python3 -m unittest test_network_traffic_observatory.py
```

---
*Network Traffic Observatory - Fiel al compromiso de transparencia, seguridad y privacidad.*
