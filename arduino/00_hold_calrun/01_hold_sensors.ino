//hold sensor functions

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

void holds_startCal(void){
    for (int i=0;i++;i<NUM_HOLDS){
    calValues_0 = LoadStruct(0+(i*EEPROM_HOLD));//load off eeprom 
  
    holds[i].set_scale(calValues_0.scaleFactor); //read scale from eeprom position 0
    holds[i].set_offset(calValues_0.offSet); //read offSet from eeprom position 100
    
    holds[i].begin(dataPin[i], clockPin);// initiate communication
  
    if ((calValues_0.scaleFactor == 0.00) || (calValues_0.offSet == 0) || (recal == true)) {
  
  
      Serial.print("\nEmpty hold #");
      Serial.print(i);
      Serial.print("press a key to continue\n");
      while (!Serial.available());
      while (Serial.available()) Serial.read();
  
      holds[i].tare(20); //average of 20 readings
      calValues_0.offSet=holds[i].get_offset();
      Serial.println(calValues_0.offSet);
  
      Serial.print("\nPut 1000 gram on hold #");
      Serial.print(i);
      Serial.print("press a key to continue\n");
      while (!Serial.available());
      while (Serial.available()) Serial.read();
  
      holds[i].calibrate_scale(CALWEIGHT, 5); //average of 5 readings
      calValues_0.scaleFactor=holds[i].get_scale();
      Serial.println(calValues_0.scaleFactor);
  
      Serial.println("\nThe hold is calibrated, calibration values:");
      Serial.print("\nOffset: \t");
      Serial.println(calValues_0.offSet);
      Serial.print("\nScale: \t");
      Serial.println(calValues_0.scaleFactor);
  
      SaveStruct(0+(i*EEPROM_HOLD), calValues_0);//Save to eeprom 
    
    } else {
      Serial.println("Using stored values for the hold calibration");
      holds[i].set_offset(calValues_0.offSet);
      holds[i].set_scale(calValues_0.scaleFactor);
    }
  }

  Serial.println("-----Holds ready-----");
}
