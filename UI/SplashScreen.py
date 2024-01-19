
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize
import os



class SplashScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        # Set window properties

        # Create logo label
        splashImage = QPixmap("UI/UIAssets/logo.png")
        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignHCenter)
        self.imageLabel.setPixmap(splashImage.scaled(QSize(int(parent.width()*0.6), int(parent.height()*0.6)), Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation))

        # Create progress bar
        self._progressBar = QProgressBar(self)
        self._progressBar.setMaximum(100)
        self._progressBar.setMinimum(0)
        self._progressBar.setTextVisible(False)
        self._progressBar.setStyleSheet(
            "QProgressBar { border: none; background-color: #F2F2F2; height: 10px; border-radius: 10px; }"
            "QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00FF94, stop:1 #00BD81); border-radius: 10px; }")
        self._progressBar.setFixedWidth(int(parent.width()*0.65))
        self._progressBar.setFixedHeight(20)
        self._progressBar.setAlignment(Qt.AlignHCenter)
        self._progressBar.setValue(30)

        # Create text label
        self.splashText = QLabel(self)
        self.splashText.setStyleSheet("font-family: DM Sans; font-size: 19px; font-weight: 400; line-height: 24px; color: #404040; ")
        self.splashText.setAlignment(Qt.AlignHCenter)
        self.splashText.setText("")
        self.splashText.setFixedWidth(int(parent.width()*0.65))

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addSpacing(80)
        layout.addWidget(self.imageLabel)
        layout.addSpacing(70)
        layout.addWidget(self._progressBar)
        layout.addSpacing(40)
        layout.addWidget(self.splashText)
        layout.addStretch(1)
        self.setLayout(layout)

    def getProgress(self):
        return self._progressBar.value()
    
    def setProgress(self, value: int):
        self._progressBar.setValue(value)

    def setError(self, message: str):
        self.splashText.setText("<font color='red'>Error: </font>" + message)
        self._progressBar.setStyleSheet("QProgressBar { border: none; background-color: #BFBFBF; height: 20px; border-radius: 10px; }"
                                       "QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B81F1F, stop:1 #FF4E4E); border-radius: 10px; }")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Climbing Rocks")
    window.setStyleSheet("background-color: #222222; font-size: 20px; color: #ffffff;")
    window.setFixedSize(1280, 800)
    
    splashScreen = SplashScreen(window)
    window.setCentralWidget(splashScreen)
    window.show()
    
    sys.exit(app.exec_())