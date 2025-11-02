#!/usr/bin/env python3
# change_slave_address.py
# Works on every Linux, every Python, every WP3084ADAM
# Run once → power-cycle → delete file → drink beer

import minimalmodbus

PORT   = '/dev/ttyUSB1'   # ← same as your MQTT script
NEW_ID = 17               # ← 1..247

# Create instrument with ANY address (will be ignored for broadcast)
instrument = minimalmodbus.Instrument(PORT, 1)   # 1 = dummy

# Serial settings — identical to your working MQTT script
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity   = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout  = 1

# ────── BROADCAST WRITE ──────
instrument.address = 0                      # ← 0 = broadcast
instrument.write_register(100, NEW_ID, functioncode=6)

print(f"WP3084ADAM slave ID changed to {NEW_ID}")
print("Power-cycle the module NOW → done forever")