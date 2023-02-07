unsigned long previousMillis = 0;
const int interval = 10000;
int currentstate;

int count_digit(int number) {
   return int(log10(number * 100) + 2); // per inviare anche numeri decimali
}

void setup() {
  // put your setup code here, to run once:
  // 3 pin input sensori e 2 pin in output
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);

  currentstate = 0;
}

void loop() {
  // put your main code here, to run repeatedly:
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    char SoL = '\xff';
    Serial.print(SoL);
    float randomValue = random(12, 22);
    int pack_size = count_digit(randomValue);
    Serial.print(pack_size);
    Serial.print(randomValue);
    Serial.print("Tsensor_0");
    char EoL = '\xfe';
    Serial.print(EoL);    
  }
  if(Serial.available() > 0){
    char val = Serial.read();

    int futurestate;
    if(currentstate == 0 && val == 'A') futurestate = 1;
    if(currentstate == 1 && val == '1') futurestate = 2; //acceso
    if(currentstate == 2 && val == 'S') futurestate = 3;
    if(currentstate == 3 && val == '1') futurestate = 4; //spento
    if(currentstate == 1 && val == '2') futurestate = 5; //acceso
    if(currentstate == 5 && val == 'S') futurestate = 6;
    if(currentstate == 6 && val == '2') futurestate = 7; //spento

    if(currentstate != futurestate){
      if(futurestate == 2) digitalWrite(13,HIGH);
      if(futurestate == 4) {
        digitalWrite(13,LOW);
        futurestate = 0;
      }
      if(futurestate == 5) digitalWrite(12,HIGH);
      if(futurestate == 7) {
        digitalWrite(12,LOW);
        futurestate = 0;
      }
    }
    else{
    	if(currentstate < 2) futurestate = 0;
      if(currentstate >= 2 && currentstate < 4) futurestate = 2;
      if(currentstate >= 5) futurestate = 5;
    }
    
    currentstate = futurestate;
  }
}

