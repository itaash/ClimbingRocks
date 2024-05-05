# ClimbingRocks

Welcome to the Climbing Rocks App! This application is designed to to automatically track and analyze users' climbing sessions. It detects climbing holds, records force and position data of the user while they climb, and provides metrics and visualizations of their climb. Additionally, it offers personalized climbing tips based on the user's weakest metric.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Copyright](#copyright)
- [Acknowledgements](#acknowledgements)


## Introduction

The application is designed in PyQt. It uses a TensorFlow model to detect climbing holds, TensorFlow MoveNet to track the user's movements, and force sensors in each climbing hold to record the user's force data. 

The analysis of climb data is done using custom algorithms that evaluate the user's performance based on their force and position data. The app provides visualizations of the user's climb, like a visualisation of their arm angle, progress through the climb, and an indicatator of how theyt used their force. The app also provides personalized climbing tips based on the user's weakest metric.

## Features

- Automatic detection of climbing holds using computer vision techniques.
- Real-time recording of force and position data of the user during climbing sessions.
- Analysis of recorded data to generate metrics and visualizations of the climb.
- Personalized climbing tips based on the user's weakest performance metric.


## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/itaash/ClimbingRocks.git
   cd ClimbingRocks
2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage
Before running the Climbing Rocks App, ensure a webcam or camera is plugged in, and plug the arduino in for recording of force data (optional but recommended). Using a camera app, ensure that the camera is working and the wall is in the center of the frame.

After doing so, execute the following command:

```bash
python ClimbingRocksApp.py
```

1. The app will open into a splash screen, loading the models and ensuring that all sensors are connected. After this completes, the app switches to the Lobby screen where the user can select to start a new climb or view previous climbs and climb scores.
2. To start a new climb, enter the user's name and click 'Start'. The app will switch to the Hold Detection screen where the hold-finding model will try to detect the climbing holds on the wall. If the model is unable to detect the holds, the user can manually select the holds by clicking on them.
3. After the holds are detected, the app switches to the Climbing screen where the user can start climbing. The user can start climbing, and the app will automatically record the user's force and position data as they climb. The recording of data is done in real-time, and automatically stops when the user reaches the top of the wall or falls off.
4. After the climb is completed, the app switches to the Analysis screen where the recorded data is analyzed to generate metrics and visualizations of the climb. The user can view their climb data, like their arm angle, progress through the climb, and an indicator of how they used their force. The app provides a personalized climbing tip based on the user's weakest performance metric.
5. The 'End Climbing Session' button can be clicked to return to the Lobby screen and start a new climb or view previous climbs and climb scores.

## Copyright
This project is the intellectual property of the ClimbingRocks team. Any unauthorized use or distribution of this project without the consent of the Climbing Rocks team is strictly prohibited.

## Acknowledgements
TensorFlow
Arduino
PyQt
OpenCV

Happy climbing!
