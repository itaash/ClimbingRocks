// FILE: gauge_calrun
// AUTHOR: Sarah Boucher
// PURPOSE: Calibrate gauge measurement or used stored values then print measuremnts to serial
//TO DO: Add multiplexer use

#include "HX711.h"

#include <EEPROM.h>

#define MCP_ADDR (0)
#define EEPROM_SIZE 100

MCP23017 mcp(MCP_ADDR);
int eeAddress = 0;

bool recal = true; // indicates that we want to enter calibration mode
HX711 scale;
byte buttonTare= 2;

uint8_t dataPin = 3;
uint8_t clockPin = 2;

struct CalValues {
  float scaleFactor;
  long offSet;
};

CalValues calValues_0;

void SaveStruct(int eeAddress, CalValues calValues_0) {
  EEPROM.put(eeAddress, calValues_0);
  Serial.println( "Save custom object to EEPROM: " );
  Serial.println( calValues_0.scaleFactor );
  Serial.println( calValues_0.offSet );
}

CalValues LoadStruct(int eeAddress) {
  EEPROM.get( eeAddress, calValues_0 );
  Serial.println( "Read custom object from EEPROM: " );
  Serial.print("scale: ");Serial.println( calValues_0.scaleFactor );
  Serial.print("offset: ");Serial.println( calValues_0.offSet );
  return calValues_0;
}


void setup()
{
  Serial.begin(115200);
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

    scale.calibrate_scale(1000, 5);
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
