import numpy as np
import seaborn as sns

def calculatePressure(climbData):
    """
    Calculates the pressure submetrics
    
    Args:
        climbData: list of strings, each string contains the data of a frame
    Returns:
        list of scores, each score represents a submetric
    """
    # TODO: implement this
    # currently returns a list of zeros as a placeholder for the scores so other parts of the app can be tested
    return [99, 98, 97, 0, 0]

def visualisePressure(climbData, progressSubmetrics):
    """
    Visualises the pressure submetrics
    
    Args:
        climbData: list of strings, each string contains the data of a frame
        progressSubmetrics: list of scores, each score represents a submetric
    Returns:
        an image that visualises the progress submetrics

    """
    # TODO: implement this
    # currently returns a black image as a placeholder for the visualisation so other parts of the app can be tested

    img = np.zeros((200, 200, 3), dtype=np.uint8)

    return img


