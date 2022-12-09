// # Target project >>
// # Flow with Application Fan control with Python
// # Example:
// # > Arduino read Fan tacho convert to rpm value <
// # > rpm value send to PC(python) <
// # > PC read fan rpm value 
// # > User set target rpm example 2000 rpm
// # > PC calcuted value of fan speed percentage to match target rpm via PID
// # > PC send value of fan speed percentage  to arduino
// # > Arduino set rpm fan
// # > LOOPBACK

// Version 2

// Reminder use arduino Nano with Shield expension to reduce Tacho noise
// Using Arduino UNO need extra circuit to remove noise
// Depend the Fan that use

//Relay control def
int RELAY = 8;  // Relay to turn on Fan fix problem cannot upload program to arduino

//Fan control def
const byte OC1A_PIN = 9;         // Pwm top Fan
const byte OC1B_PIN = 10;        // Pwm bottom Fan
const word PWM_FREQ_HZ = 25000;  //Adjust this value to adjust the frequency (Frequency in HZ!) (Set currently to 25kHZ)
const word TCNT1_TOP = 16000000 / (2 * PWM_FREQ_HZ);

//Fan read def
const int FAN_IN1 = 3;  // Tach top Fan
const int FAN_IN2 = 2;  // Tach bottom Fan
unsigned long COUNT1 = 0;
unsigned long COUNT2 = 0;
unsigned long previousMillis = 0;
unsigned long RPM1;
unsigned long RPM2;

// Set fan Speed def
int FAN_SPEED1; // Target speed top Fan
int FAN_SPEED2; // Target speed Bottom Fan

void setup() {
  delay(8000);  // 8 second delay for intialze arduino prevent fan 100% speed

  //Setup relay control
  pinMode(RELAY, OUTPUT);

  //Setup setup fan control
  pinMode(OC1A_PIN, OUTPUT);
  pinMode(OC1B_PIN, OUTPUT);
  // Clear Timer1 control and count registers
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  // Set Timer1 configuration
  // COM1A(1:0) = 0b10   (Output A clear rising/set falling)
  // COM1B(1:0) = 0b00   (Output B normal operation)
  // WGM(13:10) = 0b1010 (Phase correct PWM)
  // ICNC1      = 0b0    (Input capture noise canceler disabled)
  // ICES1      = 0b0    (Input capture edge select disabled)
  // CS(12:10)  = 0b001  (Input clock select = clock/1)
  TCCR1A |= (1 << COM1A1) | (1 << COM1B1) | (1 << WGM11);
  TCCR1B |= (1 << WGM13) | (1 << CS10);
  ICR1 = TCNT1_TOP;
  OCR1A = 0;
  OCR1B = 0;

  //Setup for tach sensor
  pinMode(FAN_IN1, INPUT_PULLUP);
  pinMode(FAN_IN2, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(FAN_IN1), COUNTER1, RISING);
  attachInterrupt(digitalPinToInterrupt(FAN_IN2), COUNTER2, RISING);

  Serial.begin(9600);
  Serial.setTimeout(0.1);
}

void loop() {

  // Set Fan speed
  FAN_SPEED1 = 13;
  FAN_SPEED2 = 6;
  setPwmDuty(FAN_SPEED1, 1);
  setPwmDuty(FAN_SPEED2, 2);

  // Turn on relay to turn FAN
  digitalWrite(RELAY, LOW); 

  // Read RPM of Fan
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis > 1000) {
    previousMillis = currentMillis;
    RPM1 = COUNT1 * 30;
    RPM2 = COUNT2 * 30;
    COUNT1 = 0;
    COUNT2 = 0;
  }


  //Serial Output for PC communication
  // Serial.print(COUNT1);
  // Serial.print(" ");
  // Serial.print(COUNT2);
  // Serial.print(" ");
  Serial.print(RPM1);
  Serial.print(",");
  Serial.println(RPM2);

  
}

void COUNTER1() {
  ++COUNT1;
}
void COUNTER2() {
  ++COUNT2;
}
void setPwmDuty(byte duty, int set) {
  if (set == 1) {
    OCR1A = (word)(duty * TCNT1_TOP) / 100;
  } else if (set == 2) {
    OCR1B = (word)(duty * TCNT1_TOP) / 100;
  }
}