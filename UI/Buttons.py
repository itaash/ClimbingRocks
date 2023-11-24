from PyQt5.QtCore import QObject, Qt, QRect, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QColor, QPainter, QPalette
import os, logging,subprocess


class InvisibleButton(QPushButton):
    def __init__(self, doubleClickCallback: callable, parent):
        super().__init__(parent)
        self.setText("")
        self.setGeometry(QRect(25,25,320, 44))  # Set the desired size for the invisible button
        self.setStyleSheet("QPushButton { opacity: 0; border-radius: 0px; background-color: transparent }")
        self.setWindowFlags(Qt.WindowStaysOnTopHint| Qt.FramelessWindowHint )  # Make the widget transparent and always on top
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_NoSystemBackground)
        # self.setWindowOpacity(0.0)
        self.doubleClickTimer = QTimer()
        self.doubleClickTimer.setSingleShot(True)
        self.doubleClickTimer.timeout.connect(self.handleSingleClick)
        self.isDoubleClick = False
        self.setText("")
        self.doubleClickCallback = doubleClickCallback

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.doubleClickTimer.start(QApplication.doubleClickInterval())

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.doubleClickTimer.stop()
            self.isDoubleClick = True
            self.handleDoubleClick()

    def handleSingleClick(self):
        if not self.isDoubleClick:
            self.isDoubleClick = False
            logging.info("hidden click")
            # Handle single click event if needed

    def handleDoubleClick(self):
        self.isDoubleClick = False
        logging.info("hidden double click")

        dialog = ShutdownDialog(self.parent())
        dialog.exec_()
        # alternatively, quit app
        # parent.stopEsxecution()
        # self.doubleClickCallback()


class StartButton(QPushButton):
    def __init__(self, callback: callable, parent=None):
        super().__init__("", parent)
        self.clicked.connect(callback)
        self.setFixedSize(200, 200)
        self.setStyleSheet("QPushButton { background-image: url(UI/UIAssets/StartButton.png); }")
        self.setWindowFlags(Qt.WindowStaysOnTopHint| Qt.FramelessWindowHint )  # Make the widget transparent and always on top
        


class StopButton(QPushButton):
    def __init__(self, callback: callable, parent=None):
        super().__init__("", parent)
        self.clicked.connect(callback)
        self.setFixedSize(88, 88)
        self.setStyleSheet("QPushButton { border-radius: 44px; background-image: url(ui_sources/dark/stop_button.png); }")
        

class ShutdownDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowFlags(Qt.FramelessWindowHint | Qt.Dialog))
        
        
        self.setWindowTitle("Shutdown Menu")
        self.setStyleSheet("Qdialog {background-color: #2B2B2B; color: #FFFFFF; border-radius: 20px;}")
        self.setFixedSize(235, 340)
        layout = QVBoxLayout(self)
        layout.addSpacing(15)

        # Title label
        titleLabel = QLabel("Shutdown Menu", self)
        titleLabel.setStyleSheet("font-family: DM Sans; font-size: 24px; font-weight: bold;")
        layout.addWidget(titleLabel, alignment=Qt.AlignHCenter)
        layout.addSpacing(25)

        # Button layout
        buttonLayout = QVBoxLayout()
        buttonLayout.setSpacing(15)


        # Shutdown button
        shutdown_button = QPushButton("Shutdown", self)
        shutdown_button.setStyleSheet(
            "QPushButton { width: 115; background-color: #F2994A; color: white; font-family: DM Sans; font-size: 20px; font-weight: bold; border-radius: 9px; padding: 9px; }"
            "QPushButton:hover { background-color: #F26B4A; }"
        )
        shutdown_button.clicked.connect(self.shutdown)
        buttonLayout.addWidget(shutdown_button, alignment=Qt.AlignHCenter)

        # Restart button
        restart_button = QPushButton("Restart", self)
        restart_button.setStyleSheet(
            "QPushButton { width: 115; background-color: #2980B9; color: white; font-family: DM Sans; font-size: 20px; font-weight: bold; border-radius: 9px; padding: 9px; }"
            "QPushButton:hover { background-color: #2D9CDB; }"
        )
        restart_button.clicked.connect(self.restart)
        buttonLayout.addWidget(restart_button, alignment=Qt.AlignHCenter)

        # Cancel button
        cancel_button = QPushButton("Cancel", self)
        cancel_button.setStyleSheet(
            "QPushButton { width: 115; background-color: #EB5757; color: white; font-family: DM Sans; font-size: 20px; font-weight: bold; border-radius: 9px; padding: 9px; }"
            "QPushButton:hover { background-color: #B03A3A; }"
        )
        cancel_button.clicked.connect(self.cancel)
        buttonLayout.addWidget(cancel_button, alignment=Qt.AlignHCenter)

        # Add button layout to the main layout
        layout.addLayout(buttonLayout)
        layout.addSpacing(30)

        # if parent:
        #    self.move(parent.geometry().center() - self.rect().center())

        logging.info("Shutdown Menu displayed")


    def shutdown(self):
        os.system("sudo shutdown now")

    def restart(self):
        os.system("sudo reboot")

    def cancel(self):
        self.close()


class CameraUnpluggedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowFlags(Qt.FramelessWindowHint | Qt.Dialog))
        self.setWindowTitle("Camera Unplugged")
        self.setStyleSheet("Qdialog {background-color: #2B2B2B; color: #FFFFFF;}")

        self.layout = QVBoxLayout(self)

        label = QLabel("<font color='#E30E0E'>Error: </font>Camera Disconnected<br><br>Please check the connection.<br>App will close soon if not reconnected.", self)
        label.setStyleSheet("font-weight: bold; font-size: 22px; font-family: DM Sans;")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label, alignment=Qt.AlignCenter)

        # Adjust the size of the dialog
        self.setMinimumWidth(400)
        self.setMinimumHeight(120)

        # Center the dialog on the parent window
        if parent:
            self.move(parent.geometry().center() - self.rect().center())

        # Set a timer to automatically close the dialog after a few seconds
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)

    def showEvent(self, event):
        super().showEvent(event)
        # Start the timer when the dialog is shown
        self.timer.start(5000)  # 5000 milliseconds = 5 seconds

    def hideEvent(self, event):
        super().hideEvent(event)
        # Stop the timer when the dialog is hidden
        self.timer.stop()