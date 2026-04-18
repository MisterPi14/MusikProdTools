"""
block_analyzer.py — Agrupación de beats en bloques y cálculo de BPM por bloque.

Un bloque es un conjunto de N compases consecutivos (default: 4).
Para cada bloque se calcula el BPM promedio a partir de los inter-beat intervals.
"""

import numpy as np
from rich.console import Console

console = Console()


def analyze_blocks(
    beat_data: dict,
    meter_data: dict,
    measures_per_block: int = 4,
    verbose: bool = False,
) -> list[dict]:
    """
    Agrupa beats en bloques de N compases y calcula BPM por bloque.

    Args:
        beat_data: Diccionario retornado por beat_tracker.detect_beats().
        meter_data: Diccionario retornado por meter_detector.detect_meter().
        measures_per_block: Número de compases por bloque (default: 4).
        verbose: Si es True, muestra información de debug.

    Returns:
        Lista de diccionarios, uno por bloque, con las claves:
            - block_number: número del bloque (1-indexed)
            - bpm: BPM promedio del bloque
            - time_start: tiempo de inicio del bloque (segundos)
            - time_end: tiempo de fin del bloque (segundos)
            - num_beats: número de beats en el bloque
            - time_signature: firma de compás
    """
    beat_times = beat_data["beat_times"]
    beats_per_bar = meter_data["beats_per_bar"]
    time_signature = meter_data["time_signature"]
    downbeat_times = meter_data["downbeat_times"]

    if len(beat_times) < 2:
        console.print("[red]✗ No hay suficientes beats para analizar bloques.[/red]")
        return []

    if verbose:
        console.print(f"\n[bold]Análisis por Bloques[/bold]")
        console.print(f"[dim]  Beats por compás: {beats_per_bar}[/dim]")
        console.print(f"[dim]  Compases por bloque: {measures_per_block}[/dim]")
        console.print(
            f"[dim]  Beats por bloque: {beats_per_bar * measures_per_block}[/dim]"
        )

    beats_per_block = beats_per_bar * measures_per_block
    blocks = []
    block_number = 1

    # Intentar alinear con downbeats si están disponibles
    # Encontrar el primer beat que coincida (o esté más cerca) de un downbeat
    start_offset = 0
    if len(downbeat_times) > 0:
        # Buscar el beat más cercano al primer downbeat
        first_downbeat = downbeat_times[0]
        diffs = np.abs(beat_times - first_downbeat)
        start_offset = np.argmin(diffs)
        if verbose:
            console.print(
                f"[dim]  Alineando con primer downbeat en t={first_downbeat:.3f}s "
                f"(offset: {start_offset} beats)[/dim]"
            )

    # Iterar en bloques
    i = start_offset
    while i + 1 < len(beat_times):
        end_i = min(i + beats_per_block, len(beat_times))

        # Si el último bloque tiene muy pocos beats, incluirlo de todos modos
        # pero solo si tiene al menos 2 beats para calcular BPM
        block_beats = beat_times[i:end_i]

        if len(block_beats) < 2:
            break

        # Calcular BPM del bloque a partir de inter-beat intervals
        ibi = np.diff(block_beats)
        mean_ibi = np.mean(ibi)
        block_bpm = 60.0 / mean_ibi if mean_ibi > 0 else 0.0

        block = {
            "block_number": block_number,
            "bpm": round(block_bpm, 1),
            "time_start": round(float(block_beats[0]), 2),
            "time_end": round(float(block_beats[-1]), 2),
            "num_beats": len(block_beats),
            "time_signature": time_signature,
        }
        blocks.append(block)

        if verbose:
            console.print(
                f"[dim]  Bloque {block_number}: "
                f"t={block['time_start']:.2f}-{block['time_end']:.2f}s, "
                f"BPM={block['bpm']}, beats={block['num_beats']}[/dim]"
            )

        block_number += 1
        i = end_i

    if verbose:
        console.print(f"[dim]  Total bloques: {len(blocks)}[/dim]")

    return blocks
