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
    QComboBox
)

class Windows(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Configure video sound")
        self.setFixedSize(500, 300)

        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QVBoxLayout(self.mainWidget)

        # Controls
        self.sliderI = None
        self.sliderLRA = None
        self.sliderTP = None

        # Init app
        self.get_menu()
        self.get_controls()


    def get_menu(self):
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

    def apply_option(self, option_name, options):
        value = options.get(option_name)
        if value is None:
            return
        self.sliderI.setValue(value["target_i"])
        self.sliderLRA.setValue(value["target_lra"])
        self.sliderTP.setValue(value["target_tp"])

    def get_controls(self, target_i=-16, target_lra=8, target_tp=-15):
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

        cancelBtn = QPushButton("Cancelar")
        startBtn = QPushButton("Iniciar")
        layoutControlsButtons.addWidget(cancelBtn)
        layoutControlsButtons.addWidget(startBtn)
        layoutControls.addLayout(layoutControlsButtons)


        self.mainLayout.addLayout(layoutControls)


if __name__ == "__main__":
    app = QApplication([])
    window = Windows()
    window.show()

    app.exec()