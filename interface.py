from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QDialogButtonBox,
    QPushButton
)

class Windows(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Configure video sound")
        self.setFixedSize(500, 300)

        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)

        self.mainLayout = QVBoxLayout(self.mainWidget)

        # Init app
        self.get_menu()
        self.get_controls()


    def get_menu(self):
        pass

    def get_controls(self):
        layoutControls = QVBoxLayout()

        # TARGET_I
        titleLabelI = QLabel("Nivel Sonoro Promedio")
        titleLabelI.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sliderI = QSlider(Qt.Orientation.Horizontal)
        sliderI.setRange(-26, -14)
        sliderI.setValue(-16)

        valueLabelI = QLabel(f"{sliderI.value()} LUFS")
        valueLabelI.setFixedWidth(70)
        sliderI.valueChanged.connect(lambda val: valueLabelI.setText(f"{val} LUFS"))

        layoutControlsValueI = QHBoxLayout()

        layoutControls.addWidget(titleLabelI)
        layoutControlsValueI.addWidget(sliderI)
        layoutControlsValueI.addWidget(valueLabelI)
        layoutControls.addLayout(layoutControlsValueI)

        # TARGET_LRA
        titleLabelLRA = QLabel("Rango Sonoro")
        titleLabelLRA.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sliderLRA = QSlider(Qt.Orientation.Horizontal)
        sliderLRA.setRange(4, 15)
        sliderLRA.setValue(8)

        valueLabelLRA = QLabel(f"{sliderLRA.value()} LU")
        valueLabelLRA.setFixedWidth(70)
        sliderLRA.valueChanged.connect(lambda val: valueLabelLRA.setText(f"{val} LU"))

        layoutControlsValueLRA = QHBoxLayout()

        layoutControls.addWidget(titleLabelLRA)
        layoutControlsValueLRA.addWidget(sliderLRA)
        layoutControlsValueLRA.addWidget(valueLabelLRA)
        layoutControls.addLayout(layoutControlsValueLRA)

        # TARGET_TP
        titleLabelTP = QLabel("Picos Sonoros")
        titleLabelTP.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sliderTP = QSlider(Qt.Orientation.Horizontal)
        sliderTP.setRange(-30, -5)
        sliderTP.setValue(-15)

        valueLabelTP = QLabel(f"{sliderTP.value()} dB")
        valueLabelTP.setFixedWidth(70)
        sliderTP.valueChanged.connect(lambda val: valueLabelTP.setText(f"{val} dB"))

        layoutControlsValueTP = QHBoxLayout()

        layoutControls.addWidget(titleLabelTP)
        layoutControlsValueTP.addWidget(sliderTP)
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