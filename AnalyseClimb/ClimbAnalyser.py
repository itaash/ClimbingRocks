import os
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from AnalyseClimb import Pressure, Positioning, Progress
import pandas as pd, numpy as np, json, random


class ClimbAnalyserThread(QThread):
    ClimbAnalysisComplete = pyqtSignal()  # Signal to indicate that analysis is complete

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
        self.climbingTipsDirectory = os.path.join(dataDirectory, 'climbingTips.json')

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

        # calculte the lowest weighted submetric and get a climbing tip based on that submetric
        self.lowestWeightedSubmetric = self.getLowestWeightedSubmetric()
        self.climbingTip = self.findClimbingTip(self.lowestWeightedSubmetric)

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
        if self.climbingTip == "":
            return "I'm sorry, but as an AI language model, I don't have personal opinions or feelings; I can only provide information based on patterns"\
                    " in the data I was trained on. Your climb was so bad that I can't even provide a tip for you. You should probably consider a different hobby. "\
                    "Just kidding, something probably went wrong. Please ask the creators for help."
        return self.climbingTip
    
    def findClimbingTip(self, submetric) -> str:
        """
        returns a climbing tip based on the submetric passed as an argument
        if more than one tip is available for the submetric, a random tip corresponding to the submetric is returned

        args:
        submetric: str

        returns:
        climbingTip: str
        """
        try:
            climbingTips = json.load(open(self.climbingTipsDirectory))

            climbingTipsforSubmetric = list(climbingTips[submetric].values())

            climbingTip = random.choice(climbingTipsforSubmetric)
        except:
            climbingTip = ""

        return climbingTip

    def getLowestWeightedSubmetric(self) -> str:
        """
        returns the submetric with the lowest weighted score

        returns:
        minSubmetric: str
        """
        minSubmetric = ""
        minScore = 100
        
        for metric in ClimbAnalyserThread.metricsWeights.keys():
            for submetric in ClimbAnalyserThread.submetricsLabels[metric]:
                if metric == "progress":
                    metricScoreList = self.progressSubmetrics
                elif metric == "positioning":
                    metricScoreList = self.positionSubmetrics
                elif metric == "pressure":
                    metricScoreList = self.pressureSubmetrics
                else:
                        raise ValueError("Invalid metric name")
                
                weightedSubmetricScore = self.submetricsWeights[metric][ClimbAnalyserThread.submetricsLabels[metric].index(submetric)]*metricScoreList[ClimbAnalyserThread.submetricsLabels[metric].index(submetric)+1]
                if weightedSubmetricScore < minScore:
                    minScore = self.submetricsWeights[metric][ClimbAnalyserThread.submetricsLabels[metric].index(submetric)]
                    minSubmetric = submetric
        print(minSubmetric)
        print(minScore)
        return minSubmetric

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