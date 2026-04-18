"""
audio_loader.py — Carga y preprocesamiento de archivos de audio.

Soporta MP3, WAV, FLAC, OGG y cualquier formato compatible con librosa/soundfile.
Realiza conversión a mono, resampling y separación armónico-percusiva (HPSS).
"""

import os
import librosa
import numpy as np
from rich.console import Console

console = Console()

# Sample rate estándar para análisis MIR
DEFAULT_SR = 22050


def load_audio(file_path: str, sr: int = DEFAULT_SR, verbose: bool = False) -> dict:
    """
    Carga un archivo de audio y lo preprocesa para análisis.

    Args:
        file_path: Ruta al archivo de audio.
        sr: Sample rate objetivo (default: 22050 Hz).
        verbose: Si es True, muestra información de debug.

    Returns:
        dict con las claves:
            - y: señal de audio (mono, resampled)
            - sr: sample rate
            - y_harmonic: componente armónica (HPSS)
            - y_percussive: componente percusiva (HPSS)
            - duration: duración en segundos
            - filename: nombre del archivo
    """
    # Validar que el archivo existe
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    # Obtener extensión para validación
    _, ext = os.path.splitext(file_path)
    supported_formats = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma', '.aiff'}
    if ext.lower() not in supported_formats:
        console.print(
            f"[yellow][WARNING] Formato '{ext}' no verificado. Intentando cargar de todas formas...[/yellow]"
        )

    if verbose:
        console.print(f"[dim]Cargando archivo: {file_path}[/dim]")

    # Cargar audio con librosa (convierte a mono automáticamente)
    y, sr_loaded = librosa.load(file_path, sr=sr, mono=True)
    duration = librosa.get_duration(y=y, sr=sr_loaded)

    if verbose:
        console.print(f"[dim]  Sample rate: {sr_loaded} Hz[/dim]")
        console.print(f"[dim]  Duración: {duration:.2f} s ({duration / 60:.1f} min)[/dim]")
        console.print(f"[dim]  Muestras: {len(y):,}[/dim]")

    # Separación armónico-percusiva (HPSS)
    # La componente percusiva es ideal para beat tracking
    if verbose:
        console.print("[dim]  Aplicando separación armónico-percusiva (HPSS)...[/dim]")

    y_harmonic, y_percussive = librosa.effects.hpss(y)

    if verbose:
        console.print("[dim]  (OK) HPSS completado[/dim]")

    return {
        "y": y,
        "sr": sr_loaded,
        "y_harmonic": y_harmonic,
        "y_percussive": y_percussive,
        "duration": duration,
        "filename": os.path.basename(file_path),
    }
