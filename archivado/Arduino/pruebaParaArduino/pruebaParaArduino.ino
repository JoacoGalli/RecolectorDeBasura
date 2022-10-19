#include <SoftwareSerial.h>
SoftwareSerial myEspSerial(10, 11);    // RX=10, TX=11; ARD, 10 es blanco y RX. en ESP, blanco es TX.

String container1= "A:60";
String container2= "B:";
int TRIG = 6;
int ECO = 5;
int DURACION;
int DISTANCIA;
float PORCENTAJE;
void setup() {
  Serial.begin(9600);
  myEspSerial.begin(9600);
  delay(5000);
  myEspSerial.flush();
  pinMode(TRIG, OUTPUT);
  pinMode(ECO, INPUT);
}

void loop() {
  // first msg.
  digitalWrite(TRIG, HIGH);
  delay(1);
  digitalWrite(TRIG, LOW);
  DURACION = pulseIn(ECO, HIGH);
  DISTANCIA = DURACION / 58.2;   // por especificacion del fabricante

  myEspSerial.print(container1);
  myEspSerial.flush();
  delay(3000);
  // second msg.
  myEspSerial.print(container2 + DISTANCIA);
  myEspSerial.flush(); 
  delay(3000);
}
