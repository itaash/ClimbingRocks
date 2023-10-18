#For HC-05 Module

import serial

ports = serial.tools.list_ports.comports()
for p in ports:
    print(p.device)
print(len(ports), 'Ports Available')

serialPort = serial.Serial(port='COM6', baudrate=9600, timeout=0, parity=serial.PARITY_EVEN, stopbits=1)
size = 1024

while 1:
    data = serialPort.readline(size)

    if data:
        print(data)
