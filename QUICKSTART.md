# ⚡ QUICKSTART

Kumpulan perintah yang paling sering dipakai.

---

## 🚀 START / STOP

### Start semua services
```bash
cd d:\PRIBADI\Proyek\iot-peternakan
docker-compose up -d
```

### Check status
```bash
docker-compose ps
```

Expected output:
```
NAME                  STATUS
iot-db                Up (healthy)
iot-mqtt              Up
iot-server            Up
```

### Stop semua
```bash
docker-compose down
```

### Restart satu service
```bash
docker-compose restart server
# atau
docker-compose restart mqtt
# atau
docker-compose restart mysql
```

---

## 🔍 LOGS

### Lihat log server (realtime)
```bash
docker-compose logs -f server
```

### Lihat log MQTT
```bash
docker-compose logs mqtt
```

### Lihat log database
```bash
docker-compose logs mysql
```

### Stop watching (Ctrl+C)

---

## 🧪 TEST DATA

### Publish fake sensor data
```bash
mosquitto_pub -h localhost -t "sensor/data" \
  -m '{"temperature": 32, "humidity": 75, "ammonia": 15}'
```

Server akan:
- Save ke database
- Check rules
- Publish command ke device/command

### Monitor incoming commands
```bash
mosquitto_sub -h localhost -t "device/command"
```

Terminal akan show:
```
{"action": "FAN_ON"}
{"action": "WINDOW_OPEN"}
```

### Monitor all MQTT traffic
```bash
mosquitto_sub -h localhost -t "#" -v
```

---

## 📡 API ENDPOINTS

### Health check
```bash
curl http://localhost:5000/api/health
```

Response:
```json
{"status": "OK", "database": "OK"}
```

### Get latest sensor reading
```bash
curl http://localhost:5000/api/sensor/latest
```

Response:
```json
{
  "temperature": 28.5,
  "humidity": 65,
  "ammonia": 12,
  "timestamp": "2024-01-15 10:30:45"
}
```

### Get history (last 10)
```bash
curl "http://localhost:5000/api/sensor/history?limit=10"
```

### List available actions
```bash
curl http://localhost:5000/api/device/actions
```

Response:
```json
[
  "FAN_ON", "FAN_OFF",
  "HEATER_ON", "HEATER_OFF",
  "WINDOW_OPEN", "WINDOW_CLOSE"
]
```

### Trigger manual action
```bash
curl -X POST http://localhost:5000/api/device/action \
  -H "Content-Type: application/json" \
  -d '{"action": "FAN_ON"}'
```

Response:
```json
{"status": "success", "action": "FAN_ON"}
```

### Get all notifications
```bash
curl http://localhost:5000/api/notifications
```

---

## 🗄️ DATABASE

### Connect to MySQL
```bash
docker-compose exec mysql mysql -u root -p

# Password: root (check .env)
```

### View all tables
```sql
USE livestock_iot;
SHOW TABLES;
```

### View sensor data
```sql
SELECT * FROM sensor_readings ORDER BY created_at DESC LIMIT 5;
```

### View notifications
```sql
SELECT * FROM notifications WHERE read_status = 0;
```

### Clear old data
```sql
DELETE FROM sensor_readings WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

---

## 🔧 SETTINGS (.env)

View current settings:
```bash
cat .env
```

Edit settings:
```bash
# Linux/Mac
nano .env

# Windows (PowerShell)
notepad .env
```

**Common settings:**
```
MQTT_BROKER=localhost      # MQTT server address
MQTT_PORT=1883             # MQTT port
DB_PASSWORD=root           # Database password
FLASK_PORT=5000            # API port
```

After changing `.env`:
```bash
docker-compose down
docker-compose up -d
```

---

## 🧹 CLEANUP

### Remove old data (keep last 7 days)
```bash
docker-compose exec mysql mysql -u root -p -e "
  USE livestock_iot;
  DELETE FROM sensor_readings WHERE created_at < DATE_SUB(NOW(), INTERVAL 7 DAY);
  SELECT COUNT(*) as 'Records remaining' FROM sensor_readings;
"
```

### Clear all containers (CAREFUL!)
```bash
docker-compose down -v
# -v removes volumes (database!) - use only if you want to reset
```

### Remove unused images
```bash
docker image prune -a
```

---

## 🐛 QUICK FIXES

### Server won't start?
```bash
docker-compose logs server
docker-compose restart server
```

### Database connection error?
```bash
docker-compose restart mysql
sleep 10
docker-compose restart server
```

### MQTT not working?
```bash
docker-compose restart mqtt
```

### Port already in use?
```bash
# Kill process on port 5000
taskkill /F /PID <PID>    # Windows
# or check docker-compose.yml and change port
```

### Need to reset everything?
```bash
docker-compose down -v
docker-compose up -d
# Wait 30 seconds for initialization
```

---

## 📊 MONITORING

### Watch realtime logs (all services)
```bash
docker-compose logs -f
```

### Watch sensor data coming in
```bash
docker-compose logs -f server | grep "✓ Sensor"
```

### Watch commands being sent
```bash
docker-compose logs -f server | grep "✓ Command"
```

---

## 📝 COMMON WORKFLOWS

### Test temperature rule
```bash
# 1. Publish high temp + high humidity
mosquitto_pub -h localhost -t "sensor/data" \
  -m '{"temperature": 32, "humidity": 75, "ammonia": 5}'

# 2. Monitor logs
docker-compose logs -f server

# 3. Check if FAN_ON command was sent
mosquitto_sub -h localhost -t "device/command"
```

### Check if rules working
```bash
# 1. Monitor device commands
mosquitto_sub -h localhost -t "device/command" &

# 2. Send different sensor values
mosquitto_pub -h localhost -t "sensor/data" \
  -m '{"temperature": 25, "humidity": 50, "ammonia": 5}'

# 3. Check which command is sent
```

### Manual device control
```bash
# Turn FAN on
curl -X POST http://localhost:5000/api/device/action \
  -H "Content-Type: application/json" \
  -d '{"action": "FAN_ON"}'

# Wait 5 seconds, see if sensor still reads high
curl http://localhost:5000/api/sensor/latest

# Turn FAN off manually
curl -X POST http://localhost:5000/api/device/action \
  -H "Content-Type: application/json" \
  -d '{"action": "FAN_OFF"}'
```

---

## 💾 BACKUP & RESTORE

### Backup database
```bash
docker-compose exec mysql mysqldump -u root -p livestock_iot > backup.sql
```

### Restore database
```bash
docker-compose exec mysql mysql -u root -p livestock_iot < backup.sql
```

---

## ⚙️ ADVANCED

### Build Docker images locally
```bash
docker-compose build
```

### Pull latest images
```bash
docker-compose pull
docker-compose up -d
```

### SSH into container
```bash
docker-compose exec server bash
```

### Run custom SQL
```bash
docker-compose exec mysql mysql -u root -p < script.sql
```

---

## 🆘 HELP

**For detailed info:**
- System overview → Read **[README.md](README.md)**
- How code works → Read **[GUIDE.md](GUIDE.md)**
- Setup & troubleshoot → Read **[SETUP.md](SETUP.md)**
- This file → **Common commands**

**For logs:**
```bash
# Everything
docker-compose logs

# Last 50 lines
docker-compose logs --tail 50

# Follow in realtime
docker-compose logs -f

# Single service
docker-compose logs server
```

---

## 🎯 5-STEP SETUP

```bash
# 1. Navigate to project
cd d:\PRIBADI\Proyek\iot-peternakan

# 2. Start services
docker-compose up -d

# 3. Wait 30 seconds
sleep 30   # or just wait manually

# 4. Test
curl http://localhost:5000/api/health

# 5. Done! Check README for next steps
```

---

**Always check logs first when something fails:** `docker-compose logs server`
