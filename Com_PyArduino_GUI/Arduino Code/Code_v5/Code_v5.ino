// # Target project >>
// # Flow with Application Fan control with Python
// # Example:
// # > Arduino read Fan tacho convert to rpm value <
// # > rpm value send to PC(python) <
// # > PC read fan rpm value <
// # > User set target rpm example 2000 rpm <
// # > PC calcuted value of fan speed percentage to match target rpm via PID < bad result
// # > PC send value of fan speed percentage  to arduino <
// # > Arduino set rpm fan <
// # > LOOPBACK <

// Version 5

// Reminder use arduino Nano with Shield expension to reduce Tacho noise
// Using Arduino UNO need extra circuit to remove noise
// Depend the Fan that use

//Relay control def
int RELAY = 8;  // Relay to turn on Fan fix problem cannot upload program to arduino

//Fan control def
const byte OC1A_PIN = 9;         // Pwm top Fan
const byte OC1B_PIN = 10;        // Pwm bottom Fan
const word PWM_FREQ_HZ = 60000;  //Adjust this value to adjust the frequency (Frequency in HZ!) (Set currently to 25kHZ)
const word TCNT1_TOP = 16000000 / (2 * PWM_FREQ_HZ);

//Fan read def
const int FAN_IN1 = 2;  // Tach top Fan
const int FAN_IN2 = 3;  // Tach bottom Fan
unsigned long COUNT1 = 0;
unsigned long COUNT2 = 0;
unsigned long previousMillis = 0;
unsigned long RPM1;
unsigned long RPM2;

// Set fan Speed def
int FAN_SPEED1 = 0;  // Target speed top Fan
int FAN_SPEED2 = 0;  // Target speed Bottom Fan
int const_SPEED = 50;
int PC_control = 0;

// Variable for serial communication
const byte numChars = 32;
char receivedChars[numChars];
boolean newData = false;
char tempChars[sizeof(receivedChars)];
char *strings[32];
char *ptr = NULL;
const char *delimiter = ",";


void setup() {
  delay(1000);  // 8 second delay for intialze arduino prevent fan 100% speed

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

  // Serial Communication loop
  recvWithStartEndMarkers();  // Where the read data from PC happen with using Marker <Data> out as receivedChars
  replyToPython();            // Send any data to PC through serial
  byte index = 0;
  strcpy(tempChars, receivedChars);    // Copy array to preserve original // receivedChars from recvWithStartMarkers()
  ptr = strtok(tempChars, delimiter);  // Split array with ","
  while (ptr != NULL) {
    strings[index] = ptr;
    index++;
    ptr = strtok(NULL, delimiter);
  }
  // Value from PC set the speed of fan
  if (Serial.available() > 0) {
    FAN_SPEED1 = atoi(strings[0]);
    FAN_SPEED2 = atoi(strings[1]);
    PC_control = 1;

    if(FAN_SPEED1 >=1000 && FAN_SPEED2 >=1000) {
      PC_control = 0;
    }
  } 

  if(PC_control  == 0){
    FAN_SPEED1 = const_SPEED;
    FAN_SPEED2 = const_SPEED;
  }
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
void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      } else {
        receivedChars[ndx] = '\0';  // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }

    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}
void replyToPython() {
  if (newData == true) {
    newData = false;
    //Serial Output for PC communication
    // Serial.print(COUNT1);
    // Serial.print(" ");
    // Serial.print(COUNT2);
    // Serial.print(" ");
    Serial.print(RPM1);
    Serial.print(",");
    Serial.print(RPM2);
    Serial.print(",<");
    Serial.print(receivedChars);
    Serial.print(">,");
    ///////////////////////
    // Serial.print(strings[0]);
    // Serial.print(",");
    // Serial.print(strings[1]);
    ///////////////////////
    Serial.print(FAN_SPEED1);
    Serial.print(",");
    Serial.print(FAN_SPEED2);
  }
}
