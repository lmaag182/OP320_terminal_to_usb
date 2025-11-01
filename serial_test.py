import minimalmodbus
import serial
import time
import paho.mqtt.client as mqtt
import json

# --- Modbus RTU configuration ---
# You might need to change the slave address.
SLAVE_ADDRESS = 1
PORT = '/dev/ttyUSB0'

# --- Values to read ---
# 4x registers are holding registers.
# Let's try reading from register 1.
REGISTER_START = 0
REGISTER_COUNT = 8
SCAN_INTERVAL = 1  # seconds

# --- MQTT Configuration ---
MQTT_BROKER = "192.168.50.75"
MQTT_PORT = 1883
MQTT_TOPIC_BASE = "wp3082adam/registers"

# Initialize Modbus instrument
instrument = minimalmodbus.Instrument(PORT, SLAVE_ADDRESS)
instrument.debug = False  # Set to True for debugging

# Configure serial port settings
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = serial.STOPBITS_ONE
instrument.serial.timeout = 1
instrument.mode = minimalmodbus.MODE_RTU

# Initialize MQTT client
client = mqtt.Client()

def connect_mqtt():
    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        exit(1)

def read_and_publish():
    data = {}
    try:
        for i in range(REGISTER_COUNT):
            register_address = REGISTER_START + i
            try:
                value = instrument.read_register(
                    registeraddress=register_address,
                    functioncode=3
                )
                data[f"register_{register_address}"] = value
                # Publish individual register value
                client.publish(f"{MQTT_TOPIC_BASE}/{register_address}", value)
            except Exception as e:
                print(f"Error reading register {register_address}: {e}")
                data[f"register_{register_address}"] = None

        # Publish all values as JSON
        client.publish(f"{MQTT_TOPIC_BASE}/all", json.dumps(data))
        print(f"Published data: {data}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Starting Modbus to MQTT bridge...")
    connect_mqtt()
    
    try:
        while True:
            read_and_publish()
            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Script finished.")

if __name__ == "__main__":
    main()