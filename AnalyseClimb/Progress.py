import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
from matplotlib.backends.backend_agg import FigureCanvasAgg


#holds_reached, total_holds, holds_coordinates, starting holds and ending holds to incorporate

# Preprocess data, forward fill
def preprocess_data(df):
    df.fillna(method='ffill', inplace=True)  # Fill NaN values in the DataFrame with last valid observation
    return df

def calculate_distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Check if both wrists are close enough to the designated hold 
def check_wrist_on_hold(row, holdCoordinates, threshold):
    left_wrist_distance = calculate_distance(row['left_wrist_X'], row['left_wrist_Y'], start_hold_x, start_hold_y)
    right_wrist_distance = calculate_distance(row['right_wrist_X'], row['right_wrist_Y'], start_hold_x, start_hold_y)
    return (left_wrist_distance <= threshold) and (right_wrist_distance <= threshold)

# Function to measure hesitation on each hold
def measure_hesitation_on_holds(data, holdsCoordinates, threshold_distance, start_time, end_time):
    holds_hesitation = {}  # Dictionary to store time spent on each hold

    timer_started = False
    current_hold = None
    hold_start_time = None

    for index, row in data.iterrows():
        feet_off_ground = check_feet_off_ground(row, start_hold_x, start_hold_y, threshold_distance)
        if feet_off_ground and check_wrist_on_hold(row, start_hold_x, start_hold_y, end_hold_x, end_hold_y, threshold_distance):
            if not timer_started:
                timer_started = True

            if timer_started:
                for hold in holdsCoordinates:  # 'holds_coordinates' contains the coordinates of each hold
                    if check_wrist_on_hold(row, hold[0], hold[1], hold[0], hold[1], threshold_distance) and current_hold != hold:
                        if current_hold is not None:
                            hold_end_time = row['Timestamp(ms)']
                            hold_duration = hold_end_time - hold_start_time
                            holds_hesitation[current_hold] = hold_duration

                        current_hold = hold
                        hold_start_time = row['Timestamp(ms)']

        else:
            if timer_started:
                end_time = row['Timestamp(ms)']
                break

    if current_hold is not None and hold_start_time is not None:
        hold_end_time = end_time
        hold_duration = hold_end_time - hold_start_time
        holds_hesitation[current_hold] = hold_duration

    return holds_hesitation

# Function to measure climbing duration and count holds reached
def measure_climbing_duration(data):
    timer_started = False
    start_time = None
    holds_reached = 0

    for index, row in data.iterrows():
        check_wrist_on_hold(row, start_hold_x, start_hold_y, end_hold_x, end_hold_y, threshold_distance)
        if not timer_started:
            timer_started = True
            start_time = row['Timestamp(ms)']
            holds_reached += 1  # Increment the count of holds reached
        else:
            # if timer_started:
            end_time = row['Timestamp(ms)']
            return start_time, end_time, holds_reached

    return None, None, None


# Function to count holds reached before falling
def count_holds_reached(climbing_data, start_hold_x, start_hold_y, end_hold_x, end_hold_y, ground_x, ground_y, threshold_distance, threshold_ground_distance):
    start_time, end_time, holds_reached = measure_climbing_duration(climbing_data, start_hold_x, start_hold_y, end_hold_x, end_hold_y,
        ground_x, ground_y, threshold_distance, threshold_ground_distance
    )

    if holds_reached is not None:
        print(f"The climber reached {holds_reached} holds before falling.")
    else:
        print("The climber did not fall during the climb.")


# Calculate score based on climbing duration and holds reached
def calculate_score(climbing_duration, max_score, holds_reached, total_holds):
    if climbing_duration is not None:
        if holds_reached == total_holds:  # Climber completed the route
            return max_score  # Return the maximum possible score (100)
        else:
            missed_holds = total_holds - holds_reached
            penalty = 20 * missed_holds  # Subtract 20 points for each hold missed
            score = max_score - penalty
            return max(0, round(score, 2))  # Ensure score doesn't go below 0
    return 0


def calculate_hesitation_score(holds_hesitation):
    total_time = sum(holds_hesitation.values())
    total_holds = len(holds_hesitation)

    if total_holds == 0 or total_time == 0:
        return 0

    average_time_per_hold = total_time / total_holds
    max_score = 100

    # Calculate the deviation of each hold's time from the average
    deviations = [abs(time - average_time_per_hold) for time in holds_hesitation.values()]

    # Calculate the score based on the deviation from average time spent on each hold
    max_deviation = max(deviations)
    score = max_score - ((max_deviation / average_time_per_hold) * max_score)

    return max(0, round(score, 2))


# Function to calculate combined score by averaging climbing duration score and hesitation score
def calculate_combined_score(climbing_duration_score, hesitation_score):
    return (climbing_duration_score + hesitation_score) / 2
    



def calculateProgress(climbData, holdsCoordinates):
    threshold_distance = 10 # specify the threshold distance for proximity to the holds

    climbing_data = preprocess_data(climbData)  # Preprocess NaN values in the DataFrame

    start_time, end_time, _ = measure_climbing_duration(climbing_data, holdsCoordinates, threshold_distance)

    if start_time is not None and end_time is not None:
        climbing_duration = end_time - start_time
        holds_hesitation = measure_hesitation_on_holds(
            climbing_data, holdsCoordinates,
            threshold_distance, start_time, end_time
        )

        hesitation_score = calculate_hesitation_score(holds_hesitation)
        climbing_duration_score = calculate_score(climbing_duration, max_score, holds_reached, total_holds)

        combined_score = calculate_combined_score(climbing_duration_score, hesitation_score)
        return combined_score, climbing_duration_score, hesitation_score

    else:
        holds_reaches = count_holds_reached(climbing_data, holdsCoordinates, threshold_distance)

        climbing_duration_score = calculate_score(climbing_duration, max_score, holds_reached, total_holds)
        return combined_score, climbing_duration_score, hesitation_score

#NEED TO MAKE SURE HOLDS_HESITATION IS THE RIGHT FORMAT FOR TESTING
def visualiseProgress(holds_hesitation):

    data = pd.DataFrame[holds_hesitation]
    colors = sb.color_palette("viridis", len(data.columns))

    # Create stacked bar chart with specified parameters
    graph = data.plot(kind='bar', stacked=True, color=colors, width=1, legend=False, figsize=(3, 6))

    plt.ylabel('Time')
    plt.xticks([])
    plt.title('Time on each hold')

    # Get the figure
    fig = graph.get_figure()

    # Render the figure as an image
    canvas = FigureCanvasAgg(fig)
    canvas.draw()

    # Convert the image to numpy array
    img = np.array(canvas.renderer.buffer_rgba())

    plt.close()  # Close the figure to free up resources

    return img
