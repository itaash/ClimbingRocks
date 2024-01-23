from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QRect
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QSpacerItem, QFrame




class ResultsScreen:
    def __init__(self, parent):
        self.parent = parent

    