from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QSlider,
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
        titleLabelI = QLabel("TARGET_I")
        titleLabelI.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layoutControls.addWidget(titleLabelI)

        sliderI = QSlider(Qt.Orientation.Horizontal)
        sliderI.setRange(0, 100)
        sliderI.setValue(0)
        layoutControls.addWidget(sliderI)

        # TARGET_LRA
        titleLabelLRA = QLabel("TARGET_LRA")
        titleLabelLRA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layoutControls.addWidget(titleLabelLRA)

        sliderLRA = QSlider(Qt.Orientation.Horizontal)
        sliderLRA.setRange(0, 100)
        sliderLRA.setValue(0)
        layoutControls.addWidget(sliderLRA)

        # TARGET_TP
        titleLabelTP = QLabel("TARGET_TP")
        titleLabelTP.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layoutControls.addWidget(titleLabelTP)

        sliderTP = QSlider(Qt.Orientation.Horizontal)
        sliderTP.setRange(0, 100)
        sliderTP.setValue(0)
        layoutControls.addWidget(sliderTP)

        self.mainLayout.addLayout(layoutControls)


if __name__ == "__main__":
    app = QApplication([])
    window = Windows()
    window.show()

    app.exec()