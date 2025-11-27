import serial
import struct
import time

# ---------------- CONFIGURATION ----------------
# Port from your screenshot
SERIAL_PORT = '/dev/cu.usbmodem11401'
# Must match the Arduino code exactly
BAUD_RATE = 921600
# Struct format: Little-endian (<), three floats (f f f)
# Total size: 4 + 4 + 4 = 12 bytes
STRUCT_FORMAT = '<fff'
PACKET_SIZE = 12


def read_serial():
    try:
        # Open the serial port
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT} @ {BAUD_RATE}...")

        # Clear buffer to avoid reading old garbage data
        ser.reset_input_buffer()

        while True:
            # 1. Read exactly 12 bytes
            data = ser.read(PACKET_SIZE)

            # 2. Check if we got a full packet
            if len(data) == PACKET_SIZE:
                # 3. Unpack binary data into Python variables
                # Returns a tuple: (e1, e2, imu)
                e1_deg, e2_deg, imu_head = struct.unpack(STRUCT_FORMAT, data)

                # 4. Print clean output
                print(f"E1: {e1_deg:6.2f}° | E2: {e2_deg:6.2f}° | IMU: {imu_head:6.2f}°")
            else:
                # If we didn't get 12 bytes, the Arduino might be resetting or disconnected
                pass

    except serial.SerialException as e:
        print(f"Could not open port {SERIAL_PORT}. Is the Arduino Serial Monitor open?")
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
        if 'ser' in locals() and ser.is_open:
            ser.close()


if __name__ == "__main__":
    read_serial()