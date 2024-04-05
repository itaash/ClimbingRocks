import numpy as np
import seaborn as sns

def preprocess_data(df):
    df.fillna(method='ffill', inplace=True)  # Fill NaN values in the DataFrame with last valid observation
    return df

def calculate_ratio(df):
    # Ignore the first column
    df = df.iloc[:, 1:]

    # Take the sum of the first three columns
    sum_first_three = df.iloc[:, :3].sum().sum()

    # Take the sum of the entire DataFrame
    total_sum = df.sum().sum()

    # Calculate the ratio
    ratio = sum_first_three / total_sum

    return ratio


def calculate_adjustments(df):
    largest_std_dev = 0
    for column in df.columns[1:]:  # Skip the first column which is assumed to be time
        non_zero_indices = df[column][df[column] != 0].index
        for i in range(len(non_zero_indices) - 1):
            start_index = non_zero_indices[i]
            end_index = non_zero_indices[i + 1] + 1
            non_zero_values = df[column][start_index:end_index]
            if len(non_zero_values) > 11:  # Calculate standard deviation only if there are more than one non-zero value
                std_dev = np.std(non_zero_values)
                if std_dev > largest_std_dev:
                    largest_std_dev = std_dev
    return largest_std_dev

def calculatePressure(climbData):

    sd = calculate_adjustments(climbData)
    adjustment_score = 100-sd

    efficiency = calculate_ratio(climbData)
    efficiency_score = efficiency*100

    combined = adjustment_score*0.5+efficiency_score*0.5

    # TODO: implement this
    # currently returns a list of zeros as a placeholder for the scores so other parts of the app can be tested
    
    return [round(combined, 2), round(efficiency_score, 2), round(adjustment_score, 2), 0, 0]

def visualisePressure(climbData, progressSubmetrics):

    sd = calculate_adjustments(climbData)
    adjustment_score = 100-sd

    efficiency = calculate_ratio(climbData)
    efficiency_score = efficiency*100

    combined = adjustment_score*0.5+efficiency_score*0.5

    strength = combined

    if strength == 0:
        img = f"UI/UIAssets/pressure/noclimb_presh.png"
    
    else:

    #REplace will calling the strength score

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


