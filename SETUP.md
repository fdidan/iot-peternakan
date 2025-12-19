# 🛠️ SETUP & DEPLOYMENT

## ⚡ Quick Start (5 minutes)

### 1. Pastikan Docker Installed
```bash
docker --version
docker-compose --version
```

### 2. Update .env File
Edit file `.env`:
```env
# Database
DB_HOST=mysql
DB_USER=root
DB_PASSWORD=root
DB_NAME=iot_peternakan

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883

# Email (optional, leave blank if not used)
EMAIL_SENDER=
EMAIL_PASSWORD=
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3. Start All Services
```bash
docker-compose up -d
```

### 4. Wait 30 seconds for services to start

### 5. Verify Everything Works
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{"status":"OK","database":"OK"}
```

If you see this → **Everything works!** ✅

---

## 📝 ESP32 Setup

### 1. Hardware Assembly
Connect:
- **GPIO 34** → Temperature sensor ADC pin
- **GPIO 35** → Humidity sensor ADC pin
- **GPIO 32** → Ammonia sensor ADC pin
- **GPIO 2** → Window relay IN pin
- **GPIO 4** → Fan relay IN pin
- **GPIO 5** → Heater relay IN pin

### 2. Arduino IDE Setup
1. Install Arduino IDE (arduino.cc)
2. Add ESP32 board: File → Preferences → Additional Boards Manager URLs
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Board Manager → Search "ESP32" → Install
4. Tools → Board → ESP32 Dev Module

### 3. Install Libraries
In Arduino IDE, Sketch → Include Library → Manage Libraries:
- Search: **WiFi** (built-in, no action needed)
- Search: **PubSubClient** → Install by Nick O'Leary
- Search: **ArduinoJson** → Install by Benoit Blanchon

### 4. Upload Code
1. Edit `esp32/main.ino`:
   ```cpp
   const char* ssid = "YOUR_WIFI_NAME";
   const char* password = "YOUR_WIFI_PASSWORD";
   const char* mqtt_server = "192.168.1.100"; // Your server IP
   ```

2. Open `esp32/main.ino` in Arduino IDE
3. Tools → Board → Select "ESP32 Dev Module"
4. Tools → Port → Select COM port of ESP32
5. Click Upload (→ button)

### 5. Verify Upload
1. Open Serial Monitor (Tools → Serial Monitor)
2. Set baud rate to 115200
3. Reset ESP32 (press RESET button)
4. Should see:
   ```
   ===== ESP32 IoT Peternakan =====
   ✓ Pin relay siap (semua OFF)
   ✓ MQTT siap
   >>> Connect WiFi: YOUR_SSID
   ✓ WiFi connected!
   >>> Connect MQTT...
   ```

---

## 🧪 Testing After Setup

### Test 1: Check Server Health
```bash
curl http://localhost:5000/api/health
```

### Test 2: View Latest Sensor Data
```bash
curl http://localhost:5000/api/sensor/latest
```

### Test 3: Get Available Actions
```bash
curl http://localhost:5000/api/device/actions
```

### Test 4: Send Fake Sensor Data
```bash
mosquitto_pub -h localhost -t "sensor/data" \
  -m '{"temperature": 32, "humidity": 75, "ammonia": 15}'
```

Check server logs:
```bash
docker-compose logs server | tail -20
```

Should show:
```
>>> Data diterima dari ESP32:
>>> Action yang perlu dijalankan: ['FAN_ON']
✓ Command terkirim: FAN_ON
```

### Test 5: Monitor MQTT Commands
Open 2 terminals:

Terminal 1 (Monitor):
```bash
mosquitto_sub -h localhost -t "device/command"
```

Terminal 2 (Send):
```bash
curl -X POST http://localhost:5000/api/device/action \
  -H "Content-Type: application/json" \
  -d '{"action": "HEATER_ON"}'
```

Terminal 1 should show:
```json
{"action":"HEATER_ON"}
```

---

## 📊 Docker Commands

### View all running containers
```bash
docker-compose ps
```

### View logs
```bash
# All services
docker-compose logs -f

# Just server
docker-compose logs -f server

# Just MySQL
docker-compose logs -f mysql

# Last 50 lines
docker-compose logs --tail=50
```

### Stop services
```bash
docker-compose stop
```

### Restart services
```bash
docker-compose restart
```

### Remove everything (cleanup)
```bash
docker-compose down
```

### Remove with volumes (full cleanup)
```bash
docker-compose down -v
```

---

## 🗄️ Database Access

### Connect to MySQL CLI
```bash
docker-compose exec mysql mysql -u root -proot iot_peternakan
```

### View sensor data
```sql
SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT 10;
```

### View notifications
```sql
SELECT * FROM notifications ORDER BY created_at DESC LIMIT 10;
```

### Exit MySQL
```sql
exit;
```

---

## 🐛 Troubleshooting

### Issue: "Cannot connect to database"
**Check:**
```bash
docker-compose logs mysql
docker-compose ps
```

**Fix:**
```bash
docker-compose restart mysql
docker-compose restart server
```

---

### Issue: "MQTT connection error"
**Check:**
```bash
# Check if MQTT broker is running
docker-compose ps

# If using external MQTT, check IP/port
# Edit .env: MQTT_BROKER=your_actual_ip
```

**Fix:**
```bash
# If docker MQTT, use: localhost
# If external, use: actual_ip_address
# Edit .env and restart
docker-compose restart server
```

---

### Issue: "ESP32 can't connect to MQTT"
**Check:**
1. WiFi connected? (check Serial Monitor)
2. MQTT server IP correct? (edit main.ino)
3. Firewall blocking port 1883?

**Fix:**
```cpp
// In main.ino, update:
const char* mqtt_server = "YOUR_SERVER_IP"; // Not "localhost", use actual IP
```

---

### Issue: "API endpoint returns error"
**Check logs:**
```bash
docker-compose logs server | tail -50
```

**Restart:**
```bash
docker-compose restart server
```

---

## 📋 Pre-Production Checklist

Before going live:
- [ ] All 3 sensors connected and reading values
- [ ] All 3 relays working (test with manual triggers)
- [ ] WiFi stable on ESP32
- [ ] MQTT topics working (test mosquitto_pub/sub)
- [ ] API endpoints responding
- [ ] Database logging data
- [ ] Rules triggering correctly
- [ ] Email alerts working (if configured)
- [ ] Logs are clean (no ERROR messages)

---

## 🚀 Deployment Options

### Option 1: Single Docker Host (Recommended for dev)
- Run everything on 1 machine
- docker-compose.yml has all services
- Port mapping: Flask 5000, MySQL 3306, MQTT 1883

### Option 2: Multiple Hosts
- Separate Flask server
- Separate MySQL server
- Separate MQTT broker
- Update docker-compose to point to external hosts

Example:
```yaml
services:
  server:
    environment:
      DB_HOST: external_mysql_ip
      MQTT_BROKER: external_mqtt_ip
```

### Option 3: Cloud Deployment
- Deploy Docker image to AWS/GCP/Azure
- Update environment variables for cloud services
- Ensure security groups allow ports

---

## 🔒 Security Notes

### For Production:
1. **Change database password** (not "root")
2. **Use strong MQTT password** (if MQTT has auth)
3. **Enable HTTPS** (put Nginx/Apache reverse proxy in front)
4. **Secure API** (add authentication token)
5. **Firewall** (only allow necessary ports)

### Currently (Dev):
- Database password is "root" (OK for development)
- No MQTT authentication (OK for dev)
- No API authentication (OK for dev)

---

## 📞 SUPPORT

### Check status:
```bash
curl http://localhost:5000/api/health
```

### View real-time logs:
```bash
docker-compose logs -f
```

### Monitor MQTT traffic:
```bash
mosquitto_sub -h localhost -t "#"
```

### Database issues:
```bash
docker-compose logs mysql
```

---

**Status:** ✅ Ready to Deploy

