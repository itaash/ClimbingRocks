//BLE LED BLINK TEST
//Purpose: Tests HC-05 by blinking on board LED when sending HC-05 a 1 or 0
//Instructions: Follow wiring diagram here (https://howtomechatronics.com/tutorials/arduino/arduino-and-hc-05-bluetooth-module-tutorial/) NOTE 1K and 2k RESISTOR to make a voltage divider on the HC-05's RX pin (HC-05 is powered by 5V but is 3.3 V logic)
//              Power on and pair HC-05 with PC -> this creates a COM port specific to the HC-05 (check device manager for which COM port # was created)
//              *RX and TX pins must be disconected to upload the script
//              Open HC-05's COM port in the serial monitor, baud = 9600, line ending = Both NL & CR. Send 0 or 1 to check connection with onboard LED blinking.

const int LED = 13; //Onboard LED for Uno
char switchstate;

void setup()  {
  Serial.begin(9600); //HC-05 default baud
  pinMode(LED,  OUTPUT);
}

void loop() {
  while(Serial.available()>0){ 
  
    switchstate = Serial.read();
    Serial.print(switchstate);
    Serial.print("\");
    
    delay(15);
    
    if(switchstate  == '1'){//Checking if the value from app is '1', if yes turn LED ON
     digitalWrite(LED, HIGH);
    }
      
    else if(switchstate == '0'){//Else,  if the vaue from app is '0',
     digitalWrite(LED, LOW);
    }
  }
}
