from main import MovieProcessor
from pathlib import Path
from PySide6.QtCore import Qt
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
    QMessageBox
)


class Windows(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Configure video sound")
        self.setFixedSize(600, 400)

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

        # Start buttons
        self.startBtn = QPushButton("Iniciar")
        self.cancelBtn = QPushButton("Cancelar")

        # Init class processor
        self.processor = MovieProcessor()

        # Init app
        self.open_file_widget()
        self.get_menu_widget()
        self.get_controls_widget()


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
        self.sliderI.setValue(value["target_i"])
        self.sliderLRA.setValue(value["target_lra"])
        self.sliderTP.setValue(value["target_tp"])

    def get_menu_widget(self):
        options = {
            "TV / Living": {"target_i": -16, "target_lra": 8, "target_tp": -15},
            "Auriculares": {"target_i": -20, "target_lra": 12, "target_tp": -10},
            "Home Cinema": {"target_i": -14, "target_lra": 9, "target_tp": -12}
        }
        titleMenu = QLabel("Predefinidos")
        comboMenu = QComboBox()
        comboMenu.addItems(list(options.keys()))

        comboMenu.currentTextChanged.connect(lambda option: self.apply_option(option, options))

        self.mainLayout.addWidget(titleMenu)
        self.mainLayout.addWidget(comboMenu)

    def get_controls_widget(self, target_i=-16, target_lra=8, target_tp=-15):
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

        # TARGET_TP
        titleLabelTP = QLabel("Picos Sonoros")
        titleLabelTP.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sliderTP = QSlider(Qt.Orientation.Horizontal)
        self.sliderTP.setRange(-30, -5)
        self.sliderTP.setValue(target_tp)

        valueLabelTP = QLabel(f"{self.sliderTP.value()} dB")
        valueLabelTP.setFixedWidth(70)
        self.sliderTP.valueChanged.connect(lambda val: valueLabelTP.setText(f"{val} dB"))

        layoutControlsValueTP = QHBoxLayout()

        layoutControls.addWidget(titleLabelTP)
        layoutControlsValueTP.addWidget(self.sliderTP)
        layoutControlsValueTP.addWidget(valueLabelTP)
        layoutControls.addLayout(layoutControlsValueTP)

        layoutControlsButtons = QHBoxLayout()

        self.cancelBtn.clicked.connect(self.close)
        self.startBtn.setEnabled(self.pathIn is not None)

        #TODO: Agregar las funciones para extraer la informacion y formatear de main.py.

        layoutControlsButtons.addWidget(self.cancelBtn)
        layoutControlsButtons.addWidget(self.startBtn)
        layoutControls.addLayout(layoutControlsButtons)

        self.mainLayout.addLayout(layoutControls)


if __name__ == "__main__":
    app = QApplication([])
    window = Windows()
    window.show()

    app.exec()