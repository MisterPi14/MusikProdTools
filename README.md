# 🎵 BPM Tracer (MusikProdTools)

**BPM Tracer** es una herramienta de terminal (CLI) diseñada para analizar archivos de audio y realizar ingeniería inversa sobre sus métricas de tiempo. Extrae el BPM y el métrico (Firma de Compás) del track, ofreciendo una alta granularidad al medir las pulsaciones por minuto divididas sistemáticamente en "bloques" musicales (ej. fragmentos de 4 compases). 

La herramienta utiliza **Librosa** para separación armónica/percusiva y análisis general del audio, y **Madmom** (Redes Neuronales Recurrentes) para realizar _Downbeat Tracking_ a nivel de estado de arte, permitiendo a la herramienta inferir compases inusuales o complejos (ej. 3/4, 4/4, 6/8, 7/8).

## Características

* Análisis profundo usando la arquitectura de redes neuronales (DBNDownBeatTrackingProcessor).
* Agrupación paramétrica de beats y estimativo individualizado de BPM.
* Soporte nativo para inferir el _Time Signature_ de manera predictiva, con respaldos heurísticos en caso de baja confianza.
* Salidas ricas en terminal y exportación automatizada a Markdown (`.md`).
* Soporta la gran mayoría de formatos estándar (.mp3, .wav, .flac, .ogg).

## Instalación

Esta aplicación requiere **Python 3.10+**. (Validada exitosamente en Python 3.13). En Windows, para automatizar la configuración del entorno, la descarga de librerías y la solución inmediata de los parches de compatibilidad de NumPy para `madmom`, sigue estos pasos:

1. Clona este repositorio o descarga sus archivos.
2. Abre la consola en el directorio raíz del proyecto.
3. Ejecuta el instalador automático en Windows:

```bat
setup.bat
```

> **Nota para puristas:** `setup.bat` llama a `patch_madmom.py`. Dado que Madmom no se actualizó para Numpy 2.0 y Python 3.12+, el parche intercepta todas las referencias obsoletas internamente dentro de tus site-packages y las rectifica, además de añadir _Monkey Patching_ a nivel de runtime. 

## Uso del CLI

### Análisis Básico
Pasa la ruta del audio como argumento. Automáticamente asumirá 4 compases por bloque de medición:

```bash
python -m bpm_tracer.main "mi_cancion.mp3"
```

### Modificación de bloques y exportación a reporte (.md)
Si necesitas agrupar el resultado cada `8` compases y generar un reporte permanente (ej. `analisis_completo.md`), utiliza los flags paramétricos correspondientes:

```bash
python -m bpm_tracer.main "mi_cancion.wav" -m 8 -o analisis_completo
```

### Ejecutar con Verbosidad Completa (Debug)
Útil si necesitas monitorear internamente cómo las RNN están debatiendo y evaluando las detecciones inter-beat intervals.

```bash
python -m bpm_tracer.main "mi_cancion.mp3" -v
```

## Arquitectura de Reportes
El programa proveerá una estética y métrica analítica de las desviaciones rítmicas del artista/productor a través de la pista de forma tabular:
* **BPM (Promedio local por bloque)**
* **Desviaciones respecto al núcleo de BPM:** Analiza acelerandos de batería o delays en el track de humano a máquina.
* **Trazabilidad en Segundos:** (Rango de inicio - fin del bloque).

---
*Desarrollado para el ecosistema de **MusikProdTools**.*
