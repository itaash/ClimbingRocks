import numpy as np
import seaborn as sns

def calculatePressure(climbData):
    """
    Calculates the pressure submetrics
    
    Args: TESTESTETSETE
        climbData: list of strings, each string contains the data of a frame
    Returns:
        list of scores, each score represents a submetric
    """
    # TODO: implement this
    # currently returns a list of zeros as a placeholder for the scores so other parts of the app can be tested
    return [100, 100, 100, 0, 0]

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

    img1 = np.zeros((200, 200, 3), dtype=np.uint8)
    img = "UI/UIAssets/pressure_placeholder.png"
    return img


