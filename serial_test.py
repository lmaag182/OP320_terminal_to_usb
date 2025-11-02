#!/usr/bin/env python3
import minimalmodbus
import serial
import time
import paho.mqtt.client as mqtt
import json

# ------------------- CONFIG -------------------
SLAVES         = [1, 17]
PORT           = '/dev/ttyUSB0'
BAUDRATE       = 9600
REGISTER_START = 0
REGISTER_COUNT = 8
SCAN_INTERVAL  = 1.0

MQTT_BROKER    = "192.168.50.75"
MQTT_PORT      = 1883
MQTT_BASE      = "wp3082adam/registers"
# ---------------------------------------------

# One instrument → we just change .address before every call
instr = minimalmodbus.Instrument(PORT, 1)  # dummy address
instr.serial.baudrate = BAUDRATE
instr.serial.bytesize = 8
instr.serial.parity   = serial.PARITY_NONE
instr.serial.stopbits = serial.STOPBITS_ONE
instr.serial.timeout  = 0.3   # short but safe
instr.mode = minimalmodbus.MODE_RTU
instr.debug = False
instr.clear_buffers_before_each_transaction = True

# MQTT
client = mqtt.Client(client_id="modbus_bridge")
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
client.loop_start()
time.sleep(0.5)

def read_slave(sid: int) -> dict:
    instr.address = sid
    data = {}
    try:
        # ONE single request for 8 registers → fastest + least bus load
        regs = instr.read_registers(REGISTER_START, REGISTER_COUNT, functioncode=3)
        for i, v in enumerate(regs):
            data[f"register_{REGISTER_START + i}"] = float(v)
    except Exception as e:
        print(f"Slave {sid} → {e}")
        for i in range(REGISTER_COUNT):
            data[f"register_{REGISTER_START + i}"] = None
    return data

def publish(sid: int, data: dict):
    base = f"{MQTT_BASE}/slave{sid}"
    for k, v in data.items():
        client.publish(f"{base}/{k}", payload=str(v) if v is not None else "null")
    client.publish(f"{base}/all", json.dumps(data))

# ------------------- MAIN -------------------
print("Modbus → MQTT bridge STARTED – slaves 1 + 17")
while True:
    start = time.time()

    # ---- ONE request per slave, back-to-back ----
    for sid in SLAVES:
        values = read_slave(sid)
        publish(sid, values)

    # ---- sleep the remainder of the second ----
    elapsed = time.time() - start
    time.sleep(max(0.01, SCAN_INTERVAL - elapsed))