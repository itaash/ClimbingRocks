import os
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from AnalyseClimb import Pressure, Positioning, Progress
import pandas as pd


class ClimbAnalyserThread(QThread):
    ClimbAnalysisComplete = pyqtSignal()  # Signal to indicate that analysis is complete

    climbingTipsDict = {"arm-bend": "Try to keep your arms straighter",
                        "hip-distance": "Try to keep your hips closer to the wall",
                        "speed": "Try to climb faster",
                        "grip-strength": "Try to improve your grip strength",
                        "hesitation": "Try to be deliberate in your movements"
    }

    metricsWeights = {"pressure": 0.3, "positioning": 0.4, "progress": 0.3}

    submetricsLabels = {"pressure": ["Strength", "Adjustments"],
                        "positioning": ["Smoothness", "Arm Bend"],
                        "progress": ["Completion", "Speed", "Hesitation"]
    }

    submetricsWeights = {"pressure": [0.5, 0.5],
                         "positioning": [0.5, 0.5],
                         "progress": [0.4, 0.3, 0.3]
    }

    def __init__(self, climberName, parent):
        super().__init__(parent)
        self.climberName = climberName
        self.parent = parent

    def run(self):
        cwd = os.getcwd()
        dataDirectory = os.path.join(cwd, 'data')
        climbDataDirectory = os.path.join(dataDirectory, "output.csv")   
        holdsCoordinatesDirectory = os.path.join(dataDirectory, "holdCoordinates.csv")
        forceDataDirectory = os.path.join(dataDirectory, "forceData.csv")
        self.leaderBoardDirectory = os.path.join(dataDirectory, 'leaderboard.csv')

        climbData = []
        holdsCoordinates = []
        forceData = []

        # Read climb data from file
        climbData = pd.read_csv(climbDataDirectory)

        # Read holds coordinates from file
        holdsCoordinates = pd.read_csv(holdsCoordinatesDirectory)
       
        # Read force data from file
        forceData = pd.read_csv(forceDataDirectory)

        if any([len(climbData) == 0, len(holdsCoordinates) == 0, len(forceData) == 0]):
            raise FileNotFoundError("Could not find data files")
        
        climbData = pd.DataFrame(climbData)
        print(climbData.columns)

        holdsCoordinates = pd.DataFrame(holdsCoordinates)
        print(holdsCoordinates.columns)
        # Calculate pressure
        self.pressureSubmetrics = Pressure.calculatePressure(forceData)
        self.pressureVisualisation = Pressure.visualisePressure(forceData, self.pressureSubmetrics)

        # Calculate positioning
        self.positionSubmetrics = Positioning.calculatePosition(climbData, holdsCoordinates)
        self.positionVisualisation = Positioning.visualisePosition(climbData, holdsCoordinates)

        # Calculate progress
        self.progressSubmetrics = Progress.calculateProgress(climbData, holdsCoordinates)
        self.progressVisualisation = Progress.visualiseProgress(climbData, holdsCoordinates)


        # Emit signal to parent to indicate that analysis is complete
        self.ClimbAnalysisComplete.emit()

    def getPressureSubmetrics(self):
        return self.pressureSubmetrics  
      
    def getPressureVisualisation(self):
        return self.pressureVisualisation
    
    def getPositioningSubmetrics(self):
        return self.positionSubmetrics    
    
    def getPositioningVisualisation(self):
        return self.positionVisualisation
    
    def getProgressSubmetrics(self):
        return self.progressSubmetrics
    
    def getProgressVisualisation(self):
        return self.progressVisualisation
    
    def getClimbingTip(self):
        """
        finds the weakest submetric and returns a tip to improve it
        weakes submetric is the one with the lowest weighted score
        """
        # TODO: implement this
        pass

    def getClimbingScore(self):
        """
        calculates the climbing score based on the weighs of the metrics and submetrics
        """
        overallScore = ClimbAnalyserThread.metricsWeights["pressure"] * self.pressureSubmetrics[0] + \
                        ClimbAnalyserThread.metricsWeights["positioning"] * self.positionSubmetrics[0] + \
                        ClimbAnalyserThread.metricsWeights["progress"] * self.progressSubmetrics[0]
       
        return round(overallScore)
    
    def saveClimbRecord(self):
        """
        saves the climb record to a the database
        climb record includes the date-time, climber name, climbing score, metrics and submetrics scores

        work in progress
        """
        leaderBoard = pd.read_csv(self.leaderBoardDirectory)
        leaderBoard = pd.DataFrame(leaderBoard)

        if len(leaderBoard) == 0:
            columnsList = ["DateTime", "Climber", "Score"]
            for metric in ClimbAnalyserThread.metricsWeights.keys():
                columnsList.append(metric)
                for submetric in ClimbAnalyserThread.submetricsLabels[metric]:
                    columnsList.append(submetric)
            leaderBoard = pd.DataFrame(columns=columnsList)

        newRecord = []
        for metric in ClimbAnalyserThread.metricsWeights.keys():
            newRecord[metric] = self.metricsWeights[metric] * self.pressureSubmetrics[0] + \
                                self.metricsWeights[metric] * self.positionSubmetrics[0] + \
                                self.metricsWeights[metric] * self.progressSubmetrics[0]
            for submetric in ClimbAnalyserThread.submetricsLabels[metric]:
                newRecord[submetric] = self.submetricsWeights[metric][ClimbAnalyserThread.submetricsLabels[metric].index(submetric)] * self.pressureSubmetrics[0] + \
                                        self.submetricsWeights[metric][ClimbAnalyserThread.submetricsLabels[metric].index(submetric)] * self.positionSubmetrics[0] + \
                                        self.submetricsWeights[metric][ClimbAnalyserThread.submetricsLabels[metric].index(submetric)] * self.progressSubmetrics[0]