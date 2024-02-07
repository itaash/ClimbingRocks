from PyQt5.QtCore import pyqtSlot, QTimer, Qt
from PyQt5.QtGui import QFont, QPixmap, QImage, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect


class ResultsScreen(QWidget):
    def __init__(self, climberName, climbSuccessful, parent=None):
        super(ResultsScreen, self).__init__(parent)

        # Set up the layout
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        # Add white space on the top
        self.mainLayout.addSpacing(20)

        #intro text
        self.climbFinishedLabel = QLabel()
        self.climbFinishedLabel.setStyleSheet("font-size: 30px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; padding: 30px; text-align: left;")
        self.climbFinishedLabel.setText(f"Climb finished, {climberName}, we're analysing your climb now...")


        self.climbSuccessful = climbSuccessful
        self.climberName = climberName

        self.mainLayout.addWidget(self.climbFinishedLabel, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Add space
        self.mainLayout.addSpacing(30)

        # Create the central hbox layout with three widgets
        hboxLayout = QHBoxLayout()
        hboxLayout.setSpacing(50)
        hboxLayout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.pressureWidget = MetricWidget("Pressure", "UI/UIAssets/loading.gif", colour='#A951F6', parent=self)
        self.positioningWidget = MetricWidget("Positioning", "UI/UIAssets/loading.gif", colour='#3EE2F4', parent=self)
        self.progressWidget = MetricWidget("Progress", "UI/UIAssets/loading.gif", colour='#DB5764', parent=self)
        hboxLayout.addWidget(self.pressureWidget)
        hboxLayout.addWidget(self.positioningWidget)
        hboxLayout.addWidget(self.progressWidget)
        self.mainLayout.addLayout(hboxLayout)

        # Add more white space on the bottom
        self.mainLayout.addSpacing(100)

        # Create the "Click to see Climbing tip" button
        self.tipButton = QPushButton("Click to see \nClimbing tip", self)
        self.tipButton.setStyleSheet("font-size: 20px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: #c58af9; border: none; padding: 10px 20px; border-radius: 10px;")
        self.tipButton.setFixedSize(200, 100)
        self.tipButton.move(parent.width() - self.tipButton.width() - 60, parent.height() - self.tipButton.height() - 60)
        self.tipButton.clicked.connect(self.goToTip)

        # Create and start a 20-second timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.goToTip)
        self.timer.start(20000)  # 20 seconds in milliseconds

        # start a 0 second timer to start climbing analysis, connect the signal from the climbanalyser to update the metrics
        self.startTimer = QTimer(self)
        self.startTimer.timeout.connect(self.startClimbAnalysis)
        self.startTimer.start(10000)

    def startClimbAnalysis(self):
        self.climbAnalyser = ClimbAnalyserThread(self.climberName, self)
        self.climbAnalyser.ClimbAnalysisComplete.connect(self.updateMetrics)
        self.climbAnalyser.start()

    def goToTip(self):
        # TODO: Implement the goToTip method to display a climbing tip
        print("Going to tip")
        pass

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

        self.pressureWidget.updateImage(pressureVisualisation)
        self.pressureWidget.updateScore(pressureSubmetrics[0])

        self.progressWidget.updateImage(progressVisualisation)
        self.progressWidget.updateScore(progressSubmetrics[0])

        self.positioningWidget.updateImage(positioningVisualisation)
        self.positioningWidget.updateScore(positioningSubmetrics[0])


class MetricWidget(QWidget):
    def __init__(self, metric, image, score=100, colour = '#C58AF9', parent=None):
        super(MetricWidget, self).__init__(parent)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Create the label and value widgets
        labelLayout= QHBoxLayout()
        labelLayout.setAlignment(Qt.AlignCenter)
        labelLogo = QLabel(self)
        labelLogo.setPixmap(QPixmap(f"UI/UIAssets/{metric}Icon.png").scaledToWidth(40, Qt.SmoothTransformation))
        # labelLogo.setPixmap(QPixmap(f"UI/UIAssets/logo.png").scaledToWidth(40, Qt.SmoothTransformation))
        labelText = QLabel(metric, self)
        labelText.setStyleSheet("font-size: 24px; color: #222222; font-weight: bold; font-family: 'DM Sans'; text-align: left;")
        labelText.setFixedWidth(140)
        labelText.setFixedHeight(40)

        self.scoreLabel = QLabel(str(score))
        self.scoreLabel.setFixedWidth(60)
        self.scoreLabel.setStyleSheet("font-size: 28px; color: #222222; font-family: 'DM Sans'; text-align: right; font-weight: bold;")
        
        labelLayout.addWidget(labelLogo)
        labelLayout.addSpacing(10)
        labelLayout.addWidget(labelText)
        labelLayout.addSpacing(10)
        labelLayout.addWidget(self.scoreLabel)

        layout.addSpacing(20)
        layout.addLayout(labelLayout)
        layout.addSpacing(20)

        # add the image
        self.image = QLabel()
        self.image.setStyleSheet("background-color: #ffffff; border-radius: 15%")
        self.image.setPixmap(QPixmap(image).scaledToHeight(270, Qt.SmoothTransformation))
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(20)

        # Set the layout for the widget
        self.setLayout(layout)
        self.setFixedSize(350, 450)

        # Set the style for the widget - a rounded rectangle with a shadow
        metricWrapper = QWidget(self)
        metricWrapper.setStyleSheet(f"border-radius: 15px; background-color: {colour}; ")
        metricWrapper.setLayout(self.layout())
        metricWrapper.setFixedWidth(self.width())
        # metricWrapper.setFixedHeight(self.height())


        # Create shadow effect for metricWrapper
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setBlurRadius(15)
        shadowEffect.setColor(QColor(colour))
        shadowEffect.setOffset(0, 0)

        # metricWrapper.setGraphicsEffect(shadowEffect)
        
        
    def updateImage(self, image):
        """
        update the image in the widget

        Args:
            image (numpy array): the image to be displayed
        """
        #decode the image
        imagePixmap = QPixmap.fromImage(QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888))
        self.image.setPixmap(imagePixmap.scaledToHeight(200, Qt.SmoothTransformation))

    def updateScore(self, score):
        self.scoreLabel.setText(str(score))


if __name__ == "__main__":
    import sys, os
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtGui import QFontDatabase
    
    sys.path.append(os.getcwd())
    
    from error import FontError
    from AnalyseClimb.ClimbAnalyser import ClimbAnalyserThread

    app = QApplication(sys.argv)

    if (QFontDatabase.addApplicationFont("UI/UIAssets/DMSans.ttf") == -1):
        raise FontError("Could not load font")

    if (QFontDatabase.addApplicationFont("UI/UIAssets/Bungee.ttf") == -1):
        raise FontError("Could not load font")

    window = QMainWindow()
    window.setWindowTitle("Climbing Rocks")
    window.setFixedSize(1280, 800)
    window.setFont(QFont("DM Sans"))
    window.setStyleSheet("background-color: #222222; font-size: 20px; color: #ffffff;")
    
    window.resultsScreen = ResultsScreen("Danica", False, window)
    window.setCentralWidget(window.resultsScreen)    

    
    window.show()
    sys.exit(app.exec_())
else:
    from AnalyseClimb.ClimbAnalyser import ClimbAnalyserThread
    