import csv, random
from operator import itemgetter

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QScrollArea, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QGraphicsDropShadowEffect


class LeaderboardWidget(QWidget):
    def __init__(self, position: int, name: str, score: int, parent):
        super().__init__(parent)

        # Set fixed size for the widget
        self.setFixedHeight(55)  # Adjust the height as needed
        self.setFixedWidth(350)  # Adjust the width as needed

        # Create rounded rectangle background
        background = QLabel(self)
        background.setStyleSheet("background-color: #87509e; border-top-left-radius: 15px; border-top-right-radius: 15px; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px; opacity: 75;")
        background.setFixedSize(self.width(), self.height())

        # Create labels for position, name, and score
        positionLabel = QLabel(str(position), self)
        positionLabel.setAlignment(Qt.AlignHCenter| Qt.AlignVCenter)
        positionLabel.setStyleSheet("background-color: 'transparent'; color: #000; font-weight: 500; line-height: 15px;")

        nameLabel = QLabel(name, self)
        nameLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        nameLabel.setStyleSheet("background-color: 'transparent'; color: #000; font-weight: 500; line-height: 15px;")

        scoreLabel = QLabel(str(score), self)
        scoreLabel.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        scoreLabel.setStyleSheet("background-color: 'transparent'; color: #000; font-weight: 500; line-height: 15px;")

        # Create the layout for the widget
        layout = QHBoxLayout(self)
        layout.addWidget(positionLabel)
        layout.addWidget(nameLabel)
        layout.addWidget(scoreLabel)
        layout.addSpacing(8)


        # Set fixed size for the widget
        self.setFixedHeight(55)  # Adjust the height as needed

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
        leaderboardLabel.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Create a scroll area for the leaderboard
        leaderboardScrollArea = QScrollArea()
        leaderboardScrollArea.setWidgetResizable(True)
        leaderboardScrollArea.setFixedWidth(400)
        leaderboardScrollArea.setStyleSheet("border: 0px")
        leaderboardScrollWidget = QWidget()
        leaderboardScrollArea.setWidget(leaderboardScrollWidget)
        leaderboardScrollLayout = QVBoxLayout(leaderboardScrollWidget)
        leaderboardScrollLayout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        leaderboardScrollLayout.setSpacing(15)

        # Populate the leaderboard from CSV
        self.populateLeaderboard(leaderboardScrollLayout)
        
        # Customize the scroll bar style
        scroll_bar_style = """
            QScrollBar:vertical {
                border: 0px;  /* Border color */
                background: 'transparent' ;  /* Background color */
                width: 10px;  /* Width of the scroll bar */
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: #87509e;  /* Scroll pill color */
                min-height: 20px;  /* Height of the scroll pill */
                border-radius: 10px;
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
        leaderboardLayout.addStretch(1)

                # Create shadow effect for leaderboardLayout
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)
        shadow_effect.setColor(Qt.black)
        shadow_effect.setOffset(0, 0)

        # Wrap the layout in a QWidget and apply the shadow effect to the widget
        leaderboardWrapper = QWidget()
        leaderboardWrapper.setFixedWidth(leaderboardScrollArea.width() + 20)
        leaderboardWrapper.setFixedHeight(leaderboardLabel.height() + leaderboardScrollWidget.visibleRegion().boundingRect().height()+20)
        leaderboardWrapper.setStyleSheet("border-radius: 10px;")
        leaderboardWrapper.setLayout(leaderboardLayout)
        leaderboardWrapper.setGraphicsEffect(shadow_effect)

        hLayout.addWidget(leaderboardWrapper)

        
        # Add some spacing between the two halves
        hLayout.addSpacing(parent.width()//7)


        # Right half: User input and start button
        inputLayout = QVBoxLayout()
        inputLayout.setAlignment(Qt.AlignTop)
        inputLayout.addSpacing(100)
        inputLabel = QLabel("ENTER NAME:")
        # inputLabel.setFixedWidth(400)
        inputLabel.setStyleSheet("font-size: 50px; font-weight: bold;")

        self.nameInput = QLineEdit()
        self.nameInput.setFixedWidth(400)
        self.nameInput.setStyleSheet("background-color: #ffffff; color: #000; font-size: 24px; font-weight: bold; border-radius: 5px; height: 40px; padding-left: 10px;")
        self.nameInput.setPlaceholderText("Nom nom nom")

        self.startButton = QPushButton("Start")
        self.startButton.setDisabled(True)  # Initially disabled
        self.startButton.clicked.connect(self.startClimbing)

        inputLayout.addWidget(inputLabel)
        inputLayout.addWidget(self.nameInput)

        inputLayout.addSpacing(50)
        inputLayout.addWidget(self.startButton)
        inputLayout.addStretch(1)

        hLayout.addLayout(inputLayout)
        hLayout.addSpacing(40)

        vLayout = QVBoxLayout()
        vLayout.addSpacing(50)
        vLayout.addLayout(hLayout)


        # Set the main layout for the LobbyScreen
        self.setLayout(vLayout)

        # Connect the textChanged signal to enable/disable the start button
        self.nameInput.textChanged.connect(self.updateStartButton)

        # Set the callback function to be called when the start button is clicked
        try:
            self.callback = parent.goToHoldFindingScreen
        except:
            self.callback = None


    def populateLeaderboard(self, layout):
        # Read data from CSV file and populate the leaderboard widgets
        filePath = "data/leaderboard.csv"

        with open(filePath, 'r') as file:
            lines = file.readlines()

        if not lines:
            return

        # Extract column headers from the first row
        headers = lines[0].strip().split(',')

        # Extract data from each line and convert scores to integers
        data_list = []
        for line in lines[1:]:
            data = line.strip().split(',')
            data_list.append([data[0]] + [int(score) for score in data[1:]])

        # Sort data by score in descending order
        data_list.sort(key=itemgetter(1), reverse=True)

        # Add up to 20 of the top-scoring climbs
        for row, data in enumerate(data_list[:20]):
            name, score = data[0], data[1]
            leaderboardWidget = LeaderboardWidget(row + 1, name, score, self)
            layout.addWidget(leaderboardWidget)

    def updateStartButton(self):
        # Enable the start button only if there is text in the input field
        self.startButton.setDisabled(self.nameInput.text() == "")

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

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5.QtGui import QFontDatabase

    # sys.path.append('C:\Users\itaas\Documents\UBC\Year 4 (2023-2024)\IGEN 430\ClimbingRocks')   

    app = QApplication(sys.argv)



    # Create the main window
    window = QMainWindow()
    window.setStyleSheet("background-color: #222222; font-size: 20px; color: #ffffff;")
    window.setFixedSize(1280, 720)  # Set the window size
    window.setWindowTitle("Climbing Rocks")  # Set the window title
    QFontDatabase.addApplicationFont("UI/UIAssets/DMSans.ttf")
    window.setFont(QFont("DM Sans"))

    # Create the LobbyScreen widget and set it as the central widget
    lobbyScreen = LobbyScreen(window)
    window.setCentralWidget(lobbyScreen)

    window.show()
    sys.exit(app.exec_())
