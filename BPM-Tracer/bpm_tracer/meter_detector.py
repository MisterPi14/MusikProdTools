"""
meter_detector.py — Detección automática de time signature (compás).

Estrategia dual:
1. madmom: RNN downbeat tracking con DBN para selección de metro
2. Heurística: análisis estadístico de intervalos entre downbeats

Soporta detección de: 2/4, 3/4, 4/4, 5/4, 6/8, 7/8, etc.
"""

import numpy as np
from collections import Counter
from rich.console import Console

console = Console()

# Metros candidatos para el DBN
CANDIDATE_METERS = [2, 3, 4, 5, 6, 7]


def detect_meter_madmom(file_path: str, verbose: bool = False) -> dict:
    """
    Detecta downbeats y metro usando madmom (RNN + DBN).

    Args:
        file_path: Ruta al archivo de audio.
        verbose: Si es True, muestra información de debug.

    Returns:
        dict con las claves:
            - downbeat_times: posiciones de downbeats en segundos
            - beat_positions: array de (time, beat_number) para cada beat
            - detected_meter: número de beats por compás detectado
            - confidence: nivel de confianza (0-1)
    """
    try:
        from madmom.features.downbeats import (
            RNNDownBeatProcessor,
            DBNDownBeatTrackingProcessor,
        )
    except ImportError:
        console.print(
            "[yellow]⚠ madmom no disponible. Usando método alternativo de detección de metro.[/yellow]"
        )
        return None

    if verbose:
        console.print("[dim]Ejecutando RNNDownBeatProcessor (madmom)...[/dim]")

    # Fase 1: Obtener activaciones con la RNN
    try:
        rnn_processor = RNNDownBeatProcessor()
        activations = rnn_processor(file_path)

        if verbose:
            console.print(f"[dim]  Activaciones shape: {activations.shape}[/dim]")

        # Fase 2: DBN downbeat tracking con múltiples metros candidatos
        if verbose:
            console.print(
                f"[dim]  Ejecutando DBN con metros candidatos: {CANDIDATE_METERS}[/dim]"
            )

        dbn_processor = DBNDownBeatTrackingProcessor(
            beats_per_bar=CANDIDATE_METERS,
            fps=100,
        )
        beat_positions = dbn_processor(activations)
    except Exception as e:
        console.print(f"[yellow][WARNING] madmom falló ({e}). Usando heurística.[/yellow]")
        return None
    # beat_positions es array de (time, beat_number)
    # beat_number = 1 indica downbeat

    if len(beat_positions) == 0:
        console.print("[yellow]⚠ No se detectaron beats con madmom.[/yellow]")
        return None

    # Extraer downbeats (beat_number == 1)
    downbeat_mask = beat_positions[:, 1] == 1
    downbeat_times = beat_positions[downbeat_mask, 0]

    # Determinar el metro detectado: contar beats entre downbeats consecutivos
    beats_per_bar_detected = []
    downbeat_indices = np.where(downbeat_mask)[0]

    for i in range(len(downbeat_indices) - 1):
        start_idx = downbeat_indices[i]
        end_idx = downbeat_indices[i + 1]
        num_beats = end_idx - start_idx
        beats_per_bar_detected.append(num_beats)

    if not beats_per_bar_detected:
        return None

    # Moda estadística del número de beats por compás
    counter = Counter(beats_per_bar_detected)
    detected_meter = counter.most_common(1)[0][0]
    confidence = counter[detected_meter] / len(beats_per_bar_detected)

    if verbose:
        console.print(f"[dim]  Downbeats detectados: {len(downbeat_times)}[/dim]")
        console.print(
            f"[dim]  Distribución de beats/compás: {dict(counter)}[/dim]"
        )
        console.print(
            f"[dim]  Metro detectado: {detected_meter} beats/bar "
            f"(confianza: {confidence:.1%})[/dim]"
        )

    return {
        "downbeat_times": downbeat_times,
        "beat_positions": beat_positions,
        "detected_meter": detected_meter,
        "confidence": confidence,
    }


def detect_meter_heuristic(beat_times: np.ndarray, onset_envelope: np.ndarray,
                           sr: int = 22050, verbose: bool = False) -> dict:
    """
    Método alternativo heurístico para detectar el metro.

    Analiza la periodicidad del onset strength envelope usando autocorrelación
    para encontrar patrones de acentuación recurrentes.

    Args:
        beat_times: Posiciones de beats en segundos.
        onset_envelope: Onset strength envelope.
        sr: Sample rate del audio.
        verbose: Si es True, muestra información de debug.

    Returns:
        dict con las claves:
            - detected_meter: número de beats por compás estimado
            - confidence: nivel de confianza (0-1)
            - downbeat_times: posiciones estimadas de downbeats
    """
    import librosa

    if len(beat_times) < 8:
        if verbose:
            console.print("[dim]  Pocos beats para análisis heurístico, asumiendo 4/4[/dim]")
        # Con pocos beats, no hay suficiente data — asumir 4/4
        downbeat_times = beat_times[::4] if len(beat_times) >= 4 else beat_times[:1]
        return {
            "detected_meter": 4,
            "confidence": 0.3,
            "downbeat_times": downbeat_times,
        }

    if verbose:
        console.print("[dim]Ejecutando detección heurística de metro...[/dim]")

    # Calcular tempograma para encontrar periodicidades rítmicas
    hop_length = 512
    tempogram = librosa.feature.tempogram(onset_envelope=onset_envelope, sr=sr, 
                                           hop_length=hop_length)

    # Calcular autocorrelación global del onset strength
    ac = librosa.autocorrelate(onset_envelope, max_size=len(onset_envelope) // 2)
    ac = ac / ac[0]  # Normalizar

    # Calcular inter-beat interval promedio (en frames)
    beat_frames = librosa.time_to_frames(beat_times, sr=sr, hop_length=hop_length)
    if len(beat_frames) >= 2:
        avg_ibi_frames = np.mean(np.diff(beat_frames))
    else:
        avg_ibi_frames = 43  # ~120 BPM default

    # Buscar picos en la autocorrelación a múltiplos del IBI
    # que corresponden a posibles metros
    best_meter = 4
    best_score = 0.0

    for candidate in CANDIDATE_METERS:
        lag = int(round(avg_ibi_frames * candidate))
        if lag < len(ac):
            score = ac[lag]
            if verbose:
                console.print(
                    f"[dim]  Candidato {candidate}/4: lag={lag}, score={score:.4f}[/dim]"
                )
            if score > best_score:
                best_score = score
                best_meter = candidate

    # Generar downbeat times estimados
    downbeat_times = beat_times[::best_meter]

    # Confianza basada en qué tan fuerte es el pico de autocorrelación
    confidence = min(max(best_score, 0.0), 1.0) * 0.7  # Scale down — heurístico

    if verbose:
        console.print(
            f"[dim]  Metro heurístico: {best_meter} beats/bar "
            f"(confianza: {confidence:.1%})[/dim]"
        )

    return {
        "detected_meter": best_meter,
        "confidence": confidence,
        "downbeat_times": downbeat_times,
    }


def detect_meter(file_path: str, beat_data: dict, audio_data: dict,
                 verbose: bool = False) -> dict:
    """
    Detecta el metro combinando madmom + heurística.

    Intenta usar madmom primero (más preciso). Si no está disponible o
    falla, usa el método heurístico como fallback.

    Args:
        file_path: Ruta al archivo de audio.
        beat_data: Diccionario retornado por beat_tracker.detect_beats().
        audio_data: Diccionario retornado por audio_loader.load_audio().
        verbose: Si es True, muestra información de debug.

    Returns:
        dict con las claves:
            - time_signature: string representando la firma (e.g. "4/4")
            - beats_per_bar: número de beats por compás
            - downbeat_times: posiciones de downbeats en segundos
            - confidence: nivel de confianza (0-1)
            - method: "madmom" o "heuristic"
    """
    if verbose:
        console.print("\n[bold]Detección de Time Signature[/bold]")

    # Intentar con madmom primero
    madmom_result = detect_meter_madmom(file_path, verbose=verbose)

    # Siempre ejecutar heurística para comparar
    heuristic_result = detect_meter_heuristic(
        beat_times=beat_data["beat_times"],
        onset_envelope=beat_data["onset_envelope"],
        sr=audio_data["sr"],
        verbose=verbose,
    )

    # Decidir cuál usar
    if madmom_result is not None and madmom_result["confidence"] >= 0.5:
        # madmom tiene alta confianza — usarlo
        meter = madmom_result["detected_meter"]
        downbeat_times = madmom_result["downbeat_times"]
        confidence = madmom_result["confidence"]
        method = "madmom"

        if verbose:
            console.print(
                f"[dim]  → Usando resultado de madmom: {meter} beats/bar "
                f"(confianza: {confidence:.1%})[/dim]"
            )
    elif madmom_result is not None:
        # madmom tiene baja confianza — comparar con heurística
        if heuristic_result["confidence"] > madmom_result["confidence"]:
            meter = heuristic_result["detected_meter"]
            downbeat_times = heuristic_result["downbeat_times"]
            confidence = heuristic_result["confidence"]
            method = "heuristic"
        else:
            meter = madmom_result["detected_meter"]
            downbeat_times = madmom_result["downbeat_times"]
            confidence = madmom_result["confidence"]
            method = "madmom"

        if verbose:
            console.print(
                f"[dim]  → Usando resultado de {method}: {meter} beats/bar "
                f"(confianza: {confidence:.1%})[/dim]"
            )
    else:
        # madmom no disponible — usar heurística
        meter = heuristic_result["detected_meter"]
        downbeat_times = heuristic_result["downbeat_times"]
        confidence = heuristic_result["confidence"]
        method = "heuristic"

        if verbose:
            console.print(
                f"[dim]  → Usando heurística: {meter} beats/bar "
                f"(confianza: {confidence:.1%})[/dim]"
            )

    # Determinar el denominador del time signature
    # Para la mayoría de los casos usamos /4
    # 6 beats → 6/8, 7 beats → 7/8 (convención musical)
    if meter in (6, 9, 12):
        denominator = 8
    elif meter in (7, 5, 11):
        denominator = 8
    else:
        denominator = 4

    time_signature = f"{meter}/{denominator}"

    return {
        "time_signature": time_signature,
        "beats_per_bar": meter,
        "downbeat_times": downbeat_times,
        "confidence": confidence,
        "method": method,
    }
