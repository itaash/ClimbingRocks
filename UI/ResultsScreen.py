from PyQt5.QtCore import pyqtSlot, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QImage, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect


class ResultsScreen(QWidget):
    timeoutSignal = pyqtSignal()
    def __init__(self, climberName, climbSuccessful, parent=None):
        super().__init__(parent)

        # Set up the layout
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        

        # Add white space on the top
        self.mainLayout.addSpacing(35)

        #intro text
        self.climbFinishedLabel = QLabel()
        self.climbFinishedLabel.setIndent(180)
        self.climbFinishedLabel.setStyleSheet("font-size: 32px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: transparent; border-radius: 10px;")
        self.climbFinishedLabel.setText(f"Hold on tight, {climberName}. \n\nWe're analysing your climb now...")


        # Add the logo to the top left corner
        self.logoLabel = QLabel(self)
        self.logoLabel.setPixmap(QPixmap("UI/UIAssets/logo.png").scaledToWidth(120, Qt.SmoothTransformation))
        self.logoLabel.setStyleSheet("background-color: transparent;")
        self.logoLabel.setFixedSize(120, 120)
        self.logoLabel.move(35, 35)


        self.climbSuccessful = climbSuccessful
        self.climberName = climberName

        self.mainLayout.addWidget(self.climbFinishedLabel, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Add space
        self.mainLayout.addSpacing(60)

        # Create the central hbox layout with three widgets
        hboxLayout = QHBoxLayout()
        hboxLayout.setSpacing(50)
        hboxLayout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.pressureWidget = MetricWidget("Pressure", "UI/UIAssets/loading.gif", ClimbAnalyserThread.submetricsLabels["pressure"], colour='#0A9DAE', parent=self)
        self.positioningWidget = MetricWidget("Positioning", "UI/UIAssets/loading.gif", submetrics = ClimbAnalyserThread.submetricsLabels["positioning"], colour='#CA2B3B', parent=self)
        self.progressWidget = MetricWidget("Progress", "UI/UIAssets/loading.gif", submetrics = ClimbAnalyserThread.submetricsLabels["progress"], colour='#8C16F3', parent=self)
        hboxLayout.addWidget(self.pressureWidget)
        hboxLayout.addWidget(self.positioningWidget)
        hboxLayout.addWidget(self.progressWidget)
        self.mainLayout.addLayout(hboxLayout)

        # Add more white space on the bottom
        self.mainLayout.addSpacing(100)

        # Create the "Click to see Climbing tip" button
        self.tipButton = QPushButton("Click to see \nClimbing tip", self)
        self.tipButton.setStyleSheet("font-size: 24px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: #8f8f8f; border: none; padding: 10px; border-radius: 20px;")
        self.tipButton.setFixedSize(220, 100)
        self.tipButton.move(parent.width() - self.tipButton.width() - 50, 50)
        self.tipButton.clicked.connect(self.goToTip)
        # hide the button until the analysis is complete
        self.tipButton.setDisabled(True)
        # self.tipButton.setVisible(False)

        # Create and start a 20-second timer to display the tip
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.goToTip)
        self.timer.start(20000)  # 20 seconds in milliseconds

        # create a 10 second timer to emit the signal to exit the results screen, starts once the tip is displayed
        self.exitTimer = QTimer(self)
        self.exitTimer.setSingleShot(True)
        self.exitTimer.timeout.connect(self.handleExitTimer)

        # start a 0 second timer to start climbing analysis, connect the signal from the climbanalyser to update the metrics
        self.startTimer = QTimer(self)
        self.startTimer.setSingleShot(True)
        self.startTimer.timeout.connect(self.startClimbAnalysis)
        self.startTimer.start(4000)

    def startClimbAnalysis(self):
        self.climbAnalyser = ClimbAnalyserThread(self.climberName, self)
        self.climbAnalyser.ClimbAnalysisComplete.connect(self.updateMetrics)
        self.climbAnalyser.start()

    def goToTip(self):
        # TODO: Implement the goToTip method to display a climbing tip
        self.timer.stop()
        print("Going to tip")

        
        pass

    @pyqtSlot()
    def handleExitTimer(self):
        self.timeoutSignal.emit()

    @pyqtSlot()
    def updateMetrics(self):
        """
        Update the metrics with the results from the climb analysis, called when the climb analysis is complete
        Makes the tip button visible and clickable
        """

        overallScoreStr = str(self.climbAnalyser.getClimbingScore())
        
        # if self.climbSuccessful:
        #     message = f"\t Congratulations, {self.climberName}, you scored <span style='font-size: 34px; color: #FF66B2;'>{overallScoreStr}</span>! \nHere's why:"
        # else:
        #     message = f"\t Skill issue, {self.climberName}, you scored <span style='font-size: 34px; color: #FF66B2;'>{overallScoreStr}</span>! \nTake notes:"

        if self.climbSuccessful:
            message = f"Congratulations, {self.climberName}, you scored <span style='color: #FF66B2;'>{overallScoreStr}</span>/100!<br><br>"\
                        "Here's why:"
        else:
            message = f"Skill issue, {self.climberName}, you scored <span style='color: #FF66B2;'>{overallScoreStr}</span>/100!<br><br>"\
                        "Take notes:"


        self.climbFinishedLabel.setText(message)

        self.tipButton.setStyleSheet("font-size: 24px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: #14904d; border: none; padding: 10px; border-radius: 20px;")
        self.tipButton.setDisabled(False)
        # self.tipButton.setVisible(True)
        
        pressureSubmetrics = self.climbAnalyser.getPressureSubmetrics()
        pressureVisualisation = self.climbAnalyser.getPressureVisualisation()

        positioningSubmetrics = self.climbAnalyser.getPositioningSubmetrics()
        positioningVisualisation = self.climbAnalyser.getPositioningVisualisation()

        progressSubmetrics = self.climbAnalyser.getProgressSubmetrics()
        progressVisualisation = self.climbAnalyser.getProgressVisualisation()

        self.pressureWidget.updateImage(pressureVisualisation)
        self.pressureWidget.updateScore(pressureSubmetrics)

        self.progressWidget.updateImage(progressVisualisation)
        self.progressWidget.updateScore(progressSubmetrics)

        self.positioningWidget.updateImage(positioningVisualisation)
        self.positioningWidget.updateScore(positioningSubmetrics)


class MetricWidget(QWidget):
    def __init__(self, metric: str, image, submetrics: list, colour: str = '#222222', score: int = 100, parent=None):
        super(MetricWidget, self).__init__(parent)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Create the label and value widgets
        self.labelLayout= QHBoxLayout()
        self.labelLayout.setAlignment(Qt.AlignCenter)
        labelLogo = QLabel(self)
        labelLogo.setPixmap(QPixmap(f"UI/UIAssets/{metric}Icon.png").scaledToWidth(40, Qt.SmoothTransformation))
        # labelLogo.setPixmap(QPixmap(f"UI/UIAssets/logo.png").scaledToWidth(40, Qt.SmoothTransformation))
        labelText = QLabel(metric, self)
        labelText.setStyleSheet("font-size: 24px; color: #ffffff; font-family: 'Bungee'; text-align: left;")
        labelText.setFixedWidth(180)
        labelText.setFixedHeight(40)

        self.scoreLabel = QLabel(str(score))
        self.scoreLabel.setFixedWidth(60)
        self.scoreLabel.setStyleSheet("font-size: 28px; color: #ffffff; font-family: 'DM Sans'; font-weight: bold;")
        self.scoreLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.labelLayout.addWidget(labelLogo)
        self.labelLayout.addSpacing(10)
        self.labelLayout.addWidget(labelText)
        self.labelLayout.addSpacing(15)
        self.labelLayout.addWidget(self.scoreLabel, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addSpacing(5)
        layout.addLayout(self.labelLayout)
        layout.addSpacing(15)

        # add the image
        self.image = QLabel()
        self.image.setStyleSheet("background-color: #ffffff; border-radius: 15px")
        # self.image.setPixmap(QPixmap(image).scaledToHeight(270, Qt.SmoothTransformation))
        self.image.setPixmap(QPixmap(image).scaledToWidth(300, Qt.SmoothTransformation))
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(10)

        self.submetricWidgetsList = []

        # create a submetric widget for each submetric
        for submetric in submetrics:
            submetricWidget = MetricWidget.SubMetric(submetric, parent=self)
            self.submetricWidgetsList.append(submetricWidget)
            layout.addWidget(submetricWidget, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)
        # Set the layout for the widget
        self.setLayout(layout)
        self.setFixedSize(365, 520)

        # Set the style for the widget - a rounded rectangle with a shadow
        metricWrapper = QWidget(self)
        metricWrapper.setStyleSheet(f"border-radius: 20px; background-color: {colour}; ")
        metricWrapper.setLayout(self.layout())
        metricWrapper.setFixedWidth(self.width())
        metricWrapper.setFixedHeight(self.height())


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

    def updateScore(self, scoreList):
        self.scoreLabel.setText(str(round(scoreList[0])))

        for i in [0,len(self.submetricWidgetsList)-1]:
            self.submetricWidgetsList[i].updateScore(scoreList[i+1])

    

    class SubMetric(QWidget):
        def __init__(self, name, score = 100, parent=None):
            super(QWidget, self).__init__(parent)

            layout = QHBoxLayout(self)
            layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

            nameLabel = QLabel(name, self)
            nameLabel.setStyleSheet("font-size: 22px; color: #ffffff; font-family: 'DM Sans'; font-weight: bold;")
            nameLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            nameLabel.setFixedWidth(180)

            self.scoreLabel = QLabel(str(score), self)
            self.scoreLabel.setFixedWidth(60)
            self.scoreLabel.setStyleSheet("font-size: 22px; color: #ffffff; font-family: 'DM Sans'; font-weight: bold;")
            self.scoreLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            layout.addWidget(nameLabel, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(self.scoreLabel, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            self.setLayout(layout)
            self.setFixedWidth(240)
            self.setFixedHeight(50)

        def updateScore(self, score):
            self.scoreLabel.setText(str(round(score)))


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
    
    window.resultsScreen = ResultsScreen("Alex", False, window)
    window.setCentralWidget(window.resultsScreen)

    
    window.show()
    sys.exit(app.exec_())
else:
    from AnalyseClimb.ClimbAnalyser import ClimbAnalyserThread
    