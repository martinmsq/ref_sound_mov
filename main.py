import os
import json
import re
import threading
from pathlib import Path
import subprocess
from typing import Callable, Optional


class ProcessingCancelled(Exception):
    """Se lanza cuando el usuario cancela el procesado en curso."""
    pass


class MovieProcessor:
    def __init__(self, target_i=None, target_lra=None, target_tp=None):
        self.TARGET_I = target_i
        self.TARGET_LRA = target_lra
        self.TARGET_TP = target_tp

    def open_movie_file(self, path_in: str, path_out: str)-> tuple[Path, Path]:
        """Abre el archivo de entrada y prepara la ruta de salida."""
        print("------- Open files -------")
        movie_path_in = Path(path_in)
        movie_path_out = Path(path_out)
        if not movie_path_in.exists():
            raise FileNotFoundError(f"El archivo de entrada no existe: {movie_path_in}")
        movie_path_out.parent.mkdir(parents=True, exist_ok=True)
        return movie_path_in, movie_path_out

    def extract_threads(self)-> int:
        """Devuelve el número de hilos basado en los núcleos de el CPU."""
        cores = os.cpu_count() or 2
        if cores <= 2:
            return 1
        elif cores <= 4:
            return 2
        else:
            return max(2, cores // 2)

    def _validate_targets(self):
        """Valida la conversion y los rangos de loudnorm antes de lanzar el proceso."""
        try:
            target_i = float(self.TARGET_I)
        except (TypeError, ValueError):
            raise ValueError(f"Integrated loudness (I) inválido: {self.TARGET_I!r}.")
        try:
            target_lra = float(self.TARGET_LRA)
        except (TypeError, ValueError):
            raise ValueError(f"Loudness range (LRA) inválido: {self.TARGET_LRA!r}.")
        try:
            target_tp = float(self.TARGET_TP)
        except (TypeError, ValueError):
            raise ValueError(f"True peak (TP) inválido: {self.TARGET_TP!r}.")

        if not -70 <= target_i <= -5:
            raise ValueError(f"I={target_i} fuera de rango [-70, -5] de loudnorm.")
        if not 1 <= target_lra <= 50:
            raise ValueError(f"LRA={target_lra} fuera de rango [1, 50] de loudnorm.")
        if not -9 <= target_tp <= 0:
            raise ValueError(f"TP={target_tp} fuera de rango [-9, 0] de loudnorm.")

    def get_duration(self, path_in: Path) -> Optional[float]:
        """Devuelve la duración del archivo de video en segundos usando ffprobe. None si no se puede obtener."""
        try:
            command = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                str(path_in),
            ]
            execution = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            data = json.loads(execution.stdout or "{}")
            duration = float(data.get("format", {}).get("duration", 0) or 0)
            return duration if duration > 0 else None
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            return None

    def _run_ffmpeg_with_progress(
        self,
        command: list,
        duration: Optional[float],
        on_progress: Optional[Callable[[int], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ) -> str:
        """Ejecuta ffmpeg con `-progress pipe:1` y reporta 0-100. Devuelve el stderr completo.

        Args:
            command: Lista de argumentos que forman el comando de ffmpeg (ej: ["ffmpeg", "-i", "video.mp4", ...]).
            duration: Duración del video en segundos, usada para calcular el porcentaje del progreso.
            on_progress: Función callback que recibe un entero 0-100 indicando el progreso.
            is_cancelled: Función callback que devuelve True si el usuario ha cancelado el proceso.
        """
        stderr_lines: list = []

        # Se lanza el proceso de ffmpeg en segundo plano con Popen y se capturan stdout y stderr.
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE, # Captura stdout en vez de enviarlo a la consola para leer el progreso.
                stderr=subprocess.PIPE, # Captura stderr para obtener mensajes de error.
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except FileNotFoundError as e:
            raise RuntimeError("No se encontró ffmpeg/ffprobe. Instálalo y añádelo al PATH.") from e

        """ Lee stderr en un hilo separado para evitar bloqueos si ffmpeg genera muchos mensajes de error.
         Los saca de la tuberia y los guarda en stderr_lines para luego analizarlos si el proceso falla."""
        def _drain_stderr():
            try:
                for line in process.stderr:
                    stderr_lines.append(line)
            except Exception:
                pass

        stderr_thread = threading.Thread(target=_drain_stderr, daemon=True)
        stderr_thread.start()

        try:
            # Lee el progreso linea a linea desde stdout.
            for raw_line in process.stdout:
                # Verifica antes de leer cada linea si el usuario apreto cancelar.
                if is_cancelled and is_cancelled():
                    process.terminate()
                    try:
                        # Cierra el ffmpeg amablemente.
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    raise ProcessingCancelled("Procesado cancelado por el usuario.")
                # Busca la línea que empieza con out_time_ms=, que indica el tiempo de salida en milisegundos.
                line = raw_line.strip()
                if line.startswith("out_time_ms="):
                    try:
                        out_ms = int(line.split("=", 1)[1].strip() or 0)
                    except ValueError:
                        continue
                    # Lo extrae y lo divide por 1_000_000 para pasarlo a segundos.
                    # Lo divide por la duration total del video y lo multiplica por 100 para sacar
                    # un porcentaje de 0 a 100 (pct).
                    if duration and duration > 0 and on_progress:
                        pct = int(max(0, min(100, (out_ms / 1_000_000) / duration * 100)))
                        # Llama al callback on_progress con el porcentaje calculadoa para subir la barra de progreso.
                        on_progress(pct)
                elif line.startswith("progress=end") and on_progress:
                    on_progress(100)
        # Limpieza.
        finally:
            try:
                # Espera a que el proceso termine si no se ha terminado aún.
                process.wait()
            except Exception:
                pass
            # Espera a que el hilo de stderr termine, pero con un timeout para no bloquear indefinidamente.
            stderr_thread.join(timeout=5)
            try:
                if process.stdout:
                    # Cierra stdout para liberar recursos.
                    process.stdout.close()
            except Exception:
                pass
            try:
                if process.stderr:
                    # Cierra stderr para liberar recursos.
                    process.stderr.close()
            except Exception:
                pass

        # Une todas las líneas de stderr en un solo string para analizarlo si ffmpeg falla.
        stderr_text = "".join(stderr_lines)
        if isinstance(process.returncode, int) and process.returncode != 0:
            # Si fue cancelado, el returncode suele ser distinto de 0; prioriza la excepción
            if is_cancelled and is_cancelled():
                raise ProcessingCancelled("Procesado cancelado por el usuario.")
            raise RuntimeError(f"ffmpeg falló (código {process.returncode}):\n{stderr_text[-2000:]}")
        return stderr_text

    def extract_info(
        self,
        movie: tuple[Path, Path],
        on_progress: Optional[Callable[[int], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    )-> dict:
        if movie is None:
            raise ValueError("No se proporcionó una película para extraer información.")
        movie_path_in, movie_path_out = movie
        print("------- Extracting info -------")
        self._validate_targets()
        duration = self.get_duration(movie_path_in)
        command = [
            "ffmpeg",
            "-threads", str(self.extract_threads()),
            "-filter_threads", str(self.extract_threads()),
            "-vn",
            "-i", str(movie_path_in),
            "-af", f"loudnorm=I={self.TARGET_I}:LRA={self.TARGET_LRA}:tp={self.TARGET_TP}:print_format=json",
            "-f", "null", "-",
            "-progress", "pipe:1",
            "-nostats",
        ]

        stderr_text = self._run_ffmpeg_with_progress(
            command, duration, on_progress=on_progress, is_cancelled=is_cancelled
        )

        match = re.search(r"{\s*\"input_i\".*}", stderr_text, re.DOTALL)
        if not match:
            raise RuntimeError("Error: No se pudieron extraer las medidas de audio.")

        metrics = json.loads(match.group(0))
        if on_progress:
            on_progress(100)
        return metrics

    def format_movie(
        self,
        metrics: dict,
        movie: tuple[Path, Path],
        on_progress: Optional[Callable[[int], None]] = None,
        is_cancelled: Optional[Callable[[], bool]] = None,
    ):
        print("------- Formatting movie -------")
        if metrics is None:
            raise ValueError("No se pudo formatear la película debido a errores en la extracción de métricas.")
        self._validate_targets()
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
        duration = self.get_duration(movie_path_in)
        command = [
            "ffmpeg",
            "-y",
            "-threads", str(self.extract_threads()),
            "-filter_threads", str(self.extract_threads()),
            "-i", str(movie_path_in),
            "-af", filters,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            str(movie_path_out),
            "-progress", "pipe:1",
            "-nostats",
        ]

        print("Procesando película... Esto puede tardar unos minutos según la duración.")
        self._run_ffmpeg_with_progress(
            command, duration, on_progress=on_progress, is_cancelled=is_cancelled
        )
        if on_progress:
            on_progress(100)
        print("¡Película procesada con éxito! Archivo de salida:", movie_path_out)

#movie = open_movie_file("movie/movie_ghibli.mp4", "movie/movie_ghibli_output.mp4")
#metrics = extract_info(movie)
#format_movie(metrics, movie)