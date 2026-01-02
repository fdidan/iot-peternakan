from flask import Flask, jsonify, request
from mqtt_listener import start_mqtt, publish_command
import threading
import mysql.connector
import os

app = Flask(__name__)

# ===== DATABASE CONFIG =====
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "iot_peternakan")


def get_db_connection():
    """Buat koneksi database MySQL"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Exception as e:
        print(f"ERROR database: {e}")
        return None


# ===== API ROUTES =====

@app.route("/", methods=["GET"])
def home():
    """Endpoint sederhana untuk test server"""
    return jsonify({"status": "Server IoT Peternakan running"}), 200


@app.route("/health", methods=["GET"])
def health_check():
    """Check kesehatan server dan database"""
    conn = get_db_connection()
    db_ok = "OK" if conn else "ERROR"
    if conn:
        conn.close()
    
    return jsonify({
        "status": "OK",
        "database": db_ok
    }), 200


@app.route("/sensor/latest", methods=["GET"])
def get_latest_sensor():
    """Ambil data sensor terbaru"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "Tidak ada data sensor"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sensor/history", methods=["GET"])
def get_sensor_history():
    """Ambil history data sensor"""
    limit = request.args.get("limit", 10, type=int)
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM sensor_data ORDER BY created_at DESC LIMIT %s",
            (limit,)
        )
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/notifications", methods=["GET"])
def get_notifications():
    """Ambil history notifikasi"""
    limit = request.args.get("limit", 20, type=int)
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM notifications ORDER BY created_at DESC LIMIT %s",
            (limit,)
        )
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/device/actions", methods=["GET"])
def get_available_actions():
    """List action apa saja yang bisa dijalankan"""
    return jsonify({
        "available_actions": [
            "OPEN_WINDOW",
            "CLOSE_WINDOW",
            "FAN_ON",
            "FAN_OFF",
            "HEATER_ON",
            "HEATER_OFF"
        ]
    }), 200


@app.route("/device/action", methods=["POST"])
def trigger_action():
    """Trigger action manual ke ESP32"""
    try:
        data = request.get_json()
        action = data.get("action")
        
        if not action:
            return jsonify({"error": "action field required"}), 400
        
        # Kirim command ke ESP32
        success = publish_command(action)
        
        if success:
            return jsonify({"message": f"Action '{action}' terkirim ke device"}), 200
        else:
            return jsonify({"error": "Gagal kirim command ke device"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Start MQTT listener di thread terpisah
    print(">>> Mulai MQTT listener...")
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()
    
    # Mulai Flask server
    print(">>> Mulai Flask server di port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=False)

