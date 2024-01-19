//BLE LED BLINK TEST
//Purpose: Tests HC-05 by blinking on board LED when sending HC-05 a 1 or 0

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
