#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ===== SETTING WiFi =====
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// ===== SETTING MQTT =====
const char* mqtt_server = "192.168.1.100";  // IP server atau docker host
const int mqtt_port = 1883;
const char* topic_sensor = "sensor/data";   // Kirim data ke server
const char* topic_command = "device/command"; // Terima command dari server

// ===== PIN SENSOR (INPUT ADC) =====
const int PIN_TEMP = 34;   // Sensor suhu
const int PIN_HUMID = 35;  // Sensor kelembaban
const int PIN_AMONIA = 32; // Sensor amonia

// ===== PIN ACTUATOR (OUTPUT RELAY) =====
const int PIN_WINDOW = 2;  // Relay jendela
const int PIN_FAN = 4;     // Relay kipas
const int PIN_HEATER = 5;  // Relay pemanas

// ===== MQTT CLIENT =====
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// ===== TIMING =====
unsigned long lastSensorTime = 0;
const unsigned long SENSOR_INTERVAL = 10000; // Publish sensor setiap 10 detik


void setup() {
  // Buka serial monitor untuk debug
  Serial.begin(115200);
  delay(100);
  Serial.println("\n\n===== ESP32 IoT Peternakan =====");
  
  // Setup pin relay sebagai OUTPUT (untuk kontrol relay)
  pinMode(PIN_WINDOW, OUTPUT);
  pinMode(PIN_FAN, OUTPUT);
  pinMode(PIN_HEATER, OUTPUT);
  
  // Set semua relay OFF (LOW = relay OFF)
  digitalWrite(PIN_WINDOW, LOW);
  digitalWrite(PIN_FAN, LOW);
  digitalWrite(PIN_HEATER, LOW);
  Serial.println("✓ Pin relay siap (semua OFF)");
  
  // Connect ke WiFi
  connectWiFi();
  
  // Setup MQTT
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(onMessageReceived);
  Serial.println("✓ MQTT siap");
}


void loop() {
  // Pastikan selalu connect ke MQTT
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop(); // Process MQTT messages
  
  // Publish sensor data setiap 10 detik
  unsigned long now = millis();
  if (now - lastSensorTime >= SENSOR_INTERVAL) {
    publishSensorData();
    lastSensorTime = now;
  }
}


void connectWiFi() {
  // Connect ke WiFi
  Serial.print(">>> Connect WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nERROR: WiFi gagal connect");
  }
}


void reconnectMQTT() {
  // Coba connect ke MQTT broker
  Serial.print(">>> Connect MQTT...");
  
  if (mqttClient.connect("ESP32")) {
    Serial.println(" OK!");
    // Subscribe ke command topic
    mqttClient.subscribe(topic_command);
    Serial.print("✓ Subscribe: ");
    Serial.println(topic_command);
  } else {
    Serial.print(" GAGAL (");
    Serial.print(mqttClient.state());
    Serial.println(") - coba lagi 5 detik");
    delay(5000);
  }
}


void publishSensorData() {
  // Baca semua sensor
  float temp = readTemperature();
  float humid = readHumidity();
  float amonia = readAmmonia();
  
  // Buat JSON dengan data sensor
  DynamicJsonDocument doc(200);
  doc["temperature"] = temp;
  doc["humidity"] = humid;
  doc["ammonia"] = amonia;
  
  // Convert JSON ke string
  String payload;
  serializeJson(doc, payload);
  
  // Publish ke MQTT
  if (mqttClient.publish(topic_sensor, payload.c_str())) {
    Serial.print("✓ Publish: ");
    Serial.println(payload);
  } else {
    Serial.println("ERROR: Publish gagal");
  }
}


void onMessageReceived(char* topic, byte* payload, unsigned int length) {
  // Saat terima command dari server
  Serial.print("\n>>> Command diterima dari: ");
  Serial.println(topic);
  
  // Konversi byte array ke string
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print(">>> Pesan: ");
  Serial.println(message);
  
  // Parse JSON
  DynamicJsonDocument doc(200);
  deserializeJson(doc, message);
  
  String action = doc["action"];
  
  // Jalankan action sesuai command dari server
  if (action == "OPEN_WINDOW") {
    digitalWrite(PIN_WINDOW, HIGH);
    Serial.println(">>> Aksi: JENDELA BUKA");
  }
  else if (action == "CLOSE_WINDOW") {
    digitalWrite(PIN_WINDOW, LOW);
    Serial.println(">>> Aksi: JENDELA TUTUP");
  }
  else if (action == "FAN_ON") {
    digitalWrite(PIN_FAN, HIGH);
    Serial.println(">>> Aksi: KIPAS HIDUP");
  }
  else if (action == "FAN_OFF") {
    digitalWrite(PIN_FAN, LOW);
    Serial.println(">>> Aksi: KIPAS MATI");
  }
  else if (action == "HEATER_ON") {
    digitalWrite(PIN_HEATER, HIGH);
    Serial.println(">>> Aksi: PEMANAS HIDUP");
  }
  else if (action == "HEATER_OFF") {
    digitalWrite(PIN_HEATER, LOW);
    Serial.println(">>> Aksi: PEMANAS MATI");
  }
  else {
    Serial.print("ERROR: Action tidak dikenal: ");
    Serial.println(action);
  }
}


float readTemperature() {
  // Baca ADC dan convert ke temperatur
  int rawValue = analogRead(PIN_TEMP);
  float voltage = (rawValue / 4095.0) * 3.3;
  float temperature = voltage * 100;  // Sesuaikan dengan sensor kamu
  return temperature;
}

float readHumidity() {
  // Baca ADC dan convert ke kelembaban
  int rawValue = analogRead(PIN_HUMID);
  float humidity = (rawValue / 4095.0) * 100;
  return humidity;
}

float readAmmonia() {
  // Baca ADC untuk amonia
  int rawValue = analogRead(PIN_AMONIA);
  float ammonia = (rawValue / 4095.0) * 100;  // PPM
  return ammonia;
}
