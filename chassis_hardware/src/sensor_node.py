import serial
import struct
import zmq
import time
import json
import os


STRUCT_FORMAT = '<fff'
PACKET_SIZE = 12


def load_config():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_path = os.path.join(project_root, 'config', 'sensor_config.json')
    
    if not os.path.exists(config_path):
        print(f"Warning: Config file not found at {config_path}")
        print("Using default configuration")
        return {
            'serial': {'port': '/dev/cu.usbmodem11401', 'baud_rate': 921600, 'timeout': 1},
            'zmq': {'port': 5555, 'publish_rate_hz': 100},
            'encoders': {'e1': {}, 'e2': {}},
            'imu': {'enabled': True}
        }
    
    with open(config_path, 'r') as f:
        return json.load(f)


def main():
    config = load_config()
    
    serial_port = config['serial']['port']
    baud_rate = config['serial']['baud_rate']
    timeout = config['serial']['timeout']
    zmq_port = config['zmq']['port']
    
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://*:{zmq_port}")
    
    print("Sensor Node Configuration:")
    print(f"  Serial: {serial_port} @ {baud_rate} baud")
    print(f"  ZMQ Publisher: port {zmq_port}")
    print(f"  E1 pins: A={config['encoders']['e1'].get('pin_a', 'N/A')}, B={config['encoders']['e1'].get('pin_b', 'N/A')}")
    print(f"  E2 pins: A={config['encoders']['e2'].get('pin_a', 'N/A')}, B={config['encoders']['e2'].get('pin_b', 'N/A')}")
    print(f"  IMU: {'enabled' if config['imu']['enabled'] else 'disabled'}")
    print()
    
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=timeout)
        print(f"Publishing sensor data on port {zmq_port}")
        print(f"Reading from {serial_port}")
        
        ser.reset_input_buffer()
        
        while True:
            data = ser.read(PACKET_SIZE)
            
            if len(data) == PACKET_SIZE:
                e1_deg, e2_deg, imu_head = struct.unpack(STRUCT_FORMAT, data)
                
                sensor_data = {
                    'e1': e1_deg,
                    'e2': e2_deg,
                    'imu': imu_head,
                    'timestamp': time.time()
                }
                
                socket.send_json(sensor_data)
                print(f"E1: {e1_deg:6.2f}° | E2: {e2_deg:6.2f}° | IMU: {imu_head:6.2f}°")
                
    except serial.SerialException as e:
        print(f"Could not open port {serial_port}")
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
        socket.close()
        context.term()


if __name__ == "__main__":
    main()