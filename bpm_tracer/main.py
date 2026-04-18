"""
main.py — Punto de entrada CLI para BPM Tracer.

Uso:
    python -m bpm_tracer.main <archivo_audio> [opciones]

Ejemplos:
    python -m bpm_tracer.main track.mp3
    python -m bpm_tracer.main track.wav -m 8 -o resultado.md
    python -m bpm_tracer.main track.flac -v
"""

import argparse
import os
import sys
import time

# Monkey patch numpy for madmom compatibility (Numpy 2.0+ removed these aliases)
import numpy as np
if not hasattr(np, 'int'): np.int = int
if not hasattr(np, 'float'): np.float = float
if not hasattr(np, 'bool'): np.bool = bool
if not hasattr(np, 'complex'): np.complex = complex
if not hasattr(np, 'object'): np.object = object
if not hasattr(np, 'str'): np.str = str

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from bpm_tracer.audio_loader import load_audio
from bpm_tracer.beat_tracker import detect_beats
from bpm_tracer.meter_detector import detect_meter
from bpm_tracer.block_analyzer import analyze_blocks
from bpm_tracer.output_formatter import display_summary, display_table, export_markdown

console = Console()


def create_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos CLI."""
    parser = argparse.ArgumentParser(
        prog="bpm-tracer",
        description=(
            "BPM Tracer -- Analiza archivos de audio para detectar BPM por bloque "
            "y firma de compas (time signature) de forma automatica."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python -m bpm_tracer.main track.mp3\n"
            "  python -m bpm_tracer.main track.wav -m 8 -o resultado.md\n"
            "  python -m bpm_tracer.main track.flac -v\n"
        ),
    )

    parser.add_argument(
        "audio_file",
        type=str,
        help="Ruta al archivo de audio (MP3, WAV, FLAC, OGG, etc.)",
    )

    parser.add_argument(
        "-m", "--measures-per-block",
        type=int,
        default=4,
        help="Número de compases por bloque (default: 4)",
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Ruta del archivo Markdown de salida (ej: resultado.md)",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Mostrar información detallada de debug",
    )

    return parser


def run(args: argparse.Namespace) -> None:
    """Ejecuta el pipeline completo de análisis."""
    audio_file = args.audio_file
    measures_per_block = args.measures_per_block
    output_path = args.output
    verbose = args.verbose

    # Validar archivo
    if not os.path.isfile(audio_file):
        console.print(f"[bold red]X Archivo no encontrado:[/bold red] {audio_file}")
        sys.exit(1)

    # Banner
    console.print()
    console.print("[bold cyan]+======================================+[/bold cyan]")
    console.print("[bold cyan]|     BPM Tracer v1.0.0                |[/bold cyan]")
    console.print("[bold cyan]|     Audio BPM & Meter Analysis       |[/bold cyan]")
    console.print("[bold cyan]+======================================+[/bold cyan]")
    console.print()

    start_time = time.time()

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        console=console,
        transient=not verbose,
    ) as progress:
        # Paso 1: Cargar audio
        task = progress.add_task("[cyan]Cargando audio...", total=4)
        audio_data = load_audio(audio_file, verbose=verbose)
        progress.update(task, advance=1, description="[cyan]Audio cargado (OK)")

        # Paso 2: Detectar beats
        progress.update(task, description="[cyan]Detectando beats...")
        beat_data = detect_beats(audio_data, verbose=verbose)
        progress.update(task, advance=1, description="[cyan]Beats detectados (OK)")

        # Paso 3: Detectar time signature
        progress.update(task, description="[cyan]Detectando time signature...")
        meter_data = detect_meter(audio_file, beat_data, audio_data, verbose=verbose)
        progress.update(task, advance=1, description="[cyan]Time signature detectada (OK)")

        # Paso 4: Analizar bloques
        progress.update(task, description="[cyan]Analizando bloques...")
        blocks = analyze_blocks(
            beat_data, meter_data,
            measures_per_block=measures_per_block,
            verbose=verbose,
        )
        progress.update(task, advance=1, description="[green]Analisis completado (OK)")

    elapsed = time.time() - start_time
    console.print(f"[dim]Tiempo de procesamiento: {elapsed:.1f}s[/dim]")

    # Mostrar resultados
    display_summary(audio_data, meter_data, blocks)
    display_table(blocks)

    # Exportar a Markdown si se especificó
    if output_path:
        # Asegurar extensión .md
        if not output_path.endswith(".md"):
            output_path += ".md"
        export_markdown(blocks, audio_data, meter_data, output_path)


def main():
    """Entry point."""
    parser = create_parser()
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
