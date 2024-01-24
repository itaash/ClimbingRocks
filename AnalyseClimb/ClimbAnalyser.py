import os
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from AnalyseClimb import Pressure, Positioning, Progress


class ClimbAnalyserThread(QThread):
    ClimbAnalysisComplete = pyqtSignal()  # Signal to indicate that analysis is complete

    def __init__(self, climberName, parent):
        super().__init__(parent)
        self.climberName = climberName
        self.parent = parent

    def run(self):
        dataDirectory = "/c:/Users/itaas/Documents/UBC/Year 4 (2023-2024)/IGEN 430/ClimbingRocks/data"
        climbDataDirectory = dataDirectory + "/output.csv"
        holdsCoordinatesDirectory = dataDirectory + "/holdsCoordinates.csv"
        forceDataDirectory = dataDirectory + "/forceData.csv"

        climbData = []
        holdsCoordinates = []
        forceData = []

        # Read climb data from file
        with open(climbDataDirectory, "r") as file:
            climbData = file.readlines()

        # Read holds coordinates from file
        with open(holdsCoordinatesDirectory, "r") as file:
            holdsCoordinates = file.readlines()

        # Read force data from file
        with open(forceDataDirectory, "r") as file:
            forceData = file.readlines()

        if any([len(climbData) == 0, len(holdsCoordinates) == 0, len(forceData) == 0]):
            raise FileNotFoundError("Could not find data files")

        # Calculate pressure
        self.pressureSubmetrics = Pressure.calculatePressure(forceData)
        self.pressureVisualisation = Pressure.visualisePressure(forceData)

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
