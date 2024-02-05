from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QRect
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy, QSpacerItem, QFrame


from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

class ResultsScreen(QWidget):
    def __init__(self, climberName, climbSuccessful, parent=None):
        super(ResultsScreen, self).__init__(parent)

        # Set up the layout
        self.mainLayout = QVBoxLayout(self)

        # Add white space on the top
        self.mainLayout.addSpacing(20)

        #intro text
        self.climbFinishedLabel = QLabel()
        self.climbFinishedLabel.setStyleSheet("font-size: 30px; color: #ffffff; font-weight: bold; font-family: 'DM Sans';")
        self.climbFinishedLabel.setText(f"Climb finished, {climberName}, we're analysing your climb")

        self.climbSuccessful = climbSuccessful
        self.climberName = climberName

        # Create the central hbox layout with three widgets
        hboxLayout = QHBoxLayout()
        hboxLayout.setSpacing(30)
        hboxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pressureWidget = MetricWidget("Pressure", "UI/UIAssets/loading.gif", self)
        positioningWidget = MetricWidget("Positioning", "UI/UIAssets/loading.gif", self)
        progressWidget = MetricWidget("Progress", "UI/UIAssets/loading.gif", self)
        hboxLayout.addWidget(pressureWidget)
        hboxLayout.addWidget(positioningWidget)
        hboxLayout.addWidget(progressWidget)
        self.mainLayout.addLayout(hboxLayout)

        # Add more white space on the bottom
        self.mainLayout.addSpacing(20)

        # Create the "Click to see Climbing tip" button
        self.tipButton = QPushButton("Click to see Climbing tip", self)
        self.tipButton.setGeometry(self.width() - 45 - self.tip_button.width(), self.height() - 45 - self.tip_button.height(), self.tip_button.width(), self.tip_button.height())
        self.tipButton.clicked.connect(self.goToTip)
        self.mainLayout.addWidget(self.tip_button, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Create and start a 20-second timer
        self.timer = QTimer(self)
        self.timer.timeout.connect()
        self.timer.start(20000)  # 20 seconds in milliseconds

        # start a 0 second timer to start climbing analysis, connect the signal from the climbanalyser to update the metrics
        self.startTimer = QTimer(self)
        self.startTimer.timeout.connect(self.startClimbAnalysis)
        self.startTimer.start(0)

    def startClimbAnalysis(self):
        self.climbAnalyser = ClimbAnalyserThread(self.climberName, self)
        self.climbAnalyser.ClimbAnalysisComplete.connect(self.updateMetrics)
        self.climbAnalyser.start()

    @pyqtSlot()
    def updateMetrics(self):

        if self.climbSuccessful:
            self.climbFinishedLabel.setText(f"Congratulations, {self.climberName}, here's how you did")
        else:
            self.climbFinishedLabel.setText(f"Skill issue, {self.climberName}, here's an analysis of your lame attempt")

        pressureSubmetrics = self.climbAnalyser.getPressureSubmetrics()
        pressureVisualisation = self.climbAnalyser.getPressureVisualisation()

        positioningSubmetrics = self.climbAnalyser.getPositioningSubmetrics()
        positioningVisualisation = self.climbAnalyser.getPositioningVisualisation()

        progressSubmetrics = self.climbAnalyser.getProgressSubmetrics()
        progressVisualisation = self.climbAnalyser.getProgressVisualisation()



class MetricWidget(QWidget):
    def __init__(self, metric, image, score=0, parent=None):
        super(MetricWidget, self).__init__(parent)

        # Set up the layout
        layout = QVBoxLayout(self)

        # Create the label and value widgets
        labelLayout= QHBoxLayout()
        labelLogo = QLabel(self)
        labelLogo.setPixmap(QPixmap(f"UI/UIAssets/{metric}Logo.png").scaledToWidth(30, Qt.AspectRatioMode.KeepAspectRatio))
        labelText = QLabel(metric, self)
        labelText.setStyleSheet("font-size: 20px; color: #cccccc; font-weight: bold; font-family: 'DM Sans'; text-align: left;")
        labelText.setFixedWidth(100)

        labelScore = QLabel(self)
        labelScore.setFixedWidth(30)
        labelScore.setText(str(score))
        labelScore.setStyleSheet("font-size: 20px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; text-align: right;")
        
        labelLayout.addWidget(labelLogo)
        labelLayout.addSpacing(10)
        labelLayout.addWidget(labelText)
        labelLayout.addWidget(labelScore)

        layout.addLayout(labelLayout)

        # add the image
        image = QLabel(self)
        image.setPixmap(QPixmap(image).scaledToWidth(300, Qt.AspectRatioMode.KeepAspectRatio))

        # Add a stretch to push the widgets to the top of the layout
        layout.addStretch()

        # Set the layout for the widget
        self.setLayout(layout)

    # Add any additional methods or signals as needed
        
        def updateImage(self, image):
            self.image.setPixmap(QPixmap(image).scaledToWidth(300, Qt.AspectRatioMode.KeepAspectRatio))
            self.image.update()

        def updateScore(self, score):
            self.labelScore.setText(str(score))
            self.labelScore.update()


if __name__ == "__main__":
    import sys, os
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtGui import QFontDatabase
    
    sys.path.append(os. getcwd())
    
    from error import FontError


    if (QFontDatabase.addApplicationFont("UI/UIAssets/DMSans.ttf") == -1):
        raise FontError("Could not load font")

    if (QFontDatabase.addApplicationFont("UI/UIAssets/Bungee.ttf") == -1):
        raise FontError("Could not load font")



    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setFixedSize(1280, 800)
    window.setFont(QFont("DM Sans"))
    window.setStyleSheet("background-color: #222222; font-size: 20px; color: #ffffff;")
    
    window.resultsScreen = ResultsScreen("John Doe", False, window)
    window.setCentralWidget(window.resultsScreen)
    
    
    window.show()
    sys.exit(app.exec_())
else:
    from AnalyseClimb.ClimbAnalyser import ClimbAnalyserThread
    