import paho.mqtt.client as mqtt
import json
import mysql.connector
from rules import evaluate_rules
from notifier.email import send_alert
import os

# Ambil setting dari .env file
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_SENSOR = "sensor/data"  # Topic dari ESP32
MQTT_TOPIC_COMMAND = "device/command"  # Topic ke ESP32

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "iot_peternakan")

# Global variable supaya bisa kirim command dari mana saja
mqtt_client = None


def get_db_connection():
    """Buat koneksi ke database MySQL"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Exception as e:
        print(f"ERROR: Database tidak bisa connect: {e}")
        return None


def save_sensor_data(data):
    """Simpan data sensor ke database"""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO sensor_data (temperature, humidity, ammonia)
        VALUES (%s, %s, %s)
        """
        temp = data.get("temperature", 0)
        humid = data.get("humidity", 0)
        amonia = data.get("ammonia", 0)
        
        cursor.execute(query, (temp, humid, amonia))
        conn.commit()
        print(f"✓ Data simpan: temp={temp}, humid={humid}, amonia={amonia}")
        return True
    except Exception as e:
        print(f"ERROR saat simpan: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def publish_command(action):
    """Kirim command ke ESP32 via MQTT"""
    global mqtt_client
    
    if not mqtt_client or not mqtt_client.is_connected():
        print("ERROR: MQTT tidak terhubung, command tidak terkirim")
        return False

    try:
        # Buat JSON dengan command
        message = json.dumps({"action": action})
        
        # Kirim ke ESP32
        result = mqtt_client.publish(MQTT_TOPIC_COMMAND, message)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"✓ Command terkirim: {action}")
            return True
        else:
            print(f"ERROR: Gagal kirim command (code: {result.rc})")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def on_message(client, userdata, msg):
    """Callback saat terima data dari MQTT"""
    try:
        # Ambil data JSON dari MQTT
        text = msg.payload.decode()
        data = json.loads(text)
        
        print(f"\n>>> Data diterima dari ESP32: {data}")

        # 1. Simpan ke database
        save_sensor_data(data)

        # 2. Evaluasi rules untuk tau action apa yang perlu dijalankan
        actions = evaluate_rules(data)
        
        if actions:
            print(f">>> Action yang perlu dijalankan: {actions}")
            
            # 3. Kirim setiap action ke ESP32
            for action in actions:
                publish_command(action)
            
            # 4. Kirim email notifikasi (optional)
            send_alert(data, actions)
        else:
            print(">>> Tidak ada action (kondisi normal)")

    except json.JSONDecodeError:
        print("ERROR: Data JSON dari ESP32 tidak valid")
    except Exception as e:
        print(f"ERROR saat process data: {e}")


def on_connect(client, userdata, flags, rc):
    """Callback saat connect ke MQTT broker"""
    if rc == 0:
        print("✓ Berhasil connect ke MQTT broker")
        # Subscribe ke topic sensor data dari ESP32
        client.subscribe(MQTT_TOPIC_SENSOR)
        print(f"✓ Subscribe ke topic: {MQTT_TOPIC_SENSOR}")
    else:
        print(f"ERROR: Connect MQTT gagal (code: {rc})")


def start_mqtt():
    """Mulai MQTT client dan connect ke broker"""
    global mqtt_client
    
    print(">>> Menghubungkan ke MQTT broker...")
    mqtt_client = mqtt.Client()
    
    # Setup callback functions
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    try:
        # Connect ke MQTT broker
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        print(f"✓ MQTT client siap, broker: {MQTT_BROKER}:{MQTT_PORT}")
        
        # Mulai loop (blocking)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"ERROR: MQTT connection failed: {e}")
