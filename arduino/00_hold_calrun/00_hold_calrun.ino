// FILE: gauge_calrun
// AUTHOR: Sarah Boucher
// PURPOSE: Calibrate gauge measurement or used stored values then print measuremnts to serial

#include "HX711.h"

#include <EEPROM.h>

//EEPROM PARAMETERS, BYTES PER HOLD
#define EEPROM_SIZE 100
#define EEPROM_HOLD  20
#define BAUD 9600 

#define CALWEIGHT 1000
#define HOLDCOUNT 10

int eeAddress = 0;

bool recal = true; // indicates that we want to enter calibration mode
//HX711 scale;
HX711 hold0, hold1, hold2, hold3, hold4, hold5, hold6, hold7, hold8, hold9;
HX711 holds[10] = {hold0, hold1, hold2, hold3, hold4, hold5, hold6, hold7, hold8, hold9};

//IO pins
uint8_t buttonTare= 11; //manual Tare button
uint8_t dataPin[] = {7,8,12,13,14,15,16,17,18,19};
uint8_t clockPin =4;
uint8_t LEDPin[] = {3,5,6,9,10}; //remove button to use 11 as PWM
float holdvals[] = {0,0,0,0,0,0,0,0,0,0};

//functions - hold_sensors
struct CalValues {
  float scaleFactor;
  long offSet;
};

CalValues calValues_0;
void SaveStruct(int eeAddress, CalValues calValues_0);
CalValues LoadStruct(int eeAddress);
void holds_startCal(void);
 
//functions - hold_LEDs
//******PUT LED FUNCTION DECLERATIONS HERE******

void setup()
{
  Serial.begin(BAUD);
  pinMode(buttonTare, INPUT_PULLUP);

  //start-up calibration for all holds
  holds_startCal();
}


void loop()
{
  for (int i=0;i++;i<HOLDCOUNT){
  if (digitalRead(buttonTare)==false){ //manual Tare of all holds
      holds[i].tare();
      delay(250);
       }
    
    holdvals[i]=holds[i].get_units(15);

    ////DO LED INDICATION HERE

    
  }
  Serial.print("holdvals:")
  Serial.print(holdvals[i])
  Serial.print(",")
  delay(250);
}
