# 🖥️ Windows Optimization Benchmark (Windows 10 x64)

Herramienta científica de medición y comparación de rendimiento para sistemas Windows 10 x64.
Permite registrar y comparar objetivamente el estado del sistema **antes y después** de aplicar configuraciones de optimización, garantizando el cumplimiento de rigor estadístico y distinguiendo explícitamente entre correlación y causalidad.

---

## 🎯 Características Principales

1. **Recolección Rigurosa de Métricas**:
   - **Tiempo de Arranque**: Event ID 100 del Visor de Eventos de Windows (*Microsoft-Windows-Diagnostics-Performance/Operational*) o Uptime.
   - **Uso de CPU y RAM en Reposo**: Muestreo continuo con periodo de estabilización (*Warm-up*).
   - **Actividad de Disco**: IOPS, tasas de transferencia en lectura/escritura (Bytes/s) y porcentaje de tiempo activo.
   - **Aplicaciones y Tareas al Inicio**: Inspección de Registro (`HKCU`/`HKLM` Run), carpetas Startup y Tareas Programadas.
   - **Tráfico de Red y Latencia**: Tasa de datos recibidos/enviados en reposo y latencia ICMP/TCP ping.

2. **Estandarización y Análisis Estadístico**:
   - Parámetros estandarizados: Número de repeticiones ($N$), tiempo de reposo y calentamiento.
   - Cálculo de tendencia central y variabilidad: **Mediana**, **Rango Intercuartílico (IQR)**, Desviación Estándar, Mínimo y Máximo.

3. **Regla de Significancia Estadística y No-Modificación**:
   - **Diseño de Solo Lectura**: La herramienta **nunca modifica el equipo automáticamente**.
   - **Regla Estricta**: No se declara una mejora si la diferencia observada entre mediciones no supera la variabilidad natural o margen de ruido del sistema ($|\Delta| \le \text{Umbral de Ruido}$).

4. **Distinción entre Correlación y Causalidad**:
   - Analizador metodológico que previene atribuir mejoras o degradaciones a optimizaciones específicas cuando existen factores de confusión (e.g., Windows Update, Defender, tareas en segundo plano o fluctuaciones de red).

5. **Formatos de Exportación e Interfaz en Español**:
   - Exportación estructurada en **JSON** y **CSV**.
   - Visor interactivo standalone **HTML** alineado con el estándar de diseño *Research Identity 10.0*.
   - Interfaz de Línea de Comandos (**CLI**) en español.

---

## 🚀 Guía de Uso

### 1. Medir Perfil "Antes / Baseline"
```bash
python -m windows_optimization_benchmark.cli medir \
    --perfil "Baseline_Antes" \
    --repeticiones 3 \
    --duracion 10 \
    --calentamiento 2 \
    --out-json baseline.json \
    --out-csv baseline.csv
```

### 2. Medir Perfil "Después / Optimizado"
Tras aplicar los cambios de optimización manualmente en Windows 10 x64:
```bash
python -m windows_optimization_benchmark.cli medir \
    --perfil "Optimizado_Despues" \
    --repeticiones 3 \
    --duracion 10 \
    --calentamiento 2 \
    --out-json optimizado.json \
    --out-csv optimizado.csv
```

### 3. Comparar Configuraciones y Generar Reportes
```bash
python -m windows_optimization_benchmark.cli comparar \
    --antes baseline.json \
    --despues optimizado.json \
    --out-json comparacion.json \
    --out-csv comparacion.csv \
    --out-html reporte_visor.html
```

---

## 🔬 Metodología Estadística y Causalidad

- **Mediana vs Media**: La mediana se utiliza como indicador primario de tendencia central debido a su insensibilidad a picos atípicos espontáneos producidos por procesos en segundo plano.
- **Rango Intercuartílico (IQR)**: Mide la dispersión del 50% central de los datos, definiendo el umbral dinámico de ruido del sistema.
- **Evaluación Causal**: La herramienta marca explícitamente cualquier cambio menor al umbral de ruido como *"Sin cambio significativo"*, evitando conclusiones erróneas de optimizaciones ineficaces.

---
*Desarrollado como parte del repositorio de Investigación Abierta por Dr. Juan Moisés de la Serna.*
