import minimalmodbus
import serial
import time

# --- Modbus RTU configuration ---
# You might need to change the slave address.
SLAVE_ADDRESS = 1
PORT = '/dev/ttyUSB1'

# --- Values to read ---
# 4x registers are holding registers.
# Let's try reading from register 1.
REGISTER_ADDRESS = 2

# Initialize Modbus instrument
instrument = minimalmodbus.Instrument(PORT, SLAVE_ADDRESS)
instrument.debug = True

# Configure serial port settings
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = serial.STOPBITS_ONE
instrument.serial.timeout = 1
instrument.mode = minimalmodbus.MODE_RTU

print(f"Attempting to READ from register {REGISTER_ADDRESS} on slave {SLAVE_ADDRESS}...")

try:
    # Let's try to READ from the register instead of writing.
    # If this succeeds, it means the register is likely read-only.
    value = instrument.read_register(
        registeraddress=REGISTER_ADDRESS,
        functioncode=3  # Function code for reading a holding register
    )
    print(f"Successfully READ from register {REGISTER_ADDRESS}. Value: {value}")

except minimalmodbus.NoResponseError:
    print("Error: No response from the instrument. Check connection and slave address.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # The port is automatically closed by minimalmodbus when the instrument object is destroyed.
    print("Script finished.")