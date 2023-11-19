import csv

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class LobbyScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        
        # Set up the horizontal layout
        hLayout = QHBoxLayout()

        # Left half: Leaderboard
        leaderboardLayout = QVBoxLayout()
        leaderboardLabel = QLabel("Leaderboard")

        self.leaderboardTable = QTableWidget()
        self.leaderboardTable.setFixedWidth(parent.width()//2)
        self.setupLeaderboard()

        leaderboardLayout.addWidget(leaderboardLabel)
        leaderboardLayout.addWidget(self.leaderboardTable)
        
        hLayout.addLayout(leaderboardLayout)
        
        # Add some spacing between the two halves
        hLayout.addSpacing(parent.width()//5)

        # Right half: User input and start button
        inputLayout = QVBoxLayout()
        inputLayout.setAlignment(Qt.AlignTop)
        inputLayout.addSpacing(100)
        inputLabel = QLabel("Enter Your Name:")
        inputLabel.setFixedWidth((parent.width()*2)//5)

        self.nameInput = QLineEdit()

        self.startButton = QPushButton("Start")
        self.startButton.setDisabled(True)  # Initially disabled
        self.startButton.clicked.connect(self.startClimbing)

        inputLayout.addWidget(inputLabel)
        inputLayout.addWidget(self.nameInput)

        inputLayout.addSpacing(100)
        inputLayout.addWidget(self.startButton)
        inputLayout.addStretch(1)

        hLayout.addLayout(inputLayout)


        vLayout = QVBoxLayout()
        vLayout.addSpacing(50)
        vLayout.addLayout(hLayout)

        # Set the main layout for the LobbyScreen
        self.setLayout(vLayout)

        # Connect the textChanged signal to enable/disable the start button
        self.nameInput.textChanged.connect(self.updateStartButton)

    def setupLeaderboard(self):
        # Read data from CSV file and populate the leaderboard table
        # Assuming a CSV file structure with columns: Rank, Name, Score, Level, Date
        # Replace 'your_file_path.csv' with the actual path to your CSV file
        # You may need to customize this part based on your CSV structure
        filePath = "data/leaderboard.csv"

        with open(filePath, 'r') as file:
            lines = file.readlines()

        if not lines:
            return

        # Extract column headers from the first row
        headers = lines[0].strip().split(',')

        # Set the number of rows and columns in the table
        self.leaderboardTable.setRowCount(len(lines) - 1)  # Exclude the header row
        self.leaderboardTable.setColumnCount(len(headers))

        # Set table headers
        self.leaderboardTable.setHorizontalHeaderLabels(headers)

        # Populate the table with data
        for row, line in enumerate(lines[1:]):  # Exclude the header row
            data = line.strip().split(',')
            for col, item in enumerate(data):
                self.leaderboardTable.setItem(row, col, QTableWidgetItem(item))

    def updateStartButton(self):
        # Enable the start button only if there is text in the input field
        self.startButton.setDisabled(self.nameInput.text() == "")

    def startClimbing(self):
        # Get the user's name from the input field
        userName = self.nameInput.text()

        # Perform any actions needed before starting the climbing session
        # For example, you can save the user's name or perform validation

        # Start the climbing session or transition to the next screen
        print(f"Starting climbing session for {userName}")
        # Add your logic to transition to the next screen or perform other actions

# Example usage:
# lobbyScreen = LobbyScreen()
# lobbyScreen.show()
