//Pins
static const uint8_t sensor[]={A0};
static const uint8_t LED[]={0};

double Th = 2.5; //Voltage threshold

double raw[] = {0};

void setup() {

  //set pinmodes
  for (int i=0; i<1; i++){
    pinMode(LED[i],OUTPUT);
  }

  Serial.begin(9600); //baud
  Serial.println("Serial started");
}

void loop() {
  while(!Serial.available()){
    for (int i=0; i<1; i++){
      raw[i] = analogRead(sensor[i]);
      Serial.println(raw[i]);
      
      if (raw[i]>=Th){
        digitalWrite(LED[i],HIGH);
      }
      else{
        digitalWrite(LED[i],LOW);
      }
    }
  }
}

