# Robocon 2026 Robot System

A modular robot control system using ZMQ for inter-process communication.

📖 **Documentation:**
- [Robot System Documentation](ROBOT_README.md) - Hardware, sensors, and nodes
- [ZMQ Monitor Tool Guide](TOOL_GUIDE.md) - Debugging and monitoring tool

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Hardware

Edit `config/sensor_config.json` with your serial port:

```bash
# Find your Arduino port
ls /dev/cu.*          # macOS
ls /dev/ttyUSB*       # Linux
```

Update the port in `config/sensor_config.json`.

### 3. Run the System

```bash
./run_nodes.sh
```

### 4. Monitor Data

```bash
cd tools/zmq_monitor
python monitor.py list              # Discover publishers
python monitor.py monitor 5555      # Monitor sensor data
```

## Architecture

```
robocon2026/
├── chassis_hardware/      # Hardware interface nodes
│   └── src/
│       └── sensor_node.py # Arduino sensor reader
├── config/                # System configuration
│   ├── nodes.json         # Node launcher config
│   └── sensor_config.json # Hardware config
├── tools/                 # Development tools
│   └── zmq_monitor/       # ZMQ debugging tool
├── run_nodes.sh           # System launcher
├── ROBOT_README.md        # Robot system documentation
└── TOOL_GUIDE.md          # Tool usage guide
```

## Project Structure

```
chassis_hardware/  - Hardware interface nodes
  src/             - Node implementations
    sensor_node.py - Arduino encoder & IMU reader

config/            - System configuration
  nodes.json       - Node launcher config
  sensor_config.json - Sensor hardware config

tools/             - Development tools
  zmq_monitor/     - ZMQ publisher monitor
    monitor.py     - CLI tool
```

## Development

Built with [Qoder](https://qoder.com) - AI-powered development assistant.

## License

For Robocon 2026 competition use.