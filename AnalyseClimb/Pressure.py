import numpy as np
import seaborn as sns

def preprocess_data(df):
    df.fillna(method='ffill', inplace=True)  # Fill NaN values in the DataFrame with last valid observation
    return df

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
    
    climbing_data = preprocess_data(climbData)

    if len(climbing_data) < 2:
        img = f"UI/UIAssets/progress/progress20.png"
    
    else:

    #REplace will calling the strength score
        
        strength = 100

        if 0 <= strength < 25:
            img = f"UI/UIAssets/pressure/pressure20.png"
        elif 25 <= strength < 50:
            img = f"UI/UIAssets/pressure/pressure40.png"
        elif 50 <= strength < 75:
            img = f"UI/UIAssets/pressure/pressure60.png"
        elif 75 <= strength:
            img = f"UI/UIAssets/pressure/pressure80.png"
        else:
            img = f"UI/UIAssets/pressure/pressure80.png"

    return img


