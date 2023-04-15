
/******************************************* INCLUDES *******************************************/

// DHT library
#include "DHT.h"

// MPU6050 libraries
#include "I2Cdev.h"
#include "MPU6050.h"
#include "Wire.h"

// WIFI libraries
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include "secrets.h"

// RFID libraries
#include <SPI.h>
#include <MFRC522.h>

/******************************************* DEFINES *******************************************/

// debug defines
#define DEBUG
#define DEBUG_WIFI

// dht pin define
#define DHT11_PIN 10

// SPI pins defines
#define SS_PIN 2
#define RST_PIN 0

// diode pin
#define LED_PIN 15

/******************************************* MPU PARAMS *******************************************/

MPU6050 accelgyro;

int16_t gx, gy, gz;

const uint8_t BUFFER_SIZE = 10;
uint8_t fifo_ptr = 0;

int16_t ax_FIFO[BUFFER_SIZE*2] = {0}, ay_FIFO[BUFFER_SIZE*2] = {0}, az_FIFO[BUFFER_SIZE*2] = {0};

int32_t ax_sum = 0, ay_sum = 0, az_sum = 0;
int32_t ax_dif_sum = 0, ay_dif_sum = 0, az_dif_sum = 0; 

double ax, ay, az, magnitude;
double ax_diff, ay_diff, az_diff, diff_magnitude;

/******************************************* END MPU PARAMS *******************************************/

/******************************************* DHT PARAMS *******************************************/

DHT dht11(DHT11_PIN ,DHT11);

float hum, temp;

/******************************************* END DHT PARAMS *******************************************/

/******************************************* WIFI PARAMS *******************************************/

ESP8266WiFiMulti WiFiMulti;

/******************************************* END WIFI PARAMS *******************************************/


/******************************************* MFRC522 PARAMS *******************************************/

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.

/******************************************* END MFRC522 PARAMS *******************************************/

String content = "";
String package_id = "";
String courier_id = "";

/******************************************* SETUP *******************************************/

void setup() {

  // initialize I2C, Serial, SPI
  Wire.begin();
  Serial.begin(115200);
  SPI.begin();

  // initialize MPU
#ifdef DEBUG
  Serial.println("Initializing I2C devices...");
#endif
  accelgyro.initialize();

  // verify MPU connection
#ifdef DEBUG
  Serial.println("Testing device connections...");
  Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");
#endif

  // initialize dht sensor
  dht11.begin();

  pinMode(LED_PIN, OUTPUT);

  // add access point
  WiFiMulti.addAP(ssid, password);

  // initialize MFRC522
  mfrc522.PCD_Init(); 
#ifdef DEBUG
  Serial.println("Approximate your card to the reader...");
  Serial.println();
  Serial.print("UID tag :");
#endif

  // waiting for entering package id
  digitalWrite(LED_PIN, HIGH);
  while(package_id == "") {
    
    // waiting for package RFID card
    if(!mfrc522.PICC_IsNewCardPresent()) {
      Serial.println(package_id);
      continue;
    }
  
    // reading card value
    if(!mfrc522.PICC_ReadCardSerial()){
      continue;
    }

    // reading content
    content = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) 
    {
      Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
      Serial.print(mfrc522.uid.uidByte[i], HEX);
      content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
      content.concat(String(mfrc522.uid.uidByte[i], HEX));
    }
    Serial.println();
    package_id = content;
  }
  digitalWrite(LED_PIN, LOW);

#ifdef DEBUG
//  Serial.print("acc_x\tacc_y\tacc_z\tmag\tdif_x\tdif_y\tdif_z\tdiff_mag\ttemp\thum\n");
    Serial.print("dif_x\tdif_y\tdif_z\tdiff_mag\ttemp\thum\n");
#endif
}

/******************************************* MAIN LOOP *******************************************/

void loop() {

  /******************************************* COURIER ID *******************************************/

  // waiting for entering package id
  while(courier_id == "") {
    
    // waiting for package RFID card
    if(!mfrc522.PICC_IsNewCardPresent()) {
      digitalWrite(LED_PIN, HIGH);
      delay(250);
      digitalWrite(LED_PIN, LOW);
      delay(250);
      continue;
    }
  
    // reading card value
    if(!mfrc522.PICC_ReadCardSerial()){
      digitalWrite(LED_PIN, HIGH);
      delay(250);
      digitalWrite(LED_PIN, LOW);
      delay(250);
      continue;
    }

    // reading content
    content = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) 
    {
      Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? "0" : " ");
      Serial.print(mfrc522.uid.uidByte[i], HEX);
      content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
      content.concat(String(mfrc522.uid.uidByte[i], HEX));
    }
    if(content != package_id) {
      courier_id = content;
    }
  }

  if(mfrc522.PICC_IsNewCardPresent()) {
    if(mfrc522.PICC_ReadCardSerial()) {
      content = "";
      for (byte i = 0; i < mfrc522.uid.size; i++) 
      {
        Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(mfrc522.uid.uidByte[i], HEX);
        content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : ""));
        content.concat(String(mfrc522.uid.uidByte[i], HEX));
      }
      Serial.println();
      if(courier_id != content && package_id != content) {
        courier_id = content;
      }
    }
  }

  /******************************************* MPU *******************************************/
  
  // read raw accel/gyro measurements from device
  accelgyro.getMotion6(&ax_FIFO[fifo_ptr], &ay_FIFO[fifo_ptr], &az_FIFO[fifo_ptr], &gx, &gy, &gz);
  // update second part of fifp
  ax_FIFO[fifo_ptr+BUFFER_SIZE] = ax_FIFO[fifo_ptr];
  ay_FIFO[fifo_ptr+BUFFER_SIZE] = ay_FIFO[fifo_ptr];
  az_FIFO[fifo_ptr+BUFFER_SIZE] = az_FIFO[fifo_ptr];

  // calculate new diff and 
//  ax_sum = 0, ay_sum = 0, az_sum = 0;
  ax_dif_sum = 0, ay_dif_sum = 0, az_dif_sum = 0; 
  for(int i = 0; i < BUFFER_SIZE; i++) {
    // 
//    ax_sum += ax_FIFO[i+fifo_ptr];
//    ay_sum += ay_FIFO[i+fifo_ptr];
//    az_sum += az_FIFO[i+fifo_ptr];
    
    if(i + fifo_ptr == 0) {
      ax_dif_sum += abs(ax_FIFO[i+fifo_ptr]-ax_FIFO[i+fifo_ptr+BUFFER_SIZE*2-1]);
      ay_dif_sum += abs(ay_FIFO[i+fifo_ptr]-ay_FIFO[i+fifo_ptr+BUFFER_SIZE*2-1]);
      az_dif_sum += abs(az_FIFO[i+fifo_ptr]-az_FIFO[i+fifo_ptr+BUFFER_SIZE*2-1]);
    } else {
      ax_dif_sum += abs(ax_FIFO[i+fifo_ptr]-ax_FIFO[i+fifo_ptr-1]);
      ay_dif_sum += abs(ay_FIFO[i+fifo_ptr]-ay_FIFO[i+fifo_ptr-1]);
      az_dif_sum += abs(az_FIFO[i+fifo_ptr]-az_FIFO[i+fifo_ptr-1]);
    }
  }

  if(++fifo_ptr >= BUFFER_SIZE) {
    fifo_ptr = 0;
  }

  // calculate mean
//  ax = double(ax_sum)/BUFFER_SIZE;
//  ay = double(ay_sum)/BUFFER_SIZE;
//  az = double(az_sum)/BUFFER_SIZE;
  
  ax_diff = double(ax_dif_sum)/BUFFER_SIZE;
  ay_diff = double(ay_dif_sum)/BUFFER_SIZE;
  az_diff = double(az_dif_sum)/BUFFER_SIZE;
  
//  ax = double(ax) / 16384;
//  ay = double(ay) / 16384;
//  az = double(az) / 16384;

  // calculate magnitude
//  magnitude = sqrt(ax*ax+ay*ay+az*az);
  diff_magnitude = sqrt(ax_diff*ax_diff+ay_diff*ay_diff+az_diff*az_diff);

  /******************************************* DHT *******************************************/

  // read temperature and humidity
  temp = dht11.readTemperature();
  hum = dht11.readHumidity();

  /******************************************* DEBUGING *******************************************/

  if((WiFiMulti.run() == WL_CONNECTED)) {
    HTTPClient http;

    String http_msg;

    http_msg = "{";
    http_msg += "\"pack_id\":\""; http_msg += package_id; http_msg += "\",";
    http_msg += "\"courier_id\":\""; http_msg += courier_id; http_msg += "\",";
    http_msg += "\"mag_diff\":\""; http_msg += diff_magnitude; http_msg += "\",";
    http_msg += "\"temp\":\""; http_msg += temp; http_msg += "\",";
    http_msg += "\"hum\":\""; http_msg += hum; http_msg += "\"";
    http_msg += "}";

#ifdef DEBUG_WIFI
  Serial.print("[HTTP] begin...\n");
  Serial.print("[HTTP] message: ");
  Serial.println(http_msg);
#endif
    
    http.begin("http://192.168.83.221:5000/KPMP-data"); //HTTP
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(http_msg);
    String payload = http.getString();

#ifdef DEBUG_WIFI
    Serial.print("[HTTP] response: ");
    Serial.println(httpCode);
    Serial.println(payload);
#endif

    http.end();
  } else {
#ifdef DEBUG_WIFI
    Serial.print("[HTTP] Wifi connection failed");
#endif
  }

#ifdef DEBUG
//  Serial.print(ax); Serial.print("\t");
//  Serial.print(ay); Serial.print("\t");
//  Serial.print(az); Serial.print("\t");
//  Serial.print(magnitude); Serial.print("\t");
  Serial.print(package_id); Serial.print("\t");
  Serial.print(courier_id); Serial.print("\t");
  Serial.print(ax_diff); Serial.print("\t");
  Serial.print(ay_diff); Serial.print("\t");
  Serial.print(az_diff); Serial.print("\t");
  Serial.print(diff_magnitude); Serial.print("\t");
  Serial.print(temp); Serial.print("\t");
  Serial.print(hum); Serial.print("\t");
  Serial.println();
#endif

  delay(100);

//  // blink LED to indicate activity
//  blinkState = !blinkState;
//  digitalWrite(LED_PIN, blinkState);
}
