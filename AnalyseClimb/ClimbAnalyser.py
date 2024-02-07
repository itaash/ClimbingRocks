import os
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from AnalyseClimb import Pressure, Positioning, Progress
import pandas as pd


class ClimbAnalyserThread(QThread):
    ClimbAnalysisComplete = pyqtSignal()  # Signal to indicate that analysis is complete

    climbingTipsDict = { "arm-bend": "Try to keep your arms straighter",
                         "hip-distance": "Try to keep your hips closer to the wall",
                         "speed": "Try to climb faster",
                        "grip-strength": "Try to improve your grip strength",
                        "hesitation": "Try to be deliberate in your movements"
    }

    metricsWeights = {"pressure": 0.5, "positioning": 0.3, "progress": 0.2}

    submetricsLabels = {"pressure": ["submetric1", "submetric2", "submetric3"],
                        "positioning": ["submetric1", "submetric2", "submetric3"],
                        "progress": ["submetric1", "submetric2", "submetric3"]
    }

    submetricsWeights = {"pressure": [0.3, 0.3, 0.4],
                         "positioning": [0.4, 0.3, 0.3],
                         "progress": [0.3, 0.4, 0.3]
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
        # TODO: implement this
        pass
