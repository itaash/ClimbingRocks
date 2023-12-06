import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Preprocess data, forward fill
def preprocess_data(df):
    df.fillna(method='ffill', inplace=True)  # Fill NaN values in the DataFrame with last valid observation
    return df

# Function to measure average arm angle throughout the climb
def measure_arm_angle(data):
    low_angle_threshold = 30  # Define a threshold for a 'low' arm angle
    high_angle_threshold = 150  # Define a threshold for a 'high' arm angle

    arm_angle_sum = 0
    num_samples = len(data)
    num_low_angles = 0

    for index, row in data.iterrows():
        left_arm_angle = row['Left Arm Angle']
        right_arm_angle = row['Right Arm Angle']

        # Calculate the average of left and right arm angles
        avg_arm_angle = (left_arm_angle + right_arm_angle) / 2
        arm_angle_sum += avg_arm_angle

        # Check if the average arm angle is 'low'
        if avg_arm_angle < low_angle_threshold:
            num_low_angles += 1

    # Calculate the average arm angle
    average_arm_angle = arm_angle_sum / num_samples if num_samples > 0 else 0

    # Calculate the proportion of low arm angles
    low_angle_proportion = num_low_angles / num_samples if num_samples > 0 else 0

    # Assign score based on the proportion of low arm angles
    score = 100 - (low_angle_proportion * 100)
    return max(0, round(score, 2))


def measure_smoothness_on_holds(data):
    hold_threshold = 10  # Set a threshold distance to determine if the hands are on holds
    smoothness_scores = []

    hold_x = data['Center of Gravity X']  # Assuming this column holds hold coordinates
    hold_y = data['Center of Gravity Y']

    hands_on_hold = False
    hand_coordinates = []

    for index, row in data.iterrows():
        left_wrist_x = row['left_wrist_X']
        left_wrist_y = row['left_wrist_Y']
        right_wrist_x = row['right_wrist_X']
        right_wrist_y = row['right_wrist_Y']

        # Calculate distances between hands and holds
        for i in range(len(hold_x)):
            left_distance = math.sqrt((hold_x[i] - left_wrist_x) ** 2 + (hold_y[i] - left_wrist_y) ** 2)
            right_distance = math.sqrt((hold_x[i] - right_wrist_x) ** 2 + (hold_y[i] - right_wrist_y) ** 2)

            # Check if hands are on holds
            if left_distance < hold_threshold and right_distance < hold_threshold:
                hands_on_hold = True
                hand_coordinates.append((left_wrist_x, left_wrist_y))
                hand_coordinates.append((right_wrist_x, right_wrist_y))
                break

        # If hands are not on holds anymore, calculate standard deviation
        if not hands_on_hold and hand_coordinates:
            x_coords = [coord[0] for coord in hand_coordinates]
            y_coords = [coord[1] for coord in hand_coordinates]
            x_std_dev = pd.Series(x_coords).std()
            y_std_dev = pd.Series(y_coords).std()

            # Calculate combined standard deviation
            combined_std_dev = (x_std_dev + y_std_dev) / 2
            smoothness_scores.append(combined_std_dev)

            # Reset hand coordinates list
            hand_coordinates = []

    if smoothness_scores:
        average_std_dev = sum(smoothness_scores) / len(smoothness_scores)
        return 100 - average_std_dev  # Return the inverse of the average as the score
    else:
        return 0  # If no data available, return 0 score
    

    # Sample usage of the functions
def main():
    climbing_data = pd.read_csv('your_data.csv')  # Replace 'your_data.csv' with your file name
    
    climbing_data = preprocess_data(climbing_data)  # Preprocess NaN values in the DataFrame


    smoothness_score = measure_smoothness_on_holds(climbing_data)
    arm_angle_score = measure_arm_angle(climbing_data)

    combined_score = (smoothness_score + arm_angle_score) / 2  # Calculate average of the two scores
    print(f"The climber's combined score is {combined_score}.")

if __name__ == "__main__":
    main()


