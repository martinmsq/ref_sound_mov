from main import MovieProcessor, ProcessingCancelled
from pathlib import Path
from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QProgressBar
)


class ProcessorWorker(QObject):
    """Ejecuta extract_info + format_movie en segundo plano con progreso real."""

    progress_extract = Signal(int)
    progress_format = Signal(int)
    status = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, processor: MovieProcessor, path_in: str, path_out: str,
                 target_i: int, target_lra: int, target_tp: float):
        super().__init__()
        self.processor = processor
        self.path_in = path_in
        self.path_out = path_out
        self.target_i = target_i
        self.target_lra = target_lra
        self.target_tp = target_tp

    def _is_cancelled(self) -> bool:
        thread = QThread.currentThread()
        return thread is not None and thread.isInterruptionRequested()

    @Slot()
    def run(self):
        try:
            self.processor.TARGET_I = self.target_i
            self.processor.TARGET_LRA = self.target_lra
            self.processor.TARGET_TP = self.target_tp

            self.status.emit("Abriendo archivo...")
            movie = self.processor.open_movie_file(self.path_in, self.path_out)

            self.status.emit("Analizando audio (1/2)...")
            self.progress_extract.emit(0)
            metrics = self.processor.extract_info(
                movie,
                on_progress=self.progress_extract.emit,
                is_cancelled=self._is_cancelled,
            )

            self.status.emit("Normalizando audio y generando video (2/2)...")
            self.progress_format.emit(0)
            self.processor.format_movie(
                metrics,
                movie,
                on_progress=self.progress_format.emit,
                is_cancelled=self._is_cancelled,
            )

            self.status.emit("Completado.")
            self.finished.emit(self.path_out)
        except ProcessingCancelled:
            self.status.emit("Cancelado por el usuario.")
            self.error.emit("Procesado cancelado por el usuario.")
        except Exception as e:  # noqa: BLE001 - se muestra al usuario
            self.status.emit("Error durante el procesado.")
            self.error.emit(str(e))


class Windows(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Configure video sound")
        self.setFixedSize(600, 560)

        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QVBoxLayout(self.mainWidget)

        # Path file
        self.pathIn = None
        self.pathOut = None

        # Controls
        self.sliderI = None
        self.sliderLRA = None
        self.sliderTP = None

        # Progress bars (una por cada parte del procesamiento)
        self.extractBar = None
        self.formatBar = None
        self.statusLabel = None

        # Worker thread
        self.thread = None
        self.worker = None

        # Start buttons
        self.startBtn = QPushButton("Iniciar")
        self.cancelBtn = QPushButton("Cancelar")

        # Init class processor
        self.processor = MovieProcessor()

        # Init app
        self.open_file_widget()
        self.get_menu_widget()
        self.get_controls_widget()
        self.get_progress_widget()


    def build_output_path(self, path_in: str, suffix: str= "_convert") -> str:
        path = Path(path_in)
        path_out = path.with_name(f"{path.stem}{suffix}{path.suffix}")
        if not path_out.exists():
            return str(path_out)

        for i in range(1, 10):
            path_out = path.with_name(f"{path.stem}{suffix}_{i}{path.suffix}")
            if not path_out.exists():
                return str(path_out)
        raise FileExistsError("No se pudo generar un nombre de archivo de salida único.")


    def load_file(self):
        self.pathIn, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de video", "", "Video (*.mp4 *.mkv *.avi)")
        if not self.pathIn:
            QMessageBox.critical(self, "Error", "No se seleccionó ningún archivo de video.")
            return
        try:
            self.startBtn.setEnabled(True)
            self.pathOut = self.build_output_path(self.pathIn)
            self.processor.open_movie_file(self.pathIn, self.pathOut)  # Call the open_movie_file method from MovieProcessor
        except FileExistsError as e:
            QMessageBox.critical(self, "Error", str(e))
            return

    def open_file_widget(self):
        searchButton = QPushButton("Seleccionar archivo de video")
        searchButton.clicked.connect(self.load_file)

        self.mainLayout.addWidget(searchButton)

    def apply_option(self, option_name, options):
        value = options.get(option_name)
        if value is None:
            return
        self.sliderI.setValue(int(value["target_i"]))
        self.sliderLRA.setValue(int(value["target_lra"]))
        self.sliderTP.setValue(int(round(float(value["target_tp"]) * 10)))

    def get_menu_widget(self):
        options = {
            "TV / Living": {"target_i": -16, "target_lra": 11, "target_tp": -1.5},
            "Auriculares": {"target_i": -16, "target_lra": 7, "target_tp": -2.0},
            "Home Cinema": {"target_i": -14, "target_lra": 9, "target_tp": -2.0}
        }
        titleMenu = QLabel("Predefinidos")
        comboMenu = QComboBox()
        comboMenu.addItems(list(options.keys()))

        comboMenu.currentTextChanged.connect(lambda option: self.apply_option(option, options))

        self.mainLayout.addWidget(titleMenu)
        self.mainLayout.addWidget(comboMenu)

    def get_controls_widget(self, target_i=-16, target_lra=8, target_tp=-1.5):
        layoutControls = QVBoxLayout()

        # TARGET_I
        titleLabelI = QLabel("Nivel Sonoro Promedio")
        titleLabelI.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sliderI = QSlider(Qt.Orientation.Horizontal)
        self.sliderI.setRange(-26, -14)
        self.sliderI.setValue(target_i)

        valueLabelI = QLabel(f"{self.sliderI.value()} LUFS")
        valueLabelI.setFixedWidth(70)
        self.sliderI.valueChanged.connect(lambda val: valueLabelI.setText(f"{val} LUFS"))

        layoutControlsValueI = QHBoxLayout()

        layoutControls.addWidget(titleLabelI)
        layoutControlsValueI.addWidget(self.sliderI)
        layoutControlsValueI.addWidget(valueLabelI)
        layoutControls.addLayout(layoutControlsValueI)

        # TARGET_LRA
        titleLabelLRA = QLabel("Rango Sonoro")
        titleLabelLRA.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sliderLRA = QSlider(Qt.Orientation.Horizontal)
        self.sliderLRA.setRange(4, 15)
        self.sliderLRA.setValue(target_lra)

        valueLabelLRA = QLabel(f"{self.sliderLRA.value()} LU")
        valueLabelLRA.setFixedWidth(70)
        self.sliderLRA.valueChanged.connect(lambda val: valueLabelLRA.setText(f"{val} LU"))

        layoutControlsValueLRA = QHBoxLayout()

        layoutControls.addWidget(titleLabelLRA)
        layoutControlsValueLRA.addWidget(self.sliderLRA)
        layoutControlsValueLRA.addWidget(valueLabelLRA)
        layoutControls.addLayout(layoutControlsValueLRA)

        # TARGET_TP (ffmpeg loudnorm: -9.0 a 0.0 dB, slider en décimas: -90 a 0)
        titleLabelTP = QLabel("Picos Sonoros")
        titleLabelTP.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sliderTP = QSlider(Qt.Orientation.Horizontal)
        self.sliderTP.setRange(-90, 0)
        self.sliderTP.setValue(int(round(float(target_tp) * 10)))

        valueLabelTP = QLabel(f"{self.sliderTP.value() / 10:.1f} dB")
        valueLabelTP.setFixedWidth(70)
        self.sliderTP.valueChanged.connect(lambda val: valueLabelTP.setText(f"{val / 10:.1f} dB"))

        layoutControlsValueTP = QHBoxLayout()

        layoutControls.addWidget(titleLabelTP)
        layoutControlsValueTP.addWidget(self.sliderTP)
        layoutControlsValueTP.addWidget(valueLabelTP)
        layoutControls.addLayout(layoutControlsValueTP)

        layoutControlsButtons = QHBoxLayout()

        self.cancelBtn.clicked.connect(self.handle_cancel)
        self.startBtn.clicked.connect(self.start_processing)
        self.startBtn.setEnabled(self.pathIn is not None)

        layoutControlsButtons.addWidget(self.cancelBtn)
        layoutControlsButtons.addWidget(self.startBtn)
        layoutControls.addLayout(layoutControlsButtons)

        self.mainLayout.addLayout(layoutControls)

    def get_progress_widget(self):
        """Barra de progreso para cada parte: análisis (extract_info) y formateo (format_movie)."""
        layoutProgress = QVBoxLayout()

        self.statusLabel = QLabel("Listo. Selecciona un video para empezar.")
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layoutProgress.addWidget(self.statusLabel)

        labelExtract = QLabel("Análisis de audio (extract_info)")
        labelExtract.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.extractBar = QProgressBar()
        self.extractBar.setRange(0, 100)
        self.extractBar.setValue(0)
        self.extractBar.setFormat("Análisis: %p%")
        layoutProgress.addWidget(labelExtract)
        layoutProgress.addWidget(self.extractBar)

        labelFormat = QLabel("Normalizado y exportación (format_movie)")
        labelFormat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formatBar = QProgressBar()
        self.formatBar.setRange(0, 100)
        self.formatBar.setValue(0)
        self.formatBar.setFormat("Formateo: %p%")
        layoutProgress.addWidget(labelFormat)
        layoutProgress.addWidget(self.formatBar)

        self.mainLayout.addLayout(layoutProgress)

    def start_processing(self):
        """Implementa extract_info + format_movie de main.py en segundo plano."""
        if not self.pathIn:
            QMessageBox.critical(self, "Error", "Primero selecciona un archivo de video.")
            return
        if self.thread is not None and self.thread.isRunning():
            QMessageBox.information(self, "En curso", "Ya hay un procesado en curso.")
            return
        try:
            self.pathOut = self.build_output_path(self.pathIn)
        except FileExistsError as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        target_i = self.sliderI.value()
        target_lra = self.sliderLRA.value()
        target_tp = self.sliderTP.value() / 10.0

        self.extractBar.setValue(0)
        self.formatBar.setValue(0)
        self.startBtn.setEnabled(False)

        self.thread = QThread(self)
        self.worker = ProcessorWorker(
            self.processor, self.pathIn, self.pathOut, target_i, target_lra, target_tp
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress_extract.connect(self.extractBar.setValue)
        self.worker.progress_format.connect(self.formatBar.setValue)
        self.worker.status.connect(self.statusLabel.setText)
        self.worker.finished.connect(self._on_processing_finished)
        self.worker.error.connect(self._on_processing_error)
        # Limpieza en ambos casos
        self.worker.finished.connect(self._cleanup_thread)
        self.worker.error.connect(self._cleanup_thread)

        self.thread.start()

    @Slot(str)
    def _on_processing_finished(self, path_out: str):
        self.startBtn.setEnabled(True)
        QMessageBox.information(self, "Éxito", f"¡Película procesada con éxito!\nArchivo: {path_out}")

    @Slot(str)
    def _on_processing_error(self, message: str):
        self.startBtn.setEnabled(True)
        if "cancelado" in message.lower():
            QMessageBox.information(self, "Cancelado", message)
        else:
            QMessageBox.critical(self, "Error", message)

    @Slot()
    def _cleanup_thread(self):
        if self.thread is not None:
            self.thread.quit()
            self.thread.wait()
            self.thread.deleteLater()
            self.thread = None
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None

    def handle_cancel(self):
        """Cancela el procesado en curso o cierra la ventana si no hay nada corriendo."""
        if self.thread is not None and self.thread.isRunning():
            self.statusLabel.setText("Cancelando...")
            self.thread.requestInterruption()
        else:
            self.close()

    def closeEvent(self, event):
        if self.thread is not None and self.thread.isRunning():
            self.thread.requestInterruption()
            self.thread.quit()
            self.thread.wait(3000)
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    window = Windows()
    window.show()

    app.exec()