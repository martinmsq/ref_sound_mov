import os
import json
import re
from pathlib import Path
import subprocess


TARGET_I = "-22.0"  # -24
TARGET_LRA = "7.0"  # 7
TARGET_TP = "-1.5"  # -2

def open_movie_file(path_in, path_out):
    print("------- Open files -------")
    movie_path_in = Path(path_in)
    movie_path_out = Path(path_out)
    if not movie_path_in.exists():
        print("Please provide both input and output file paths.")
        return None
    movie_path_out.parent.mkdir(parents=True, exist_ok=True)
    return movie_path_in, movie_path_out

def extract_threads():
    cores = os.cpu_count()
    if cores <= 2:
        return 1
    elif cores <= 4:
        return 2
    else:
        return max(2, cores // 2)


def extract_info(movie):
    if movie is None:
        return None
    movie_path_in, movie_path_out = movie
    print("------- Extracting info -------")
    command = [
        "ffmpeg",
        "-threads", str(extract_threads()),
        "-filter_threads", str(extract_threads()),
        "-vn",
        "-i", str(movie_path_in),
        "-af", f"loudnorm=I={TARGET_I}:LRA={TARGET_LRA}:tp={TARGET_TP}:print_format=json",
        "-f", "null", "-"
    ]

    execution = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")

    match = re.search(r"{\s*\"input_i\".*}", execution.stderr, re.DOTALL)
    if not match:
        print("Error: No se pudieron extraer las medidas de audio.")
        print(execution.stderr)
        return

    metrics = json.loads(match.group(0))
    print("¡Análisis completado con éxito! Datos obtenidos:")
    print(json.dumps(metrics, indent=2))
    return metrics

def format_movie(metrics, movie):
    print("------- Formatting movie -------")
    if metrics is None:
        print("No se pudo formatear la película debido a errores en la extracción de métricas.")
        return
    filters = (
        f"loudnorm=I={TARGET_I}:LRA={TARGET_LRA}:tp={TARGET_TP}:"
        f"measured_I={metrics['input_i']}:"
        f"measured_LRA={metrics['input_lra']}:"
        f"measured_tp={metrics['input_tp']}:"
        f"measured_thresh={metrics['input_thresh']}:"
        f"offset={metrics['target_offset']}:"
        f"linear=true"
    )
    movie_path_in, movie_path_out = movie
    command = [
        "ffmpeg",
        "-y",
        "-threads", str(extract_threads()),
        "-filter_threads", str(extract_threads()),
        "-i", str(movie_path_in),
        "-af", filters,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        str(movie_path_out)
    ]

    print("Procesando película... Esto puede tardar unos minutos según la duración.")
    subprocess.run(command, check=True)
    print("¡Película procesada con éxito! Archivo de salida:", movie_path_out)



if __name__ == "__main__":
    movie = open_movie_file("", "")
    metrics = extract_info(movie)
    format_movie(metrics, movie)