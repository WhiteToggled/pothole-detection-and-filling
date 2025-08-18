DEBUG = True

# ==========================
# Camera Config (ESP32-CAM)
# ==========================
ESP32CAM_IP = "10.165.45.249"
ESP32CAM_CAPTURE_URL = f"http://{ESP32CAM_IP}/capture"

# ==========================
# MQTT Config
# ==========================
MQTT_BROKER = "192.168.1.100"  # Replace with your broker IP (e.g., Mosquitto)
MQTT_PORT = 1883
MQTT_TOPIC_COORDS = "pothole/coords"
MQTT_TOPIC_STATUS = "car/status"
MQTT_TOPIC_COMMANDS = "car/commands"

# ==========================
# Detection Parameters
# ==========================
MIN_POTHOLE_AREA = 500        # Minimum contour area to be considered a pothole
