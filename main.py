import os
import json
import re
from pathlib import Path
import subprocess


class MovieProcessor:
    def __init__(self, target_i=None, target_lra=None, target_tp=None):
        self.TARGET_I = target_i
        self.TARGET_LRA = target_lra
        self.TARGET_TP = target_tp

    def open_movie_file(self, path_in: str, path_out: str)-> tuple[Path, Path]:
        print("------- Open files -------")
        movie_path_in = Path(path_in)
        movie_path_out = Path(path_out)
        if not movie_path_in.exists():
            raise FileNotFoundError(f"El archivo de entrada no existe: {movie_path_in}")
        movie_path_out.parent.mkdir(parents=True, exist_ok=True)
        return movie_path_in, movie_path_out

    def extract_threads(self)-> int:
        cores = os.cpu_count()
        if cores <= 2:
            return 1
        elif cores <= 4:
            return 2
        else:
            return max(2, cores // 2)

    def extract_info(self, movie: tuple[Path, Path])-> dict:
        if movie is None:
            raise ValueError("No se proporcionó una película para extraer información.")
        movie_path_in, movie_path_out = movie
        print("------- Extracting info -------")
        command = [
            "ffmpeg",
            "-threads", str(self.extract_threads()),
            "-filter_threads", str(self.extract_threads()),
            "-vn",
            "-i", str(movie_path_in),
            "-af", f"loudnorm=I={self.TARGET_I}:LRA={self.TARGET_LRA}:tp={self.TARGET_TP}:print_format=json",
            "-f", "null", "-"
        ]

        execution = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")

        match = re.search(r"{\s*\"input_i\".*}", execution.stderr, re.DOTALL)
        if not match:
            raise RuntimeError("Error: No se pudieron extraer las medidas de audio.")
            #print(execution.stderr)

        metrics = json.loads(match.group(0))
        #print("¡Análisis completado con éxito! Datos obtenidos:")
        #print(json.dumps(metrics, indent=2))
        return metrics

    def format_movie(self,metrics: dict, movie: tuple[Path, Path]):
        print("------- Formatting movie -------")
        if metrics is None:
            raise ValueError("No se pudo formatear la película debido a errores en la extracción de métricas.")
        filters = (
            f"loudnorm=I={self.TARGET_I}:LRA={self.TARGET_LRA}:tp={self.TARGET_TP}:"
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
            "-threads", str(self.extract_threads()),
            "-filter_threads", str(self.extract_threads()),
            "-i", str(movie_path_in),
            "-af", filters,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            str(movie_path_out)
        ]

        print("Procesando película... Esto puede tardar unos minutos según la duración.")
        subprocess.run(command, check=True)
        print("¡Película procesada con éxito! Archivo de salida:", movie_path_out)
