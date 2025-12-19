# 📖 PANDUAN SISTEM IoT Peternakan

## 🎯 Konsep Dasar (Mudah Dipahami)

Sistem ini **sangat sederhana**:

```
1. ESP32 baca sensor → kirim ke server via MQTT
2. Server terima → check kondisi dengan rules
3. Jika perlu aksi → server kirim command ke ESP32
4. ESP32 terima → jalankan aksi (nyalakan relay)
```

### Contoh Real:
```
Suhu naik ke 32°C
    ↓
Server terima: "temperature": 32
    ↓
Check rule: temp > 30 dan humidity > 70?
    ↓
YES → generate action: "FAN_ON"
    ↓
Kirim ke ESP32: {"action": "FAN_ON"}
    ↓
ESP32 terima → set GPIO 4 = HIGH
    ↓
Kipas mulai hidup 💨
```

---

## 📝 FILE PENTING (BACA INI)

### 1. **esp32/main.ino** (Program ESP32)
Berisi:
- Baca 3 sensor (temp, humidity, ammonia)
- Publish ke MQTT setiap 10 detik
- Terima command dari server
- Jalankan command (nyalakan/matikan relay)

**Pin penting:**
```
INPUT:  GPIO 34, 35, 32 (ADC sensor)
OUTPUT: GPIO 2, 4, 5 (relay)
```

### 2. **server/mqtt_listener.py** (MQTT Handler)
Berisi:
- `on_message()` → saat terima data dari ESP32
- `evaluate_rules()` → check rule untuk tau aksi apa
- `publish_command()` → kirim command ke ESP32

### 3. **server/rules.py** (Business Logic)
Berisi 6 rules:
```
Jika temp > 30 + humidity > 70 → nyalakan kipas
Jika temp < 28 + humidity < 60 → matikan kipas
Jika temp < 22 → nyalakan pemanas
Jika temp > 25 → matikan pemanas
Jika ammonia > 25 → buka jendela
Jika ammonia < 10 → tutup jendela
```

### 4. **server/app.py** (REST API)
Berisi 7 endpoint untuk akses dari web/mobile:
```
GET  /api/sensor/latest    → data terbaru
GET  /api/sensor/history   → riwayat
GET  /api/notifications    → log aksi
POST /api/device/action    → trigger manual
GET  /api/device/actions   → list aksi
GET  /api/health           → status
```

---

## 🔄 KOMUNIKASI (How It Works)

### Topic MQTT
```
sensor/data ← dari ESP32 (setiap 10 detik)
device/command ← dari server (saat perlu)
```

### Format JSON

**Data Sensor (ESP32 → Server):**
```json
{
  "temperature": 28.5,
  "humidity": 65.0,
  "ammonia": 18.0
}
```

**Command (Server → ESP32):**
```json
{
  "action": "FAN_ON"
}
```

---

## 🌐 API Endpoints

### Lihat Data Sensor
```bash
curl http://localhost:5000/api/sensor/latest
```
Response:
```json
{
  "id": 1,
  "temperature": 28.5,
  "humidity": 65.0,
  "ammonia": 18.0,
  "created_at": "2024-12-19 10:30:45"
}
```

### History Sensor (ambil 10 terakhir)
```bash
curl "http://localhost:5000/api/sensor/history?limit=10"
```

### Lihat Aksi Apa Saja Available
```bash
curl http://localhost:5000/api/device/actions
```
Response:
```json
{
  "available_actions": [
    "OPEN_WINDOW",
    "CLOSE_WINDOW",
    "FAN_ON",
    "FAN_OFF",
    "HEATER_ON",
    "HEATER_OFF"
  ]
}
```

### Trigger Manual (Buka Jendela)
```bash
curl -X POST http://localhost:5000/api/device/action \
  -H "Content-Type: application/json" \
  -d '{"action": "OPEN_WINDOW"}'
```

### Check Status Server & DB
```bash
curl http://localhost:5000/api/health
```

---

## ⚙️ RULES YANG ADA

| Kondisi | Action | Keterangan |
|---------|--------|-----------|
| Temp > 30 + Humidity > 70 | FAN_ON | Panas + lembab |
| Temp < 28 + Humidity < 60 | FAN_OFF | Sudah normal |
| Temp < 22 | HEATER_ON | Dingin |
| Temp > 25 | HEATER_OFF | Sudah hangat |
| Ammonia > 25 | OPEN_WINDOW | Jelek, buka |
| Ammonia < 10 | CLOSE_WINDOW | Bagus, tutup |

**Cara kerja:**
- Otomatis setiap kali ESP32 kirim data
- Server evaluasi rules
- Jika rule match → kirim command ke ESP32

---

## 🚀 SETUP & RUN

### Setup Pertama Kali (5 menit)

1. **Update .env**
```bash
nano .env
```
Isi:
```env
DB_HOST=mysql
DB_USER=root
DB_PASSWORD=root
DB_NAME=iot_peternakan
MQTT_BROKER=localhost
MQTT_PORT=1883
```

2. **Start Docker**
```bash
docker-compose up -d
```

3. **Tunggu services start** (30 detik)

4. **Check status**
```bash
curl http://localhost:5000/api/health
```
Kalau response: `{"status":"OK","database":"OK"}` → Sukses! ✓

### Lihat Logs (untuk debug)
```bash
docker-compose logs -f server
```

### Matikan Services
```bash
docker-compose down
```

---

## 🧪 TESTING SIMPLE

### Test 1: Send Sensor Data (Simulate ESP32)
```bash
mosquitto_pub -h localhost -t "sensor/data" \
  -m '{"temperature": 32, "humidity": 75, "ammonia": 15}'
```

Check logs:
```bash
docker-compose logs server
```
Harus keluar:
```
>>> Data diterima dari ESP32: {'temperature': 32, ...}
>>> Action yang perlu dijalankan: ['FAN_ON']
✓ Command terkirim: FAN_ON
```

### Test 2: Monitor Command (Lihat command terkirim)
```bash
mosquitto_sub -h localhost -t "device/command"
```

Buka terminal baru dan trigger manual:
```bash
curl -X POST http://localhost:5000/api/device/action \
  -H "Content-Type: application/json" \
  -d '{"action": "FAN_ON"}'
```

Di terminal monitor harus keluar:
```
{"action":"FAN_ON"}
```

### Test 3: Check Database
```bash
docker-compose exec mysql mysql -u root -proot iot_peternakan
SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT 5;
exit
```

---

## 🔌 PIN MAPPING (ESP32)

### Input (Sensor - ADC)
- **GPIO 34** → Temperature Sensor
- **GPIO 35** → Humidity Sensor
- **GPIO 32** → Ammonia Sensor

### Output (Relay)
- **GPIO 2** → Window Relay
- **GPIO 4** → Fan Relay
- **GPIO 5** → Heater Relay

**Catatan:** HIGH = ON, LOW = OFF

---

## 🐛 TROUBLESHOOTING

### Problem: "Database connection failed"
**Solution:**
```bash
# Check MySQL running
docker-compose logs mysql

# Restart MySQL
docker-compose restart mysql
```

### Problem: MQTT tidak connect
**Solution:**
```bash
# Check .env MQTT_BROKER value
# Jika di docker, harus "localhost" atau service name "mqtt"
# Jika di luar docker, harus actual IP

# Monitor MQTT
mosquitto_sub -h localhost -t "#"
```

### Problem: ESP32 tidak terima command
**Solution:**
1. Check serial monitor ESP32
2. Pastikan WiFi connected
3. Pastikan MQTT_BROKER IP benar
4. Monitor logs: `docker-compose logs -f`

### Problem: API tidak respond
**Solution:**
```bash
# Restart server
docker-compose restart server

# Check logs
docker-compose logs server
```

---

## 📊 QUICK REFERENCE

**Ports:**
- API: 5000
- MySQL: 3306
- MQTT: 1883

**Files Location:**
```
server/
├── app.py           ← API routes
├── mqtt_listener.py ← MQTT handler
├── rules.py         ← Business logic
└── notifier/email.py ← Email alerts

esp32/
└── main.ino         ← ESP32 code

database/
├── Dockerfile
└── init.sql         ← Database schema
```

**Database Tables:**
```
sensor_data:
  - id
  - temperature
  - humidity
  - ammonia
  - created_at

notifications:
  - id
  - message
  - sent_via
  - created_at
```

---

## ✨ WHAT'S INSIDE

```
✅ Sensor data receiver (MQTT)
✅ Rules engine (6 rules)
✅ Command sender (MQTT)
✅ REST API (7 endpoints)
✅ Database logging
✅ Email alerts (optional)
✅ Docker setup
✅ Simple, newbie-friendly code
```

---

## 🎓 UNTUK BEGINNER

### Workflow sederhana:
1. ESP32 membaca ADC pins
2. Convert ke float values (temp, humidity, ammonia)
3. Create JSON: `{"temperature": X, ...}`
4. Publish ke MQTT: `sensor/data`
5. Server MQTT client terima (callback)
6. Parse JSON → save database
7. Evaluate rules (simple if-else)
8. If rule match → create command JSON
9. Publish command ke MQTT: `device/command`
10. ESP32 MQTT client terima command (callback)
11. Parse JSON → ambil action
12. digitalWrite(pin, HIGH/LOW)

**Itu saja!** Tidak ada magic, semua straightforward.

---

**Status:** ✅ Newbie-Friendly  
**Complexity:** Very Low  
**Time to Understand:** 1-2 hours

