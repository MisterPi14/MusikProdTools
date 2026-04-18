"""
beat_tracker.py — Detección de beats usando librosa.

Usa la componente percusiva del audio para obtener posiciones precisas de beats.
"""

import librosa
import numpy as np
from rich.console import Console

console = Console()


def detect_beats(audio_data: dict, verbose: bool = False) -> dict:
    """
    Detecta posiciones de beats en el audio.

    Args:
        audio_data: Diccionario retornado por audio_loader.load_audio().
        verbose: Si es True, muestra información de debug.

    Returns:
        dict con las claves:
            - beat_times: posiciones de cada beat en segundos (np.ndarray)
            - tempo_global: tempo global estimado (float, BPM)
            - onset_envelope: onset strength envelope
            - beat_frames: frames de los beats
    """
    y_perc = audio_data["y_percussive"]
    sr = audio_data["sr"]

    if verbose:
        console.print("[dim]Calculando onset strength envelope...[/dim]")

    # Calcular onset strength envelope sobre la componente percusiva
    onset_env = librosa.onset.onset_strength(y=y_perc, sr=sr)

    if verbose:
        console.print("[dim]Ejecutando beat tracking...[/dim]")

    # Beat tracking usando la componente percusiva
    tempo_global, beat_frames = librosa.beat.beat_track(
        y=y_perc,
        sr=sr,
        onset_envelope=onset_env,
        units="frames",
    )

    # Convertir a float si es array
    if hasattr(tempo_global, '__len__'):
        tempo_global = float(tempo_global[0]) if len(tempo_global) > 0 else 0.0
    else:
        tempo_global = float(tempo_global)

    # Convertir frames a tiempos en segundos
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    if verbose:
        console.print(f"[dim]  Tempo global estimado: {tempo_global:.1f} BPM[/dim]")
        console.print(f"[dim]  Beats detectados: {len(beat_times)}[/dim]")
        if len(beat_times) >= 2:
            ibi = np.diff(beat_times)
            console.print(
                f"[dim]  Inter-beat interval: "
                f"mean={np.mean(ibi):.3f}s, std={np.std(ibi):.3f}s[/dim]"
            )

    return {
        "beat_times": beat_times,
        "tempo_global": tempo_global,
        "onset_envelope": onset_env,
        "beat_frames": beat_frames,
    }
