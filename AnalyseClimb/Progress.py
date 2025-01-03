import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas



#holds_reached, total_holds, holds_coordinates, starting holds and ending holds to incorporate

# Preprocess data, forward fill
def preprocess_data(df):
    df.fillna(method='ffill', inplace=True)  # Fill NaN values in the DataFrame with last valid observation
    return df

def calculate_time_on_holds(climb_data, holdsCoordinates, threshold_distance):
    result_df_left = pd.DataFrame(columns=['Hold_Id', 'Total_Time_Left(ms)', 'Start_Timestamp_Left(ms)', 'End_Timestamp_Left(ms)'])
    result_df_right = pd.DataFrame(columns=['Hold_Id', 'Total_Time_Right(ms)', 'Start_Timestamp_Right(ms)', 'End_Timestamp_Right(ms)'])

    holds_data = pd.DataFrame({
        'Hold_Id': holdsCoordinates["holdNumber"],
        'Hold_X': holdsCoordinates["left"],
        'Hold_Y': holdsCoordinates["top"],
    })

    farthest_hold_left = 0
    farthest_hold_right = 0

    for hold_index, hold_row in holds_data.iterrows():
        hold_id, hold_x, hold_y = hold_row

        # Filter the climb_data based on the hold coordinates and threshold for left hand
        left_wrist_hold = climb_data[
            ((climb_data['left_wrist_X'] - hold_x)**2 + (climb_data['left_wrist_Y'] - hold_y)**2) <= threshold_distance**2
        ]

        if not left_wrist_hold.empty:
            farthest_hold_left = max(farthest_hold_left, hold_id)

            # Calculate the total time spent on the hold by the left hand
            total_time_on_hold_left = left_wrist_hold['Timestamp(ms)'].sum()

            # Determine the start and end timestamps for the left hand
            start_timestamp_left = left_wrist_hold['Timestamp(ms)'].min()
            end_timestamp_left = left_wrist_hold['Timestamp(ms)'].max()

            # Append the result to the left hand DataFrame
            result_df_left = pd.concat([
                result_df_left,
                pd.DataFrame({
                    'Hold_Id': hold_id,
                    'Total_Time_Left(ms)': total_time_on_hold_left,
                    'Start_Timestamp_Left(ms)': start_timestamp_left,
                    'End_Timestamp_Left(ms)': end_timestamp_left
                }, index=[0])
            ], ignore_index=True)
        else:
            # If hold was not held at all by the left hand, set values to 0
            result_df_left = pd.concat([
                result_df_left,
                pd.DataFrame({
                    'Hold_Id': hold_id,
                    'Total_Time_Left(ms)': 0,
                    'Start_Timestamp_Left(ms)': 0,
                    'End_Timestamp_Left(ms)': 0
                }, index=[0])
            ], ignore_index=True)


        # Filter the climb_data based on the hold coordinates and threshold for right hand
        right_wrist_hold = climb_data[
            ((climb_data['right_wrist_X'] - hold_x)**2 + (climb_data['right_wrist_Y'] - hold_y)**2) <= threshold_distance**2
        ]

        if not right_wrist_hold.empty:
            farthest_hold_right = max(farthest_hold_right, hold_id)

            # Calculate the total time spent on the hold by the right hand
            total_time_on_hold_right = right_wrist_hold['Timestamp(ms)'].sum()

            # Determine the start and end timestamps for the right hand
            start_timestamp_right = right_wrist_hold['Timestamp(ms)'].min()
            end_timestamp_right = right_wrist_hold['Timestamp(ms)'].max()

            # Append the result to the right hand DataFrame
            result_df_right = pd.concat([
                result_df_right,
                pd.DataFrame({
                    'Hold_Id': hold_id,
                    'Total_Time_Right(ms)': total_time_on_hold_right,
                    'Start_Timestamp_Right(ms)': start_timestamp_right,
                    'End_Timestamp_Right(ms)': end_timestamp_right
                }, index=[0])
            ], ignore_index=True)

        else:
            # If hold was not held at all by the right hand, set values to 0
            result_df_right = pd.concat([
                result_df_right,
                pd.DataFrame({
                    'Hold_Id': hold_id,
                    'Total_Time_Right(ms)': 0,
                    'Start_Timestamp_Right(ms)': 0,
                    'End_Timestamp_Right(ms)': 0
                }, index=[0])
            ], ignore_index=True)


    return result_df_left, result_df_right, farthest_hold_left, farthest_hold_right


# Function to measure climbing duration and count holds reached
def measure_climbing_duration(climbData):

    # Extract the first and last values from the column
    first_value = climbData['Timestamp(ms)'].iloc[0]
    last_value = climbData['Timestamp(ms)'].iloc[-1]

    # Subtract the first value from the last value
    timeclimb = last_value - first_value

    return timeclimb


# Calculate score based on climbing duration and holds reached
def calculate_hold_score(climbing_data, holdsCoordinates, climbSuccessful):

    if climbSuccessful == True: 
        return 100
    
    elif climbing_data["left_wrist_X"].isnull().all():
        return 0
    
    else: 
        bottom_hold = holdsCoordinates.iloc[0]
        top_hold = holdsCoordinates.iloc[-1]
        #holdsCoordinates[]

        left_highest_reach = min(climbing_data["left_wrist_X"])
        right_highest_reach = min(climbing_data["right_wrist_X"])

        highest_reach = min(left_highest_reach, right_highest_reach)

        if highest_reach < 0:
            highest_reach = 0

        reach = 100 - highest_reach*125 #COMPLETION SCALE VALUE
    
    #if farthest_left == farthest_right == total_holds:  # Climber completed the route
        #return 100  # Return the maximum possible score (100)
    #else:
        #missed_holds = total_holds - max(farthest_left, farthest_right)
        #penalty = 20 * missed_holds  # Subtract 20 points for each hold missed
        #score = 100
        return round(reach, 2)  # Ensure score doesn't go below 0
   


def calculate_hesitation_score(results_left, results_right):

    error_factor = 5 # PATHFINDING SCALE FACTOR

    # Calculate the average time spent on each hold for left hand
    results_left['Average_Time_Left(ms)'] = results_left['Total_Time_Left(ms)'] / (results_left['End_Timestamp_Left(ms)'] - results_left['Start_Timestamp_Left(ms)'])

    # Calculate the absolute difference between consecutive averages for left hand
    results_left['Time_Difference_Left'] = abs(results_left['Average_Time_Left(ms)'].diff())

    # Calculate the overall deviation score for left hand
    left_deviation_score = results_left['Time_Difference_Left'].mean()

    # Calculate the average time spent on each hold for right hand
    results_right['Average_Time_Right(ms)'] = results_right['Total_Time_Right(ms)'] / (results_right['End_Timestamp_Right(ms)'] - results_right['Start_Timestamp_Right(ms)'])

    # Calculate the absolute difference between consecutive averages for right hand
    results_right['Time_Difference_Right'] = abs(results_right['Average_Time_Right(ms)'].diff())

    # Calculate the overall deviation score for right hand
    right_deviation_score = results_right['Time_Difference_Right'].mean()

    hesitation_score = (left_deviation_score + right_deviation_score) * error_factor

    return hesitation_score


def calculate_time_score(timeclimb):
    if np.isnan(timeclimb):
        timeclimb = 0
    else:
        timeclimb = timeclimb/1000
    # TODO: 
    return timeclimb


def hold_number_force(forceData):
    columns_count = (forceData > 3000).any(axis=0).sum()
    return columns_count


# Function to calculate combined score by averaging climbing duration score and hesitation score
def calculate_combined_score(hesitation_score, hold_score):
    
    return (hesitation_score*0.4 + hold_score*0.6) 

    

def calculateProgress(climbData, holdsCoordinates, climbSuccessful, forceData):
    threshold_distance = 10 # specify the threshold distance for proximity to the holds

    climbing_data = preprocess_data(climbData)  # Preprocess NaN values in the DataFrame

    if len(climbing_data) < 2:
        return (0,0,0,0)
    
    else: 
        result_left, result_right, farthest_left, farthest_right = calculate_time_on_holds(climbing_data, holdsCoordinates, threshold_distance)
        timeclimb = measure_climbing_duration(climbing_data)


        force_progress = hold_number_force(forceData)
        pathfinding_score_force = force_progress*10 + 10
        if pathfinding_score_force > 100:
            pathfinding_score_force = 100

        hesitation_score = calculate_hesitation_score(result_left, result_right)
        #hold_score = calculate_hold_score(farthest_left, farthest_right, total_holds = 10)
        hold_score = calculate_hold_score(climbing_data, holdsCoordinates, climbSuccessful)
        climbing_duration_score = calculate_time_score(timeclimb)*2

        #pathfinding_score = max(pathfinding_score_force, hold_score)

        combined_score = calculate_combined_score(pathfinding_score_force, hold_score)
        print(combined_score, hold_score, climbing_duration_score, hesitation_score)
        return [round(combined_score), round(hold_score), round(pathfinding_score_force), round(climbing_duration_score)]

def sum_left_right(result_left, result_right, holdsCoordinates):

    total_hold_time = pd.DataFrame({'Hold num': holdsCoordinates['holdNumber'], 'Time': result_left['Total_Time_Left(ms)'] + result_right['Total_Time_Right(ms)']})

    return total_hold_time


def visualiseProgress(climbData, holdsCoordinates, climbSuccessful):

    climbing_data = preprocess_data(climbData)

    if len(climbing_data) < 2:
        img = f"UI/UIAssets/progress/noclimb.png"

    else:
        hold_score = calculate_hold_score(climbing_data, holdsCoordinates, climbSuccessful)

        if climbSuccessful == True:
            img = f"UI/UIAssets/progress/progress100.png"

        elif 0 <= hold_score < 20:
            img = f"UI/UIAssets/progress/progressr20.png"
        elif 20 <= hold_score < 40:
            img = f"UI/UIAssets/progress/progressy40.png"
        elif 40 <= hold_score < 60:
            img = f"UI/UIAssets/progress/progress60.png"
        elif 60 <= hold_score < 80:
            img = f"UI/UIAssets/progress/progress80.png"
        else:
            img = f"UI/UIAssets/progress/progress100.png"
    
    return img
