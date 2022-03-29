  #include <DHT11.h>

int pin7 = 7;
int pinA0 = 0;
int pinA1 = 1;

// Pines para salidas leds (dispositivos de control)
int pinD22 = 22; //luz
int pinD24 = 24; //hum suelo
int pinD26 = 26; //hum
int pinD28 = 28; //temperatura

int pinD32 = 32; //temperatura

//Variables para limitar temperaturas
float limT = 24.0; //limite Temeratura
float limH = 60.0; //limite Humedad
float limL = 50.0; //limite intensidad luz
float limS = 800.0; //limite humedad suelo

// Variable definir valores limites
String entrada = "N";

DHT11 dht11(pin7);

void setup() {
  Serial.begin(9600);
  pinMode(pinD22,OUTPUT);
  pinMode(pinD24,OUTPUT);
  pinMode(pinD26,OUTPUT);
  pinMode(pinD28,OUTPUT);
}

void loop() {
  
  int err;
  float temp, hum; //Temperatura y humedad
  float lux = analogRead(pinA0) * 0.9765625; // leer sensor de luz y convertur a lux (0 a 1000 lux)
  float humS = analogRead(pinA1);  // Humedad del suelo

  //leer valor
  String unidad = "";
  float valor = -1;
  int init = 0;
  int fin = 0; 
  entrada = Serial.readStringUntil('\n');
  fin = entrada.indexOf(',',init);
  valor = entrada.substring(init,fin).toFloat();
  unidad = entrada.substring(fin+1,fin+2);
  Serial.print(valor);
  Serial.print("+");
  Serial.print(unidad);
  
  if (unidad == "H" || unidad == "T" || unidad == "L" || unidad == "S"){  // -1 No se recibe nada, 13 devulve luego de una lectura (bin)
    //Humedad
    if (unidad == "H"){
      for (int i = 0;i<3;i++){
        digitalWrite(pinD26, HIGH);
        delay(100);
        digitalWrite(pinD26, LOW);
        delay(200);
      }
      limH = valor;
    }
    
    //Temperatura
    if (unidad == "T"){
      for (int i = 0;i<3;i++){
        digitalWrite(pinD28, HIGH);
        delay(100);
        digitalWrite(pinD28, LOW);
        delay(200);
      }
      limT = valor;
    }
    
    //Luz (L->76)
    if (unidad == "L"){
      for (int i = 0;i<3;i++){
        digitalWrite(pinD22, HIGH);
        delay(100);
        digitalWrite(pinD22, LOW);
        delay(200);
      }
      limL = valor;
    }
    
    //Hum Suelo (S->83)
    if (unidad == "S"){
      for (int i = 0;i<3;i++){
        digitalWrite(pinD24, HIGH);
        delay(100);
        digitalWrite(pinD24, LOW);
        delay(200);
      }
      limS = valor;
    }
    
  } 

  //DATOS QUE SE IMPRIMEM POR SERIE

  //Sensores
  if ((err = dht11.read(hum, temp)) == 0) {
    Serial.print("-");
    Serial.print(temp);
    Serial.print(",");
    Serial.print(hum);
    Serial.print(",");
  } else {
    Serial.println();
    Serial.print("Error Num:");
    Serial.print(err);
    Serial.println();
  }

  Serial.print(lux);
  Serial.print(",");
  Serial.print(humS);
  Serial.print(",");

  //Limites
  
  Serial.print(limT);
  Serial.print(",");
  Serial.print(limH);
  Serial.print(",");
  Serial.print(limL);
  Serial.print(",");
  Serial.print(limS);
  Serial.print(",");
  
  Serial.println("");


  //Control temperatura
  if (temp < limT){
    digitalWrite(pinD28,HIGH);
  } else {
    digitalWrite(pinD28,LOW);
  }

  //Control humedad
  if (hum < limH){
    digitalWrite(pinD26,HIGH);
  } else {
    digitalWrite(pinD26,LOW);
  }

  //Control intensidad luz
  if (lux > limL){
    digitalWrite(pinD22,HIGH);
  } else {
    digitalWrite(pinD22,LOW);
  }

  //Control hum suelo
  if (humS > limS){
    digitalWrite(pinD24,HIGH);
  } else {
    digitalWrite(pinD24,LOW);
  }
  
  delay(1000);
}

//Para sensor de humedad suelo:
//if(valor >= 1000)-> El sensor no está en el suelo o está desconectado
//if(valor < 1000 && valor >= 600)-> El suelo está SECO
//if(valor < 600 && valor >= 370) -> El suelo es HÚMEDO
//if(valor < 370) -> Sensor en AGUA

//Consultar: ls -l /dev | grep ACM
//conceder permisos puertos: sudo chmod 777 /dev/ttyACM0
