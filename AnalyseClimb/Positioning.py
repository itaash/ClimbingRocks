import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
from matplotlib.backends.backend_agg import FigureCanvasAgg


# Preprocess data, forward fill
def preprocess_data(df):
    df.fillna(method='ffill', inplace=True)  # Fill NaN values in the DataFrame with last valid observation
    return df

# Function to measure average arm angle throughout the climb
def measure_arm_angle(data):
    #low_angle_threshold = 30  # Define a threshold for a 'low' arm angle
    #high_angle_threshold = 150  # Define a threshold for a 'high' arm angle

    #arm_angle_sum = 0
    #num_samples = len(data)
    #num_low_angles = 0
    #num_high_angles = 0

    # Convert 'Left Arm Angle' and 'Right Arm Angle' columns to numeric
    #data['Left Arm Angle'] = pd.to_numeric(data['Left Arm Angle'], errors='coerce')
    #data['Right Arm Angle'] = pd.to_numeric(data['Right Arm Angle'], errors='coerce')

    #for index, row in data.iterrows():
     #   left_arm_angle = row['Left Arm Angle']
      #  right_arm_angle = row['Right Arm Angle']
#
        # Check for NaN values after conversion
        #if pd.notna(left_arm_angle) and pd.notna(right_arm_angle):
            # Calculate the average of left and right arm angles
            #avg_arm_angle = (left_arm_angle + right_arm_angle) / 2
            #arm_angle_sum += avg_arm_angle

            # Check if the average arm angle is 'low'
            #if avg_arm_angle < low_angle_threshold:
            #    num_low_angles += 1

            #if avg_arm_angle > high_angle_threshold:
                #num_high_angles += 1

    # Calculate the proportion of low arm angles
    #low_angle_proportion = num_low_angles / num_samples if num_samples > 0 else 0

    # Assign score based on the proportion of low arm angles
    score = (np.mean(data["Left Arm Angle"]) + np.mean(data["Right Arm Angle"]))/2

    if score >= 170:
        score = 100
    elif 170 > score:
        score = score/180*100
    
    return round(score, 2)


# Function definition with separate results for right and left hands
def calculate_time_on_holds(climb_data, holdsCoordinates, threshold_distance=2):
    result_df_left = pd.DataFrame(columns=['Hold_Id', 'Total_Time_Left(ms)', 'Start_Timestamp_Left(ms)', 'End_Timestamp_Left(ms)'])
    result_df_right = pd.DataFrame(columns=['Hold_Id', 'Total_Time_Right(ms)', 'Start_Timestamp_Right(ms)', 'End_Timestamp_Right(ms)'])
    holdsCoordinates = pd.DataFrame(holdsCoordinates)
    climb_data = pd.DataFrame(climb_data)
    holds_data = pd.DataFrame({
    'Hold_Id': holdsCoordinates["right"],
    'Hold_X': holdsCoordinates["left"],
    'Hold_Y': holdsCoordinates["top"],
})
    
    for hold_index, hold_row in holds_data.iterrows():
        hold_id, hold_x, hold_y = hold_row

        # Filter the climb_data based on the hold coordinates and threshold for left hand
        left_wrist_hold = climb_data[
            ((climb_data['left_wrist_X'] - hold_x)**2 + (climb_data['left_wrist_Y'] - hold_y)**2) <= threshold_distance**2
        ]

        if not left_wrist_hold.empty:
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


    return result_df_left, result_df_right

def calculate_smoothness(climb_data, left_hand_df, right_hand_df):
    # Merge the two DataFrames on 'Hold_Id'
    merged_df = pd.merge(left_hand_df, right_hand_df, on='Hold_Id', how='inner', suffixes=('_left', '_right'))

    # Identify rows where there is an overlap in the time interval
    overlap_df = merged_df[
        (merged_df['Start_Timestamp_Left(ms)'] <= merged_df['End_Timestamp_Right(ms)']) &
        (merged_df['End_Timestamp_Left(ms)'] >= merged_df['Start_Timestamp_Right(ms)'])
    ]

    # Create a new DataFrame with common timestamps and standard deviations
    common_timestamps_df = pd.DataFrame(columns=['Start_Time_Common(ms)', 'End_Time_Common(ms)', 'COG_X_Std', 'COG_Y_Std'])

    # Iterate through overlapping rows
    for index, row in overlap_df.iterrows():
        # Determine the common start and end times
        start_time_common = max(row['Start_Timestamp_Left(ms)'], row['Start_Timestamp_Right(ms)'])
        end_time_common = min(row['End_Timestamp_Left(ms)'], row['End_Timestamp_Right(ms)'])

        # Filter climb data for the common timestamp period
        common_data = climb_data[
            (climb_data['Timestamp(ms)'] >= start_time_common) &
            (climb_data['Timestamp(ms)'] <= end_time_common)
        ]

        # Calculate the standard deviation of 'Center of Gravity X' and 'Center of Gravity Y'
        cog_x_std = common_data['Center of Gravity X'].std()
        cog_y_std = common_data['Center of Gravity Y'].std()

        # Append to the result DataFrame
        common_timestamps_df = pd.concat([
            common_timestamps_df,
            pd.DataFrame({
                'Start_Time_Common(ms)': start_time_common,
                'End_Time_Common(ms)': end_time_common,
                'COG_X_Std': cog_x_std,
                'COG_Y_Std': cog_y_std
            }, index=[0])
        ], ignore_index=True)

    
    scaler = 2 #THIS VALUE TO CHANGE WHEN WE START TESTING
    avg_cog_x_std = common_timestamps_df['COG_X_Std'].mean()
    avg_cog_y_std = common_timestamps_df['COG_Y_Std'].mean()
    avg_cog = (avg_cog_y_std + avg_cog_x_std)/2
    cog_score = 100 - avg_cog*scaler
    return cog_score


    # Sample usage of the functions
def calculatePosition(climbData, holdsCoordinates):
    climbing_data = preprocess_data(climbData)  # Just do columns we need, not whole thing TO DO
    threshold_distance = 10 #THIS VALUE TO CHANGE WHEN WE START TESTING
    result_dataframe_left, result_dataframe_right = calculate_time_on_holds(climbData, holdsCoordinates, threshold_distance)
    smoothness_score = calculate_smoothness(climbing_data, result_dataframe_left, result_dataframe_right)
    arm_angle_score = measure_arm_angle(climbing_data)

    combined_score = (smoothness_score + arm_angle_score) / 2  # Calculate average of the two scores
    # if any of the scores are NaN, replace with -1
    if np.isnan(combined_score):
        combined_score = -1
    if np.isnan(smoothness_score):
        smoothness_score = -1
    if np.isnan(arm_angle_score):
        arm_angle_score = -1

    return [round(combined_score), round(smoothness_score, 2), round(arm_angle_score, 2)]


def visualisePosition(climbData, holdsCoordinates):
    # Create a DataFrame
    #threshold = 5 #VALUE TO BE CHANGED WHEN TESTING
    #data = {'Time': climbData['Timestamp(ms)'], 'Values': climbData['Center of Gravity X']}
    climbing_data = preprocess_data(climbData)
    arm_score = measure_arm_angle(climbing_data)

    if 0<= arm_score < 20:
        img = f"UI/UIAssets/position/Position_0_30.png"
    elif 20<= arm_score < 40:
        img = f"UI/UIAssets/position/Position_30_60.png"
    elif 40<= arm_score < 60:
        img = f"UI/UIAssets/position/Position_60_90.png"
    elif 60<= arm_score < 80:
        img = f"UI/UIAssets/position/Position_105_135.png"
    else:
        img = f"UI/UIAssets/position/Position_135_165.png"

    return img

    # Return the plot
    #graph 2 on top of each other, green zone is good, when you had good control the line is in the green and bad the line is in the clear

