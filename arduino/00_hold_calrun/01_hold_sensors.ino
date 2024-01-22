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
