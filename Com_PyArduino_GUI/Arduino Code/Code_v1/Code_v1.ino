// Version 1
// Problem cannot send multiple value

int x;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(0.1);
}

void loop() {
  while (!Serial.available())
    ;
  x = Serial.readString().toInt();
  
  Serial.print(x);
}
