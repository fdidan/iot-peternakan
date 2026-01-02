# 🐓 IoT Peternakan

Sistem monitoring & kontrol kandang ternak otomatis berbasis IoT.

**Status:** ✅ Production Ready | **Language:** Simple & Newbie-Friendly

---

## 🎯 Apa Itu?

Sistem yang membuat kandang hewan **otomatis**:
- 📡 ESP32 membaca sensor suhu, kelembaban, amonia
- 🔄 Kirim data ke server setiap 10 detik
- 🧠 Server evaluate kondisi dengan rules
- 💡 Otomatis buka/tutup jendela, nyalakan kipas/pemanas
- 📱 Bisa manual trigger via API

---

## 🚀 Quick Start (5 menit)

### 1. Start Services
```bash
cd d:\PRIBADI\Proyek\iot-peternakan
docker-compose up -d
```

### 2. Check Status
```bash
curl http://localhost:5000/api/health
```

Response: `{"status":"OK","database":"OK"}` → Success! ✅

### 3. Test
```bash
# Get latest sensor data
curl http://localhost:5000/api/sensor/latest

# See available actions
curl http://localhost:5000/api/device/actions

# Trigger manual action
curl -X POST http://localhost:5000/api/device/action \
  -H "Content-Type: application/json" \
  -d '{"action": "FAN_ON"}'
```

---

## 📚 DOKUMENTASI

| File | Untuk | Isi |
|------|-------|-----|
| **[GUIDE.md](GUIDE.md)** | Semua orang | Konsep, API, testing |
| **[SETUP.md](SETUP.md)** | Deployment | Setup, troubleshoot |
| **[QUICKSTART.md](QUICKSTART.md)** | Cepat | Command reference |

**Start here:** → [GUIDE.md](GUIDE.md)

---

## 🔧 Sistem Overview

```
┌──────────────┐
│   ESP32      │
│ (3 Sensor)   │
└──────┬───────┘
       │ MQTT publish
       │ "sensor/data"
       ▼
┌──────────────────┐
│ MQTT Broker      │
│ (mosquitto)      │
└──────┬───────────┘
       │ subscribe
       ▼
┌──────────────────────┐
│ Server               │
│ ├─ mqtt_listener.py  │ ← Receive data
│ ├─ rules.py          │ ← Logic
│ ├─ app.py            │ ← REST API
│ └─ email.py          │ ← Alerts
└──────┬───────────────┘
       │ MQTT publish
       │ "device/command"
       ▼
┌──────────────┐
│   ESP32      │
│ (3 Relay)    │
└──────────────┘
```

---

## 📊 RULES ENGINE

| Kondisi | Aksi |
|---------|------|
| Temp > 30 + Humidity > 70 | Nyalakan kipas |
| Temp < 28 + Humidity < 60 | Matikan kipas |
| Temp < 22 | Nyalakan pemanas |
| Temp > 25 | Matikan pemanas |
| Ammonia > 25 | Buka jendela |
| Ammonia < 10 | Tutup jendela |

---

## 🌐 REST API

### Lihat Data Terbaru
```bash
curl http://localhost:5000/api/sensor/latest
```

### Lihat History (10 terakhir)
```bash
curl "http://localhost:5000/api/sensor/history?limit=10"
```

### Lihat Action Available
```bash
curl http://localhost:5000/api/device/actions
```

### Trigger Manual Action
```bash
curl -X POST http://localhost:5000/api/device/action \
  -H "Content-Type: application/json" \
  -d '{"action": "FAN_ON"}'
```

### Check Status
```bash
curl http://localhost:5000/api/health
```

---

## 📁 STRUKTUR FILE

```
iot-peternakan/
├── esp32/
│   └── main.ino              ← Program ESP32
├── server/
│   ├── app.py                ← REST API
│   ├── mqtt_listener.py      ← MQTT handler
│   ├── rules.py              ← Business logic
│   ├── notifier/email.py     ← Email alerts
│   └── requirements.txt
├── database/
│   ├── Dockerfile
│   └── init.sql              ← Database schema
├── docker-compose.yml        ← Services config
├── .env                      ← Settings
├── README.md                 ← Ini (overview)
├── GUIDE.md                  ← How to understand
├── SETUP.md                  ← How to setup
└── QUICKSTART.md             ← Commands reference
```

---

## 🧠 HOW IT WORKS

### Flow Otomatis:
```
1. ESP32 baca sensor → publish JSON ke MQTT
2. Server MQTT terima → save database
3. Server evaluate rules → generate actions
4. Server publish command ke MQTT
5. ESP32 terima command → jalankan (digitalWrite)
```

### Flow Manual (via API):
```
1. User POST /api/device/action {"action": "FAN_ON"}
2. Server kirim command ke MQTT
3. ESP32 terima → jalankan
```

---

## 🔌 HARDWARE PIN

### Input (Sensor ADC)
- GPIO 34 → Temperature sensor
- GPIO 35 → Humidity sensor
- GPIO 32 → Ammonia sensor

### Output (Relay)
- GPIO 2 → Window relay
- GPIO 4 → Fan relay
- GPIO 5 → Heater relay

---

## 🎓 UNTUK PEMULA

Code sangat **sederhana** dan mudah dipahami:

- **mqtt_listener.py** (130 lines)
  - on_message() → saat terima data
  - publish_command() → kirim command
  - Simple if logic

- **esp32/main.ino** (200 lines)
  - readTemperature() → baca ADC
  - publishSensorData() → kirim JSON
  - onMessageReceived() → terima command

- **rules.py** (30 lines)
  - Simple if-else statements
  - Temperature, humidity, ammonia checks

- **app.py** (150 lines)
  - 7 Flask routes
  - Database queries
  - JSON responses

**Total:** ~500 lines of straightforward code, heavily commented.

---

## ✨ FEATURES

✅ Two-way MQTT communication  
✅ Automatic rules engine (6 rules)  
✅ Manual API control  
✅ Database logging  
✅ Email alerts (optional)  
✅ REST API (7 endpoints)  
✅ Simple newbie-friendly code  
✅ Docker deployment  
✅ Comprehensive docs  

---

## 🛠️ DEPLOYMENT

### Requirements
- Docker + Docker Compose
- 3 ports free: 5000 (API), 3306 (DB), 1883 (MQTT)

### Setup
1. Edit `.env` (optional, defaults work)
2. Run: `docker-compose up -d`
3. Wait 30 seconds
4. Test: `curl http://localhost:5000/api/health`

**Total time:** ~5 minutes

---

## 🧪 TESTING

### Test 1: Send fake data
```bash
mosquitto_pub -h localhost -t "sensor/data" \
  -m '{"temperature": 32, "humidity": 75, "ammonia": 15}'
```

Server should:
- Receive data
- Check rules
- Send command "FAN_ON"

### Test 2: Monitor commands
```bash
mosquitto_sub -h localhost -t "device/command"
```

### Test 3: Manual trigger
```bash
curl -X POST http://localhost:5000/api/device/action \
  -H "Content-Type: application/json" \
  -d '{"action": "HEATER_ON"}'
```

---

## 🐛 TROUBLESHOOT

### Database error?
```bash
docker-compose logs mysql
docker-compose restart mysql
```

### MQTT not working?
```bash
docker-compose logs server
# Check .env MQTT_BROKER value
```

### API not responding?
```bash
docker-compose restart server
docker-compose logs server
```

---

## 📞 HELP

1. Read **[GUIDE.md](GUIDE.md)** → Konsep & API
2. Read **[SETUP.md](SETUP.md)** → Setup & Troubleshoot
3. Check logs: `docker-compose logs -f`
4. Monitor MQTT: `mosquitto_sub -h localhost -t "#"`

---

## 📊 PROJECT INFO

- **Lines of Code:** ~500 (simple)
- **Documentation:** 3 files (Guide, Setup, Quick)
- **API Endpoints:** 7
- **Rules:** 6
- **Complexity:** Very Low (Newbie-Friendly)
- **Time to Deploy:** 5 minutes
- **Time to Understand:** 1-2 hours

---

## ✅ CHECKLIST

- [x] Code simplified for newbie
- [x] Documentation consolidated (3 files)
- [x] All features working
- [x] Production ready
- [x] Easy to deploy
- [x] Easy to understand

---

**Status:** 🎉 **PRODUCTION READY**

Start with: **[GUIDE.md](GUIDE.md)**
