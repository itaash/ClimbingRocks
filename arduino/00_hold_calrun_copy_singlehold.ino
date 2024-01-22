// FILE: gauge_calrun
// AUTHOR: Sarah Boucher
// PURPOSE: Calibrate gauge measurement or used stored values then print measuremnts to serial
//TO DO: Add multiplexer use

#include "HX711.h"

#include <EEPROM.h>

#define EEPROM_SIZE 100
#define BAUD 9600 

#DEFINE CALWEIGHT 1000

int eeAddress = 0;

bool recal = true; // indicates that we want to enter calibration mode
HX711 scale;

//IO pins
uint8_t buttonTare= 11;
uint8_t dataPin = [7,8,12,13,14,15,16,17,18,19,];
uint8_t clockPin =4;
uint8_t LEDPin = [3,5,6,9,10]; //remove button to use 11 as PWM

//functions - hold_sensors
struct CalValues {
  float scaleFactor;
  long offSet;
};

CalValues calValues_0;
void SaveStruct(int eeAddress, CalValues calValues_0);
CalValues LoadStruct(int eeAddress);
 
//functions - hold_LEDs
//******PUT LED FUNCTION DECLERATIONS HERE******

void setup()
{
  Serial.begin(BAUD);
  pinMode(buttonTare, INPUT_PULLUP);
  calValues_0 = LoadStruct(0);//load off eeprom 

  scale.set_scale(calValues_0.scaleFactor); //read scale from eeprom position 0
  scale.set_offset(calValues_0.offSet); //read offSet from eeprom position 100
  
  scale.begin(dataPin, clockPin);// initiate communication

  if ((calValues_0.scaleFactor == 0.00) || (calValues_0.offSet == 0) || (recal == true)) {


    Serial.println("\nEmpty the scale, press a key to continue");
    while (!Serial.available());
    while (Serial.available()) Serial.read();

    scale.tare(20);
    calValues_0.offSet=scale.get_offset();
    Serial.println(calValues_0.offSet);

    Serial.println("\nPut 1000 gram in the scale, press a key to continue");
    while (!Serial.available());
    while (Serial.available()) Serial.read();

    scale.calibrate_scale(CALWEIGHT, 5);
    calValues_0.scaleFactor=scale.get_scale();
    Serial.println(calValues_0.scaleFactor);

    Serial.println("\nScale is calibrated, calibration values:");
    Serial.print("\nOffset: \t");
    Serial.println(calValues_0.offSet);
    Serial.print("\nScale: \t");
    Serial.println(calValues_0.scaleFactor);

    Serial.println("\nUse this code for setting zero and calibration factor permanently:");

    Serial.println("\nPress a key to continue");
    while (!Serial.available());
    while (Serial.available()) Serial.read();

    SaveStruct( 0, calValues_0);//Save to eeprom 
  
  } else {
    Serial.println("The scale is calibrated... press to continue");
    while (!Serial.available());
    while (Serial.available()) Serial.read();
    scale.set_offset(calValues_0.offSet);
    scale.set_scale(calValues_0.scaleFactor);
  }
}


void loop()
{
  if (digitalRead(buttonTare)==false){
      scale.tare();
      delay(500);
       }

  Serial.println(scale.get_units(15));
  delay(250);
}