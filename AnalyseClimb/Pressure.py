import numpy as np
import seaborn as sns

def calculateProgress(climbData, holdsCoordinates):
    """
    Calculates the progress submetrics
    
    Args:
        climbData: list of strings, each string contains the data of a frame
        holdsCoordinates: list of strings, each string contains the coordinates of a hold
    Returns:
        list of scores, each score represents a submetric
    """
    # TODO: implement this
    # currently returns a list of zeros as a placeholder for the scores so other parts of the app can be tested
    return [0, 0, 0, 0, 0]

def visualiseProgress(climbData, holdsCoordinates, progressSubmetrics):
    """
    Visualises the progress submetrics
    
    Args:
        climbData: list of strings, each string contains the data of a frame
        holdsCoordinates: list of strings, each string contains the coordinates of a hold
        progressSubmetrics: list of scores, each score represents a submetric
    Returns:
        an image that visualises the progress submetrics

    """
    # TODO: implement this
    # currently returns a black image as a placeholder for the visualisation so other parts of the app can be tested

    img = np.zeros((100, 100, 3), dtype=np.uint8)

    return img


