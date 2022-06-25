#include <SoftwareSerial.h>
SoftwareSerial myEspSerial(10, 11);    // RX=10, TX=11; ARD, 10 es blanco y RX. en ESP, blanco es TX.

String container1= "A:60";
String container2= "B:80";

void setup() {
  Serial.begin(9600);
  myEspSerial.begin(9600);
  delay(5000);
  myEspSerial.flush();
}

void loop() {
  // first msg.
  myEspSerial.print(container1);
  myEspSerial.flush();
  delay(3000);
  // second msg.
  myEspSerial.print(container2);
  myEspSerial.flush(); 
  delay(3000);
}
