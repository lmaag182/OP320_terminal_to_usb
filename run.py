import time
import threading
import serial
from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
import logging

# Set up logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)  # Debug mode for detailed logs

# Define the Modbus data store for slave ID 1
datablock = ModbusSequentialDataBlock(0, [0] * 100)  # 100 holding registers
store = {
    1: {  # Slave ID 1
        'co': ModbusSequentialDataBlock(0, [0] * 100),  # Coils
        'di': ModbusSequentialDataBlock(0, [0] * 100),  # Discrete Inputs
        'hr': datablock,  # Holding Registers
        'ir': ModbusSequentialDataBlock(0, [0] * 100)   # Input Registers
    }
}

# Initialize server context
context = ModbusServerContext()  # No 'slaves' or 'datastore' keywords
context[1] = store[1]  # Assign store for slave ID 1

def run_server():
    # Serial port settings
    port = '/dev/ttyUSB1'  # Confirmed port
    baudrate = 9600
    parity = serial.PARITY_EVEN
    bytesize = serial.EIGHTBITS
    stopbits = serial.STOPBITS_ONE
    timeout = 1

    log.info(f"Starting Modbus RTU slave on {port} at {baudrate} baud...")
    try:
        StartSerialServer(
            context=context,
            port=port,
            baudrate=baudrate,
            parity=parity,
            bytesize=bytesize,
            stopbits=stopbits,
            timeout=timeout,
            framer='rtu'
        )
    except Exception as e:
        log.error(f"Failed to start server: {e}")

def update_registers():
    while True:
        try:
            # Set holding register 0 (40001) to 1
            datablock.setValues(0, [1])
            log.info("Set holding register 0 to 1")
        except Exception as e:
            log.error(f"Error updating register: {e}")
        time.sleep(1)  # Update every second

if __name__ == "__main__":
    # Set initial value
    try:
        datablock.setValues(0, [1])
        log.info("Initial value set: holding register 0 = 1")
    except Exception as e:
        log.error(f"Error setting initial value: {e}")
    
    # Start update_registers in a separate thread
    update_thread = threading.Thread(target=update_registers, daemon=True)
    update_thread.start()
    
    try:
        run_server()
    except KeyboardInterrupt:
        log.info("Server stopped.")
    except Exception as e:
        log.error(f"Server error: {e}")