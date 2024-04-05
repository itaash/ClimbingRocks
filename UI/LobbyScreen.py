import csv, random
from operator import itemgetter

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QScrollArea, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QColor, QPixmap
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QGraphicsDropShadowEffect


class LeaderboardWidget(QWidget):
    def __init__(self, position: int, name: str, score: int, numRows: int, parent):
        super().__init__(parent)

        # Set fixed size for the widget
        self.setFixedHeight(65)  # Adjust the height as needed
        self.setFixedWidth(350)  # Adjust the width as needed

        self.setFont(QFont("DM Sans"))

        commonEdgeCornerRadius = 8

        # Create rounded rectangle background
        background = QLabel(self)
        background.setFixedSize(self.width(), self.height())


        if position != 1 and position != numRows and numRows > 1:
            background.setStyleSheet(f"background-color: #222222; border-top-left-radius: {commonEdgeCornerRadius}px; border-top-right-radius: {commonEdgeCornerRadius}px; border-bottom-left-radius: {commonEdgeCornerRadius}px; border-bottom-right-radius: {commonEdgeCornerRadius}px; opacity: 75;")
        elif position == 1:
            if numRows != 1:
                background.setStyleSheet(f"background-color: #222222; border-top-left-radius: {self.height()//2}px; border-top-right-radius: {self.height()//2}px; border-bottom-left-radius: {commonEdgeCornerRadius}px; border-bottom-right-radius: {commonEdgeCornerRadius}px; opacity: 75;")
            else:
                background.setStyleSheet(f"background-color: #222222; border-top-left-radius: {self.height()//2}px; border-top-right-radius: {self.height()//2}px; border-bottom-left-radius: {self.height()//2}px; border-bottom-right-radius: {self.height()//2}px; opacity: 75;")
        else:
            background.setStyleSheet(f"background-color: #222222; border-top-left-radius: {commonEdgeCornerRadius}px; border-top-right-radius: {commonEdgeCornerRadius}px; border-bottom-left-radius: {self.height()//2}px; border-bottom-right-radius: {self.height()//2}px; opacity: 75;")

        # Create labels for position, name, and score
        positionLabel = QLabel(str(position), self)
        positionLabel.setAlignment(Qt.AlignHCenter| Qt.AlignVCenter)
        positionLabel.setStyleSheet("background-color: 'transparent'; color: #ffffff; font-weight: 500; line-height: 18px;")

        nameLabel = QLabel(name, self)
        nameLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        nameLabel.setStyleSheet("background-color: 'transparent'; color: #ffffff; font-weight: 500; line-height: 18px;")

        scoreLabel = QLabel(str(score), self)
        scoreLabel.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        scoreLabel.setFixedWidth(40)
        scoreLabel.setFixedHeight(40)
        scoreLabel.setStyleSheet(f"background-color: '#dddddd'; color: #222222; font-weight: 500; line-height: 24px; border-radius: {scoreLabel.height()//2}; text-align: top;")


        # Create the layout for the widget
        layout = QHBoxLayout(self)
        layout.addWidget(positionLabel)
        layout.addWidget(nameLabel)
        layout.addWidget(scoreLabel)
        layout.addSpacing(8)


        # Set fixed size for the widget
        # self.setFixedHeight(55)  # Adjust the height as needed

        # Adjust label sizes to ensure consistent appearance
        positionLabel.setFixedWidth(35)
        nameLabel.setFixedWidth(150)
        scoreLabel.setFixedWidth(45)


class LobbyScreen(QWidget):
    def __init__(self, parent):
        super().__init__(parent)


        hLayout = QHBoxLayout()
        hLayout.setAlignment(Qt.AlignHCenter)
        hLayout.addSpacing(40)


        # Left half: Leaderboard
        leaderboardLayout = QVBoxLayout()

        # Create the leaderboard label
        leaderboardLabel = QLabel("Leaderboard", alignment=Qt.AlignHCenter)
        leaderboardLabel.setStyleSheet("font-size: 40px; font-weight: bold; color: #000; font-family: 'Bungee';")

        # Create a scroll area for the leaderboard
        leaderboardScrollArea = QScrollArea()
        leaderboardScrollArea.setWidgetResizable(True)
        leaderboardScrollArea.setFixedWidth(400)
        # leaderboardScrollArea.viewport().setFixedHeight(500)
        # leaderboardScrollArea.setStyleSheet("border: 0px")
        leaderboardScrollWidget = QWidget()
        leaderboardScrollArea.setWidget(leaderboardScrollWidget)
        self.leaderboardScrollLayout = QVBoxLayout(leaderboardScrollWidget)
        self.leaderboardScrollLayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.leaderboardScrollLayout.setSpacing(7)

        # Populate the leaderboard from CSV
        self.populateLeaderboard()
        
        # Customize the scroll bar style
        scroll_bar_style = """
            QScrollBar:vertical {
                background: solid;  /* Scroll bar background color */
                border-radius: 3px;
                width: 16px;  /* Width of the scroll bar */
                padding: 7px 3px 7px 3px;   /* Padding of the scroll bar */
                }

            QScrollBar::handle:vertical {
                background: #222222;  /* Scroll pill color */
                min-height: 2px;  /* Height of the scroll pill */
                width: 10px;  /* Width of the scroll pill */
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical {
                border: none;
                background: none;
            }

            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """

        leaderboardScrollArea.verticalScrollBar().setStyleSheet(scroll_bar_style)

        leaderboardLayout.addWidget(leaderboardLabel)
        leaderboardLayout.addWidget(leaderboardScrollArea)
        leaderboardLayout.addSpacing(6)

        # Create shadow effect for leaderboardLayout
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(30)
        shadow_effect.setColor(QColor('#c58af9'))
        shadow_effect.setOffset(0, 0)
        
        # Wrap the layout in a QWidget and apply the shadow effect to the widget
        leaderboardWrapper = QWidget()
        leaderboardWrapper.setFixedWidth(leaderboardScrollArea.width() + 20)
        leaderboardWrapper.setFixedHeight(parent.height() - 155)
        leaderboardWrapper.setStyleSheet("border-radius: 10px; background-color: #c58af9;")
        leaderboardWrapper.setLayout(leaderboardLayout)
        leaderboardWrapper.setGraphicsEffect(shadow_effect)

        hLayout.addWidget(leaderboardWrapper)

        
        # Add some spacing between the two halves
        hLayout.addSpacing(parent.width()//7)


        # Right half: User input and start button
        inputLayout = QVBoxLayout()
        inputLayout.setAlignment(Qt.AlignTop)
        inputLayout.addSpacing(190)
        inputLabel = QLabel("ENTER NAME:")
        # inputLabel.setFixedWidth(400)
        inputLabel.setStyleSheet("font-size: 54px; font-weight: bold; font-family: 'Bungee';")

        self.nameInput = QLineEdit()
        self.nameInput.setFixedWidth(400)
        self.nameInput.setStyleSheet("background-color: #ffffff; color: #000; font-size: 26px; font-weight: bold; border-radius: 10px; height: 40px; padding-left: 10px;")
        self.nameInput.setPlaceholderText("Nom nom nom")
        self.nameInput.setMaxLength(14)
        self.nameInput.setFixedHeight(54)

        self.startButton = StartButton(self.startClimbing, self)
        self.startButton.setDisabled(True)
        self.startButton.setVisible(False)
        self.startButton.move(parent.width() - self.startButton.width() - 60, parent.height() - self.startButton.height() - 60)

        inputLayout.addWidget(inputLabel)
        inputLayout.addWidget(self.nameInput)

        # inputLayout.addSpacing(80)
        # inputLayout.addWidget(self.startButton, alignment=Qt.AlignRight)
        inputLayout.addStretch(1)

        hLayout.addLayout(inputLayout)
        hLayout.addSpacing(40)

        vLayout = QVBoxLayout()
        vLayout.addSpacing(30)
        vLayout.addLayout(hLayout)

        # add logo to the center top of the inputLayout
        # logoLabel = QLabel(self)
        # logoLabel.setPixmap(QPixmap("UI/UIAssets/logo.png").scaledToWidth(180, Qt.SmoothTransformation))
        # logoLabel.setStyleSheet("background-color: transparent;")
        # logoLabel.setFixedSize(180, 180)
        # logoLabel.move(inputLayout.geometry().center().x(), 20)


        # Set the main layout for the LobbyScreen
        self.setLayout(vLayout)

        # Connect the textChanged signal to enable/disable the start button
        self.nameInput.textChanged.connect(self.updateStartButton)

        # Set the callback function to be called when the start button is clicked
        try:
            self.callback = parent.goToHoldFindingScreen
        except:
            self.callback = None


    def populateLeaderboard(self):
        # Read data from CSV file and populate the leaderboard widgets
        filePath = "data/leaderboard.csv"
        layout = self.leaderboardScrollLayout

        # remove all widgets from the layout
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)

        with open(filePath, 'r') as file:
            lines = file.readlines()

        if not lines:
            return

        # Extract column headers from the first row
        headers = lines[0].strip().split(',')

        # Extract data from each line and convert scores to integers
        dataList = []
        for line in lines[1:]:
            data = line.strip().split(',')
            dataList.append([data[0]] + [int(score) for score in data[1:]])

        # Sort data by score in descending order
        dataList.sort(key=itemgetter(1), reverse=True)\
        
        if len(dataList) > 20:
            dataList = dataList[:20]
            numWidgets = 20
        else:
            numWidgets = len(dataList)

        # Add up to 20 of the top-scoring climbs
        for row, data in enumerate(dataList):
            name, score = data[0], data[1]
            leaderboardWidget = LeaderboardWidget(row + 1, name, score, numWidgets, self) 
            layout.addWidget(leaderboardWidget)

    def updateStartButton(self):
        # Enable the start button only if there are at least 3 characters in the input field
        self.startButton.setDisabled(self.nameInput.text() == "" and len(self.nameInput.text()) < 3)
        self.startButton.setVisible(self.nameInput.text() != "" and len(self.nameInput.text()) >= 3)


    def startClimbing(self):
        # Get the user's name from the input field
        userName = self.nameInput.text()

        print(f"Starting climbing session for {userName}")

        self.callback()  # Call the callback function

        # Perform any actions needed before starting the climbing session
        # For example, you can save the user's name or perform validation

        # Start the climbing session or transition to the next screen
        # Add your logic to transition to the next screen or perform other actions

    getClimberName = lambda self: self.nameInput.text()

    def updateLeaderboard(self):
        """
        called when the user finishes climbing to update the leaderboard
        """
        # Get the user's name and score
        

    def reset(self):
        self.nameInput.clear()
        self.startButton.setDisabled(True)
        self.startButton.setVisible(False)

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtGui import QFontDatabase
    from Buttons import StartButton

    sys.path.append('C:/Users/itaas/Documents/UBC/Year 4 (2023-2024)\IGEN 430/ClimbingRocks')   

    app = QApplication(sys.argv)



    # Create the main window
    window = QMainWindow()
    window.setStyleSheet("background-color: #222222; font-size: 20px; color: #ffffff;")
    window.setFixedSize(1280, 800)  # Set the window size
    window.setWindowTitle("Climbing Rocks")  # Set the window title
    QFontDatabase.addApplicationFont("UI/UIAssets/DMSans.ttf")
    window.setFont(QFont("DM Sans"))
    QFontDatabase.addApplicationFont("UI/UIAssets/Bungee.ttf")

    # Create the LobbyScreen widget and set it as the central widget
    lobbyScreen = LobbyScreen(window)
    window.setCentralWidget(lobbyScreen)

    window.show()
    sys.exit(app.exec_())
else:
    from UI.Buttons import StartButton
