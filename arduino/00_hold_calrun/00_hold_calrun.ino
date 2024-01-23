// FILE: 00_hold_calrun
// AUTHOR: Sarah Boucher
// PURPOSE: Calibrate gauge measurement or used stored values then print measuremnts to serial & update LEDs

#include "HX711.h"
#include <EEPROM.h>
#include <FastLED.h>

//EEPROM PARAMETERS, BYTES PER HOLD
#define EEPROM_SIZE 100
#define EEPROM_HOLD  20
#define BAUD 9600 

//HOLD PARAMETERS
#define CALWEIGHT 1000
#define HOLDCOUNT 10
//max value for maping hold reading, grams - edit as needed or receive from rPi
#define MAXVAL 50000 

//LED PARAMETERS
#define NUM_LEDS 100
#define LEDS_PER_INPUT 10
//LEDPin definition, use any PWM pin: 3,5,6,9,10,(11 - in use)
#define LEDPin 6
CRGB leds[NUM_LEDS];

bool recal = true; // indicates that we want to enter calibration mode
int eeAddress = 0;

//HOLD INDICES
HX711 hold0, hold1, hold2, hold3, hold4, hold5, hold6, hold7, hold8, hold9;
HX711 holds[10] = {hold0, hold1, hold2, hold3, hold4, hold5, hold6, hold7, hold8, hold9};
float holdvals[] = {0,0,0,0,0,0,0,0,0,0};

//LED INDICES
uint8_t ledIndices[HOLDCOUNT][LEDS_PER_INPUT] = {
  {0,1,2,3,4,5,6,7,8,9},
  {10,11,12,13,14,15,16,17,18,19},
  {20,21,22,23,24,25,26,27,28,29},
  {30,31,32,33,34,35,36,37,38,39},
  {40,41,42,43,44,45,46,47,48,49},
  {50,51,52,53,54,55,56,57,58,59},
  {60,61,62,63,64,65,66,67,68,69},
  {70,71,72,73,74,75,76,77,78,79},
  {80,81,82,83,84,85,86,87,88,89},
  {90,91,92,93,94,95,96,97,98,99}
};

//IO PINS
uint8_t buttonTare= 11; //manual Tare button
uint8_t dataPin[] = {7,8,12,13,14,15,16,17,18,19};
uint8_t clockPin =4;
//uint8_t LEDPin = 6; //use any PWM pin: 3,5,6,9,10,(11 - in use) PWM pins

//FUNCTIONS DELCARATION - hold_sensors
struct CalValues {
  float scaleFactor;
  long offSet;
};

CalValues calValues_0;
void SaveStruct(int eeAddress, CalValues calValues_0);
CalValues LoadStruct(int eeAddress);
void holds_startCal(void);
 
//FUNCTIONS DECLARATION - hold_LEDs
//******PUT LED FUNCTION DECLERATIONS HERE******

void setup()
{
  Serial.begin(BAUD);
  pinMode(buttonTare, INPUT_PULLUP);

  //OPTIONAL - Yellow LED lights signifying calibrating
  for (int i=0;i++;i<HOLDCOUNT){
    for (int led = 0; led< LEDS_PER_INPUT; led++){
        leds[ledIndices[i][led]]=CRGB(128,128,0); //set LEDs yellow
      }
  }
  FastLED.show();
  
  //start-up calibration for all holds
  holds_startCal();

  //setup for RGB LEDs
  FastLED.addLeds<WS2811, LEDPin,GRB>(leds,NUM_LEDS);

  //OPTIONAL - Green LED lights signifying ready
  for (int i=0;i++;i<HOLDCOUNT) {
    for (int led = 0; led< LEDS_PER_INPUT; led++){
        leds[ledIndices[i][led]]=CRGB(0,128,0); //set LEDs green
      }
  }
  FastLED.show();
  
  //CSV saving to start after "READY" received
  Serial.println("READY");
}


void loop()
{
  //loop through reading all holds and updating LEDs
  for (int i=0;i++;i<HOLDCOUNT){
    //manual tare of all holds if button pressed
    if (digitalRead(buttonTare)==false){
        holds[i].tare();
        delay(250);
         }

    //read hold, average from 10 readings
    holdvals[i]=holds[i].get_units(10); 
    int brightness = map(holdvals[i], 0, MAXVAL, 0, 255); //map hold value to LED brightness

    //set hold's LEDs
    for (int led = 0; led< LEDS_PER_INPUT; led++){
      leds[ledIndices[i][led]]=CRGB(brightness,0,0); //set LEDs red brightness based on input value
    }
    
  }
  //Update LEDs and send values to rPi
  FastLED.show();
  Serial.print("holdvals:");
  for (int i=0;i++;i<HOLDCOUNT){
  Serial.print(holdvals[i]);
  Serial.print(",");
  }
  delay(250);
}
