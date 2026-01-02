#include <WiFi.h>
#include "DHT.h"
#include <HTTPClient.h>
#include <ESP_Mail_Client.h>

#define WIFI_SSID "DHIRA001" 
#define WIFI_PASSWORD "ramzy383" 

const char* host = "http://192.168.1.4/esp/insert_data.php"; 

#define MQPIN 26      // Pin GPIO tempat MQ-135 terhubung
#define DHTPIN 4      // Pin GPIO tempat DHT terhubung 
#define DHTTYPE DHT22 // atau DHT22
DHT dht(DHTPIN, DHTTYPE);

const float SUHU_MAX = 29.0; // Batas Suhu Maksimum dalam Celsius (RULE!)
const float HUMIDITY_MAX = 70.0; // Batas Kelembaban Maksimum dalam Persen
const float MQ135_MAX = 150.0; // Batas Polusi Maksimum (nilai MQ-135)
bool email_sent = false; 

#define SMTP_HOST "smtp.gmail.com"
#define SMTP_PORT 465
#define SENDER_EMAIL "praktikiot26@gmail.com"

#define SENDER_PASSWORD "ittp fpgu vzdx bxvx"
#define RECIPIENT_EMAIL "fdidan09@gmail.com"

SMTPSession smtp;
Session_Config session;
SMTP_Message message;

void setupEmail(){
    // Konfigurasi koneksi SMTP
    session.server.host_name = SMTP_HOST;
    session.server.port = SMTP_PORT;
    session.login.email = SENDER_EMAIL;
    session.login.password = SENDER_PASSWORD;

    // Isi pesan
    message.sender.name = "ESP32";
    message.sender.email = SENDER_EMAIL;
    message.subject = "⚠️ PERINGATAN! Suhu Melebihi Batas!";
    message.addRecipient("Admin", RECIPIENT_EMAIL);
}


void sendNotificationEmail(float current_temp, float current_humid) {

    if (email_sent) return;

    Serial.println("Mengirim email...");

    String message_body = "Suhu saat ini: **" + String(current_temp, 2) + " C**\n";
    message_body += "Kelembaban: " + String(current_humid, 2) + " %\n";
    message_body += "Batas normal: " + String(SUHU_MAX, 2) + " C\n";
    
    message.text.content = message_body;

    if (!smtp.connect(&session)) {
        Serial.println("Koneksi SMTP gagal.");
        return;
    }

    if (!MailClient.sendMail(&smtp, &message)) {
        Serial.println("Error saat mengirim email: " + smtp.errorReason());
    } else {
        Serial.println("Email berhasil dikirim!");
        email_sent = true;
    }
}

void sendDataToMySQL(float temp, float humid, float mq135_value) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String postData = "temperatur=" + String(temp) + "&kelembaban=" + String(humid) + "&mq135=" + String(mq135_value);

        http.begin(host);
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");

        int httpCode = http.POST(postData);

        if (httpCode > 0) {
            String payload = http.getString();
            Serial.print("Respons Server: ");
            Serial.println(payload);
        } else {
            Serial.print("Error saat request HTTP: ");
            Serial.println(httpCode);
        }
        http.end();
    } else {
        Serial.println("WiFi tidak terhubung.");
    }
}

void setup() {
    Serial.begin(9600);
    
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(300);
    }
    Serial.println("\nWiFi Terhubung.");
    Serial.print("Alamat IP ESP: ");
    Serial.println(WiFi.localIP());

    dht.begin();
    setupEmail();
}

void loop() {
    float h = dht.readHumidity();  //membaca data kelembaban
    float t = dht.readTemperature(); //membaca data suhu dalam Celcius
    float m = analogRead(MQPIN);  // membaca data dari sensor MQ-135

    if (isnan(h) || isnan(t)) {
        Serial.println("Gagal membaca dari sensor DHT!");
        delay(2000); 
        return;
    }

    sendDataToMySQL(t, h, m);
    if (t > SUHU_MAX || h > HUMIDITY_MAX || m > MQ135_MAX) {
        Serial.println("Kondisi tidak normal!");
        sendNotificationEmail(t, h);
    } else {
        Serial.println("Suhu normal.");
        email_sent = false; 
    }

    delay(5000);
}