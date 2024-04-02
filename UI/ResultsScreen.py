from PyQt5.QtCore import pyqtSlot, QTimer, Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QFont, QPixmap, QImage, QColor, QLinearGradient, QPainter, QPainterPath, QBrush
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QDialog, QStackedLayout


class ResultsScreen(QWidget):
    timeoutSignal = pyqtSignal()
    def __init__(self, climberName = "", climbSuccessful = False, parent=None):
        super().__init__(parent)

        # Set up the layout
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        

        # Add white space on the top
        self.mainLayout.addSpacing(53)

        #intro text
        self.climbFinishedLabel = QLabel()
        self.climbFinishedLabel.setIndent(180)
        self.climbFinishedLabel.setStyleSheet("font-size: 32px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: transparent; border-radius: 10px;")
        self.climbFinishedLabel.setText(f"Hold on tight, {climberName}. \nWe're analysing your climb now...")


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
        self.mainLayout.addSpacing(70)

        #add a stacked layout(contained within a widget) with the three metrics on one layer and the tip dialog widget on another
        self.stackedWidget = QWidget()
        self.stackedLayout = QStackedLayout(self.stackedWidget)
        self.stackedLayout.setAlignment(Qt.AlignCenter)

        # Create the central hbox layout with three widgets
        hboxLayout = QHBoxLayout()
        hboxLayout.setSpacing(50)
        hboxLayout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        # Create the three metric widgets
        self.pressureWidget = MetricWidget("Pressure", "UI/UIAssets/loading.gif", ClimbAnalyserThread.submetricsLabels["pressure"], colour='#0A9DAE', parent=self)
        self.positioningWidget = MetricWidget("Positioning", "UI/UIAssets/loading.gif", submetrics = ClimbAnalyserThread.submetricsLabels["positioning"], colour='#CA2B3B', parent=self)
        self.progressWidget = MetricWidget("Progress", "UI/UIAssets/loading.gif", submetrics = ClimbAnalyserThread.submetricsLabels["progress"], colour='#8C16F3', parent=self)
        # extremely pink: #FF79B4
        hboxLayout.addWidget(self.pressureWidget)
        hboxLayout.addWidget(self.positioningWidget)
        hboxLayout.addWidget(self.progressWidget)
        hboxWidget = QWidget()
        hboxWidget.setLayout(hboxLayout)

        self.stackedLayout.insertWidget(0, hboxWidget)
        self.stackedLayout.setCurrentIndex(0)

        self.mainLayout.addWidget(self.stackedWidget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Add more white space on the bottom
        self.mainLayout.addStretch(1)

        # Create the "Click to see Climbing tip" button
        self.tipButton = QPushButton("Click to see \nClimbing tip", self)
        self.tipButton.setStyleSheet("font-size: 24px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: #8f8f8f; border: none; padding: 10px; border-radius: 20px;")
        self.tipButton.setFixedSize(220, 100)
        self.tipButton.move(parent.width() - self.tipButton.width() - 50, 50)
        self.tipButton.clicked.connect(self.onTipButtonClicked)
        # hide the button until the analysis is complete
        self.tipButton.setDisabled(True)
        # self.tipButton.setVisible(False)

        # Create and start a 20-second timer to display the tip
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.onTipButtonClicked)
        self.timer.start(20000)  # 20 seconds in milliseconds

        # create a 10 second timer to emit the signal to exit the results screen, starts once the tip is displayed
        self.exitTimer = QTimer(self)
        self.exitTimer.setSingleShot(True)
        self.exitTimer.timeout.connect(self.exitClimbingScreen)

        # start a 0 second timer to start climbing analysis, connect the signal from the climbanalyser to update the metrics
        self.startTimer = QTimer(self)
        self.startTimer.setSingleShot(True)
        self.startTimer.timeout.connect(self.startClimbAnalysis)
        self.startTimer.start(4000)

    def startClimbAnalysis(self):
        self.climbAnalyser = ClimbAnalyserThread(self.climberName, self.climbSuccessful, self)
        self.climbAnalyser.ClimbAnalysisComplete.connect(self.updateMetrics)
        self.climbAnalyser.start()

    def onTipButtonClicked(self):
        # TODO: Implement the goToTip method to display a climbing tip
        self.timer.stop()
        if self.stackedLayout.currentIndex() == 0:
            self.stackedLayout.setCurrentIndex(1)
            self.tipButton.setText("Click to show \nClimb metrics")
            self.tipButton.setStyleSheet("font-size: 24px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: #CB2727; border: none; padding: 10px; border-radius: 20px;")
        elif self.stackedLayout.currentIndex() == 1:
            self.stackedLayout.setCurrentIndex(0)
            self.tipButton.setText("Click to see \nClimbing tip")
            self.tipButton.setStyleSheet("font-size: 24px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: #14904d; border: none; padding: 10px; border-radius: 20px;")
            self.exitTimer.start(10000)
        pass


    def exitClimbingScreen(self):
        print("Exiting climbing screen")
        self.timer.stop()
        self.exitTimer.stop()
        self.timeoutSignal.emit()

    @pyqtSlot()
    def updateMetrics(self):
        """
        Update the metrics with the results from the climb analysis, called when the climb analysis is complete
        Makes the tip button visible and clickable
        """

        overallScoreStr = str(self.climbAnalyser.getClimbingScore())

        self.setSuccessfulClimb(overallScoreStr)

        self.tipButton.setStyleSheet("font-size: 24px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: #14904d; border: none; padding: 10px; border-radius: 20px;")
        self.tipButton.setDisabled(False)
        
        pressureSubmetrics = self.climbAnalyser.getPressureSubmetrics()
        pressureVisualisation = self.climbAnalyser.getPressureVisualisation()

        positioningSubmetrics = self.climbAnalyser.getPositioningSubmetrics()
        positioningVisualisation = self.climbAnalyser.getPositioningVisualisation()

        progressSubmetrics = self.climbAnalyser.getProgressSubmetrics()
        progressVisualisation = self.climbAnalyser.getProgressVisualisation()

        lowestWeightedSubmetric = self.climbAnalyser.getLowestWeightedSubmetric()
        climbingTip = self.climbAnalyser.getClimbingTip()

        self.pressureWidget.updateImage(pressureVisualisation)
        self.pressureWidget.updateScore(pressureSubmetrics)

        self.progressWidget.updateImage(progressVisualisation)
        self.progressWidget.updateScore(progressSubmetrics)

        self.positioningWidget.updateImage(positioningVisualisation)
        self.positioningWidget.updateScore(positioningSubmetrics)

        self.tipDialog = TipDialog(lowestWeightedSubmetric, climbingTip, self)
        self.tipHBoxLayout = QHBoxLayout()
        self.tipHBoxLayout.addWidget(self.tipDialog, alignment=Qt.AlignmentFlag.AlignCenter)
        self.tipBoxWidget = QWidget()
        self.tipBoxWidget.setLayout(self.tipHBoxLayout)
        self.stackedLayout.insertWidget(1, self.tipBoxWidget)

    def setCurrentClimber(self, climberName):
        self.climberName = climberName

    def setSuccessfulClimb(self, overallScoreStr):

        if self.climbSuccessful:
            message = f"Congratulations, {self.climberName}, you scored <span style='color: #FF66B2;'>{overallScoreStr}</span>/100!<br>"\
                        "Here's an analysis:"
        else:
            message = f"Good try, {self.climberName}, you scored <span style='color: #FF66B2;'>{overallScoreStr}</span>/100!<br>"\
                        "Here's a breakdown:"


        self.climbFinishedLabel.setText(message)


    # def getLowestWeightedSubmetric(self, pressureSubmetrics, positioningSubmetrics, progressSubmetrics):
    #     """
    #     Get the lowest weighted submetric from the three submetric lists

    #     Args:
    #         pressureSubmetrics (list): list of submetric scores for the pressure metric
    #         positioningSubmetrics (list): list of submetric scores for the positioning metric
    #         progressSubmetrics (list): list of submetric scores for the progress metric

    #     Returns:
    #         str: the name of the lowest weighted submetric
    #     """

    def reset(self):
        self.climbFinishedLabel.setText(f"Hold on tight, {self.climberName}. \nWe're analysing your climb now...")
        self.tipButton.setDisabled(True)
        self.tipButton.setText("Click to see \nClimbing tip")
        self.tipButton.setStyleSheet("font-size: 24px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: #8f8f8f; border: none; padding: 10px; border-radius: 20px;")
        self.stackedLayout.setCurrentIndex(0)
        


class MetricWidget(QWidget):
    def __init__(self, metric: str, image, submetrics: list, colour: str = '#222222', score: int = 100, parent=None):
        super(MetricWidget, self).__init__(parent)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        darkerColour = QColor(colour).darker(150)
        darkerColourHex = darkerColour.name()

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

        labelLayoutWrapper = QWidget(self)
        labelLayoutWrapper.setLayout(self.labelLayout)
        labelLayoutWrapper.setStyleSheet(f"background-color: {colour}; border-radius: {labelLayoutWrapper.height()}px;")

        layout.addSpacing(5)
        layout.addWidget(labelLayoutWrapper, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)

        # add the image
        self.image = QLabel()
        self.image.setStyleSheet("background-color: 'transparent'; border-radius: 15px")
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
        self.setFixedSize(365, 500)

        # Set the style for the widget - a rounded rectangle with a shadow
        metricWrapper = QWidget(self)
        metricWrapper.setStyleSheet(f"border-radius: {labelLayoutWrapper.height()}px; background-color: {colour}; ")
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
        imagePixmap = QPixmap(image)
        #imagePixmap = QPixmap.fromImage(QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888))
        self.image.setPixmap(imagePixmap.scaledToHeight(250, Qt.SmoothTransformation))

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


class TipDialog(QWidget):
    """
    Dialog to display the climbing tip associated with the results of the climb analysis
    Opens when the tip button is clicked or when the timer runs out
    Contains a label with the tip and a close button. Closes when the close button is clicked or the escape key is pressed or if the dialog loses focus or a timer runs out.
    """
    def __init__(self, submetric, tip, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.setFixedSize(round(parent.width() * 0.8), 500)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        submetricLabel = QLabel()
        submetricLabel.setStyleSheet("font-size: 34px; color: #ffffff; font-family: 'DM Sans'; background-color: transparent; padding: 10px; font-weight: bold;")
        submetricLabel.setText(f"Your area of improvement is: <span style='font-family: Bungee;'>{submetric}</span>") 

        self.tipLabel = QLabel(tip)
        self.tipLabel.setStyleSheet("font-size: 28px; color: #ffffff; font-family: 'DM Sans'; background-color: transparent; padding: 10px; font-weight: 400")
        self.tipLabel.setFixedWidth(round(self.width() * 0.8))
        self.tipLabel.setWordWrap(True)

        dividerLine = QLabel(self)
        dividerLine.setFixedWidth(round(self.width() * 0.8))
        dividerLine.setFixedHeight(4)
        dividerLine.setStyleSheet("background-color: #222222; border-radius: 2px;")
        
        # Add button to exit climbing screen
        exitButton = QPushButton("End Climbing Session", self)
        exitButton.clicked.connect(self.parent.exitClimbingScreen)
        exitButton.setFixedSize(300, 60)
        exitButton.setStyleSheet("font-size: 24px; color: #ffffff; font-weight: bold; font-family: 'DM Sans'; background-color: #14904d;"\
                                 "border: none; padding: 10px; border-radius: 20px;")
        
        # Add shadow effect to the button
        shadowEffect = QGraphicsDropShadowEffect()
        shadowEffect.setBlurRadius(50)
        shadowEffect.setColor(QColor("#222222"))
        shadowEffect.setOffset(0, 0)
        exitButton.setGraphicsEffect(shadowEffect)

        self.layout.addSpacing(30) 
        self.layout.addWidget(submetricLabel, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.layout.addSpacing(20)
        self.layout.addWidget(dividerLine, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.tipLabel, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)



        self.layout.addStretch(1)

        self.layout.addSpacing(30)
        self.layout.addWidget(exitButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addSpacing(30)


        # Set the layout for the widget
        self.setLayout(self.layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create a linear gradient for the background
        # gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient = QLinearGradient(0, self.height(), self.width(), 0)
        gradient.setColorAt(1, QColor("#CA2B3B"))  # color at right
        gradient.setColorAt(0.5, QColor("#8C16F3"))  # color at in the middle
        gradient.setColorAt(0, QColor("#0A9DAE"))  # color at left


        # Draw the rounded rectangle with the gradient background
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)

        radius = 20
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        painter.drawPath(path)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def focusOutEvent(self, event):
        self.close()
    """
    def showEvent(self, event):
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close)
        self.timer.start(20000)  # 10 seconds in milliseconds
    """
    def close(self):
        self.timer.stop()
        super().close()



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
    
    window.resultsScreen = ResultsScreen("itaash Fails", False, window)
    window.setCentralWidget(window.resultsScreen)

    
    window.show()
    sys.exit(app.exec_())
else:
    from AnalyseClimb.ClimbAnalyser import ClimbAnalyserThread
    