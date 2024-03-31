import cv2
import numpy as np
import time

"""
Hough Circle Transform is used to detect circles in an image. It is a popular technique for circle detection because it is simple and effective.
Below are the effects of increasing the parameters of the Hough Circle Transform:
dp	- Decreases the accumulator resolution.<br>- More precise detection but slower computation.
minDist	- Increases the minimum distance between detected circles.<br>- Reduces false positives but may miss closely spaced circles.
param1	- Increases the gradient value threshold.<br>- Reduces false positives but may miss faint circles.
param2	- Decreases the circle center threshold.<br>- More circles detected but also increases false positives.
minRadius	- Increases the minimum circle radius to consider.<br>- Ignores smaller circles, reducing false positives but may miss smaller objects.
maxRadius	- Increases the maximum circle radius to consider.<br>- Ignores larger circles, reducing false positives but may miss larger objects.
"""

def detect_circles(image):
    
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    # Apply Hough Circle Transform
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30,
                               param1=125, param2=19, minRadius=8, maxRadius=25)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        # Draw detected circles
        for (x, y, r) in circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)


        

    return image

def main():
    # Open webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Couldn't open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't capture frame")
            break

        # Detect circles
        output = detect_circles(frame)

        # Display output
        cv2.imshow("Detected Circles", output)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(1/15)

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()