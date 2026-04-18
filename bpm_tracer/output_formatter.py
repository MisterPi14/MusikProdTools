"""
output_formatter.py — Formato de salida: tabla en consola y exportación a Markdown.

Usa 'rich' para tablas con colores en la terminal.
Genera un archivo .md con la tabla de resultados y resumen.
"""

import os
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()


def display_summary(audio_data: dict, meter_data: dict, blocks: list[dict]) -> None:
    """
    Muestra un resumen del análisis en consola.
    """
    if not blocks:
        console.print("[red]No hay bloques para mostrar.[/red]")
        return

    bpms = [b["bpm"] for b in blocks]
    avg_bpm = np.mean(bpms)
    min_bpm = np.min(bpms)
    max_bpm = np.max(bpms)
    bpm_range = max_bpm - min_bpm

    summary_lines = [
        f"[bold]Archivo:[/bold]     {audio_data['filename']}",
        f"[bold]Duración:[/bold]    {audio_data['duration']:.2f}s ({audio_data['duration']/60:.1f} min)",
        f"[bold]Time Sig:[/bold]    {meter_data['time_signature']} "
        f"(confianza: {meter_data['confidence']:.0%}, método: {meter_data['method']})",
        f"[bold]BPM global:[/bold]  {avg_bpm:.1f}",
        f"[bold]BPM rango:[/bold]   {min_bpm:.1f} - {max_bpm:.1f} (Dif {bpm_range:.1f})",
        f"[bold]Bloques:[/bold]     {len(blocks)}",
    ]

    panel = Panel(
        "\n".join(summary_lines),
        title="[bold cyan]BPM Tracer -- Resumen[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)


def display_table(blocks: list[dict]) -> None:
    """
    Muestra la tabla de bloques en consola usando rich.
    """
    if not blocks:
        return

    table = Table(
        title="[bold]Análisis BPM por Bloque[/bold]",
        show_header=True,
        header_style="bold magenta",
        border_style="bright_black",
        row_styles=["", "dim"],
    )

    table.add_column("Bloque", justify="center", style="cyan", width=8)
    table.add_column("BPM", justify="center", style="bold green", width=10)
    table.add_column("Time Sig", justify="center", style="yellow", width=10)
    table.add_column("Inicio (s)", justify="right", style="white", width=12)
    table.add_column("Fin (s)", justify="right", style="white", width=12)
    table.add_column("Beats", justify="center", style="dim", width=7)

    # Calcular BPM promedio para colorear desviaciones
    bpms = [b["bpm"] for b in blocks]
    avg_bpm = np.mean(bpms)

    for block in blocks:
        # Colorear BPM según desviación del promedio
        deviation = abs(block["bpm"] - avg_bpm)
        if deviation < 1:
            bpm_style = "bold green"
        elif deviation < 3:
            bpm_style = "bold yellow"
        else:
            bpm_style = "bold red"

        bpm_text = Text(f"{block['bpm']:.1f}", style=bpm_style)

        table.add_row(
            str(block["block_number"]),
            bpm_text,
            block["time_signature"],
            f"{block['time_start']:.2f}",
            f"{block['time_end']:.2f}",
            str(block["num_beats"]),
        )

    console.print()
    console.print(table)
    console.print()


def export_markdown(
    blocks: list[dict],
    audio_data: dict,
    meter_data: dict,
    output_path: str,
) -> None:
    """
    Exporta los resultados a un archivo Markdown.

    Args:
        blocks: Lista de bloques con datos de BPM.
        audio_data: Datos del audio.
        meter_data: Datos de la firma de compás.
        output_path: Ruta del archivo .md de salida.
    """
    if not blocks:
        console.print("[red]No hay bloques para exportar.[/red]")
        return

    bpms = [b["bpm"] for b in blocks]
    avg_bpm = np.mean(bpms)
    min_bpm = np.min(bpms)
    max_bpm = np.max(bpms)

    lines = []
    lines.append(f"# BPM Traceability Report")
    lines.append("")
    lines.append(f"## Información General")
    lines.append("")
    lines.append(f"| Propiedad | Valor |")
    lines.append(f"|:---|:---|")
    lines.append(f"| **Archivo** | `{audio_data['filename']}` |")
    lines.append(
        f"| **Duración** | {audio_data['duration']:.2f}s "
        f"({audio_data['duration']/60:.1f} min) |"
    )
    lines.append(
        f"| **Time Signature** | {meter_data['time_signature']} "
        f"(confianza: {meter_data['confidence']:.0%}) |"
    )
    lines.append(f"| **Método de detección** | {meter_data['method']} |")
    lines.append(f"| **BPM promedio** | {avg_bpm:.1f} |")
    lines.append(f"| **BPM rango** | {min_bpm:.1f} – {max_bpm:.1f} |")
    lines.append(f"| **Total bloques** | {len(blocks)} |")
    lines.append("")
    lines.append(f"## Análisis por Bloque")
    lines.append("")
    lines.append(
        f"> Cada bloque representa un conjunto de compases consecutivos. "
        f"La columna **Dif** indica la desviación respecto al BPM promedio."
    )
    lines.append("")
    lines.append(
        f"| Bloque | BPM | Dif | Time Sig | Inicio (s) | Fin (s) | Beats |"
    )
    lines.append(
        f"|:------:|:---:|:-:|:--------:|:----------:|:-------:|:-----:|"
    )

    for block in blocks:
        delta = block["bpm"] - avg_bpm
        delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"

        lines.append(
            f"| {block['block_number']} "
            f"| {block['bpm']:.1f} "
            f"| {delta_str} "
            f"| {block['time_signature']} "
            f"| {block['time_start']:.2f} "
            f"| {block['time_end']:.2f} "
            f"| {block['num_beats']} |"
        )

    lines.append("")
    lines.append("---")
    lines.append(f"*Generado por BPM Tracer v1.0.0*")
    lines.append("")

    # Escribir archivo
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    console.print(
        f"[bold green](OK)[/bold green] Reporte exportado a: [underline]{output_path}[/underline]"
    )
