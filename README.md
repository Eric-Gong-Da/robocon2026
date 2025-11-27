# Robocon 2026 Robot System

A modular robot control system using ZMQ for inter-process communication.

## Architecture

```
robocon2026/
├── chassis_hardware/      # Hardware interface nodes
│   └── src/
│       ├── sensor_node.py # Arduino encoder & IMU reader
│       └── README.md
├── config/                # System configuration
│   ├── nodes.json         # Node registry and launcher config
│   ├── sensor_config.json # Sensor hardware configuration
│   └── README.md
├── tools/                 # Development and monitoring tools
│   └── zmq_monitor/       # ZMQ publisher discovery and monitoring
│       ├── monitor.py
│       └── README.md
├── run_nodes.sh           # Launch all configured nodes
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
pip install pyzmq pyserial
```

### 2. Configure Sensors

Edit `config/sensor_config.json`:

```json
{
  "serial": {
    "port": "/dev/cu.usbmodem11401",
    "baud_rate": 921600
  },
  "zmq": {
    "port": 5555
  }
}
```

Find your serial port:
- **macOS**: `ls /dev/cu.*`
- **Linux**: `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`

### 3. Run the System

```bash
./run_nodes.sh
```

This starts all enabled nodes from `config/nodes.json`.

### 4. Monitor Data

In a new terminal:

```bash
cd tools/zmq_monitor

# Discover active publishers
python monitor.py list

# Monitor sensor data
python monitor.py monitor 5555
```

## Components

### Chassis Hardware

**sensor_node.py** - Reads encoder and IMU data from Arduino via serial, publishes to ZMQ.

- **Reads**: 3 floats (e1, e2, imu) from Arduino
- **Publishes**: JSON on ZMQ (`{"e1": float, "e2": float, "imu": float, "timestamp": float}`)
- **Config**: `config/sensor_config.json`

### Configuration

All system configuration is centralized in `config/`:

- **nodes.json**: Which nodes to run and their paths
- **sensor_config.json**: Serial port, encoder pins, ZMQ settings

See `config/README.md` for details.

### ZMQ Monitor Tool

Developer tool for debugging ZMQ communication:

```bash
# Discover all active publishers with data types
python monitor.py list

# Monitor by port
python monitor.py monitor 5555

# (Optional) Register friendly names
python monitor.py add sensors 5555 --desc "Chassis sensors"
python monitor.py monitor sensors
```

See `tools/zmq_monitor/README.md` for full documentation.

## Workflow

### Adding a New Node

1. **Create the node**:
   ```bash
   # Example: motor control node
   touch chassis_hardware/src/motor_node.py
   ```

2. **Add to launcher**:
   Edit `config/nodes.json`:
   ```json
   {
     "nodes": [
       {
         "name": "motor_node",
         "path": "chassis_hardware/src/motor_node.py",
         "enabled": true,
         "description": "Motor control"
       }
     ]
   }
   ```

3. **Run**:
   ```bash
   ./run_nodes.sh
   ```

### Development Workflow

```bash
# Terminal 1: Run nodes
./run_nodes.sh

# Terminal 2: Monitor data
cd tools/zmq_monitor
python monitor.py list
python monitor.py monitor sensors

# Stop all: Ctrl+C in Terminal 1
```

### Debugging

**No data appearing?**
```bash
# Check if publisher is active
cd tools/zmq_monitor
python monitor.py list

# Check serial port
ls /dev/cu.*          # macOS
ls /dev/ttyUSB*       # Linux

# Verify config
cat config/sensor_config.json
```

**Serial port permission denied?** (Linux)
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

## Communication Protocol

### ZMQ Pattern

All nodes use **PUB/SUB** pattern:
- Publishers: Hardware interfaces (sensors, motors)
- Subscribers: Control logic, data logging, monitoring

### Message Format

JSON-serialized dictionaries:

```json
{
  "field1": value,
  "field2": value,
  "timestamp": 1732745565.123
}
```

### Default Ports

- `5555`: Sensor data (encoders, IMU)
- `5556+`: Add new publishers here

Register in ZMQ monitor for easy reference:
```bash
python monitor.py add sensors 5555
```

## Project Structure

```
chassis_hardware/  - Hardware interface nodes
  src/             - Node implementations
    sensor_node.py - Arduino sensor reader
    README.md      - Hardware node documentation

config/            - System configuration
  nodes.json       - Node launcher config
  sensor_config.json - Sensor hardware config
  README.md        - Config documentation

tools/             - Development tools
  zmq_monitor/     - ZMQ debugging tool
    monitor.py     - CLI monitor
    README.md      - Tool documentation

run_nodes.sh       - System launcher script
README.md          - This file
```

## Next Steps

- [ ] Add motor control node
- [ ] Add odometry calculation
- [ ] Add navigation controller
- [ ] Add web interface for monitoring
- [ ] Add data logging

## Resources

- **ZMQ Guide**: https://zguide.zeromq.org/
- **PySerial**: https://pyserial.readthedocs.io/
- **Config**: `config/README.md`
- **Monitor Tool**: `tools/zmq_monitor/README.md`

## License

For Robocon 2026 competition use.
