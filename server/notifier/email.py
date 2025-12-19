import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import mysql.connector

EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "iot_peternakan")


def save_notification(message, sent_via):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        query = "INSERT INTO notifications (message, sent_via) VALUES (%s, %s)"
        cursor.execute(query, (message, sent_via))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Notification saved: {message}")
    except Exception as e:
        print(f"Error saving notification: {e}")


def send_alert(sensor_data, actions):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("Email not configured - notification skipped")
        save_notification(f"Alert: {actions}", "system")
        return

    try:
        subject = "⚠️ IoT Peternakan Alert"
        body = f"""
Alert dari sistem IoT Peternakan:

Sensor Data:
- Suhu: {sensor_data.get('temperature')}°C
- Kelembaban: {sensor_data.get('humidity')}%
- Amonia: {sensor_data.get('ammonia')} ppm

Aksi yang dijalankan:
{chr(10).join(f"• {action}" for action in actions)}

Silakan periksa kondisi kandang Anda.
        """

        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_SENDER
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"Email alert sent")
        save_notification(f"Alert sent: {actions}", "email")

    except Exception as e:
        print(f"Error sending email: {e}")
        save_notification(f"Alert failed: {str(e)}", "error")
