import serial
import csv
import time


port = 'COMx'
baud_rate = 9600

arduino_serial = serial.Serial(port, baud_rate)

csv_file_path = 'arduino_data.csv'
csv_file = open(csv_file_path, 'w', newline='')
csv_writer = csv.writer(csv_file)

header = ['Timestamp', 'SensorData1', 'SensorData2', 'SensorData3', 'SensorData4', 'SensorData5','SensorData6', 'SensorData7', 'SensorData8', 'SensorData9', 'SensorData10',]
csv_writer.writerow(header)

# Array to temporarily store data
data_array = []

startTime = time.time()


try:
    while True:
        arduino_data = arduino_serial.readline().decode('utf-8').strip()

        data_values = arduino_data.split(',')
        # Assuming you have two values: timestamp and sensor data
        timestamp = (time.time - startTime) * 1000
        sensor_data = data_values[1]

        # Append data to the array
        data_array.append([timestamp, sensor_data])

        # Optional: Process, validate, or perform error checking on the data here

        # Write data to CSV file in chunks (e.g., every 11 entries)
        if len(data_array) >= 11:
            csv_writer.writerows(data_array)
            data_array = []  # Clear the array

except KeyboardInterrupt:
    print("Stopping data acquisition.")

finally:
    # Write any remaining data in the array to the CSV file
    if data_array:
        csv_writer.writerows(data_array)

    # Close the CSV file and serial connection
    csv_file.close()
    arduino_serial.close()
