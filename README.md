# 🎛️ MusikProdTools

Bienvenido a **MusikProdTools**, un repositorio central (monorepo) destinado a albergar una suite creciente de herramientas para ingeniería de sonido, producción musical, DJing y análisis forense de audio.

El objetivo a futuro de este ecosistema es agrupar pequeñas a medianas utilidades de terminal, automatizaciones de procesamiento digital de señales (DSP) y scripts de Inteligencia Artificial que suelen estar esparcidos. Cada herramienta se desarrolla de forma modular y cuenta con su propia subcarpeta, su propio entorno virtual (`venv`) y su propia configuración detallada.

---

## 🛠️ Catálogo de Herramientas

A continuación se lista el catálogo actual de herramientas disponibles en el ecosistema. Ingresa a la carpeta de cada una para leer sus instrucciones específicas de instalación y uso.

### 1. [BPM Tracer](./BPM-Tracer)
Herramienta de análisis MIR (Music Information Retrieval) para detectar y medir de forma modular el Tempo y el Compás (Time Signature) de un track. 
*   **Para qué sirve:** A diferencia de los contadores comunes que arrojan un único número estático, BPM Tracer corta tú audio en bloques ajustables (ej. 4 compases) y calcula desviaciones orgánicas en el tempo o en el métrico (3/4, 7/8).
*   **Enfoque técnico:** Redes Neuronales Recurrentes aplicadas al audiosignal _Downbeat Tracking_.
*   [Ver Documentación e Instalación ➔](./BPM-Tracer/README.md)

---

> _Más herramientas se irán agregando a este repositorio orgánicamente._
