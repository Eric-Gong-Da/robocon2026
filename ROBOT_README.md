# Robot System Documentation

Complete documentation for the Robocon 2026 robot hardware and software architecture.

## Table of Contents

- [System Overview](#system-overview)
- [Hardware Components](#hardware-components)
- [Nodes and Publishers](#nodes-and-publishers)
- [Configuration](#configuration)
- [Communication Protocol](#communication-protocol)
- [Development Workflow](#development-workflow)

## System Overview

The robot system uses a modular, ZMQ-based architecture where independent nodes communicate via publish/subscribe pattern.

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Arduino   │ Serial  │ Sensor Node  │   ZMQ   │  Control    │
│  (Hardware) │────────>│   (Python)   │────────>│   Nodes     │
└─────────────┘         └──────────────┘         └─────────────┘
```

**Benefits:**
- **Modular**: Add/remove nodes independently
- **Language-agnostic**: Any language with ZMQ bindings
- **Testable**: Mock publishers for testing
- **Scalable**: Distribute across multiple machines

## Hardware Components

### Sensors

#### 1. Encoders (E1, E2)

**Type**: Quadrature encoders  
**Interface**: Arduino digital pins with interrupts  
**Output**: Rotational angle in degrees

**E1 - Left Encoder**
- Pin A: Digital 2
- Pin B: Digital 3
- Purpose: Left wheel rotation tracking

**E2 - Right Encoder**
- Pin A: Digital 4
- Pin B: Digital 5
- Purpose: Right wheel rotation tracking

**Specifications:**
- Resolution: Configured in Arduino firmware
- Update rate: ~100 Hz
- Data type: `float` (degrees)

#### 2. IMU (Inertial Measurement Unit)

**Type**: Heading/orientation sensor  
**Interface**: Arduino (I2C or Serial)  
**Output**: Heading angle in degrees

**Specifications:**
- Range: 0-360°
- Update rate: ~100 Hz
- Data type: `float` (degrees)
- Purpose: Robot orientation tracking

### Communication

**Arduino → Computer**
- Protocol: Serial (UART)
- Baud rate: 921600
- Format: Binary packed struct (`<fff` - 3 little-endian floats)
- Packet size: 12 bytes (4 bytes × 3 floats)

## Nodes and Publishers

### Active Nodes

| Node | Path | Status | Description |
|------|------|--------|-------------|
| sensor_node | `chassis_hardware/src/sensor_node.py` | ✅ Active | Arduino sensor reader |

### Publisher Information

#### sensor_node

**ZMQ Port:** 5555 (default, configurable)  
**Update Rate:** ~100 Hz (Arduino-dependent)  
**Message Format:** JSON

**Published Data:**

```json
{
  "e1": 45.23,
  "e2": -12.45,
  "imu": 180.34,
  "timestamp": 1732745565.123
}
```

**Field Specifications:**

| Field | Type | Unit | Range | Description |
|-------|------|------|-------|-------------|
| `e1` | float | degrees | -∞ to +∞ | Left encoder angle (cumulative) |
| `e2` | float | degrees | -∞ to +∞ | Right encoder angle (cumulative) |
| `imu` | float | degrees | 0 to 360 | IMU heading angle |
| `timestamp` | float | seconds | UNIX time | Message timestamp |

**Data Types (for monitoring):**
```
e1:float, e2:float, imu:float, timestamp:float
```

**Example Subscription (Python):**

```python
import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b'')

while True:
    data = socket.recv_json()
    print(f"E1: {data['e1']:.2f}°, E2: {data['e2']:.2f}°, IMU: {data['imu']:.2f}°")
```

## Configuration

### Sensor Configuration

**File:** `config/sensor_config.json`

```json
{
  "serial": {
    "port": "/dev/cu.usbmodem11401",
    "baud_rate": 921600,
    "timeout": 1
  },
  "encoders": {
    "e1": {
      "pin_a": 2,
      "pin_b": 3,
      "description": "Left encoder"
    },
    "e2": {
      "pin_a": 4,
      "pin_b": 5,
      "description": "Right encoder"
    }
  },
  "imu": {
    "enabled": true,
    "description": "IMU heading sensor"
  },
  "zmq": {
    "port": 5555,
    "publish_rate_hz": 100
  }
}
```

**Configuration Guide:**

1. **Find serial port:**
   ```bash
   # macOS
   ls /dev/cu.*
   
   # Linux
   ls /dev/ttyUSB* /dev/ttyACM*
   ```

2. **Update port in config:**
   ```json
   "serial": {
     "port": "/dev/ttyUSB0",  // Your port here
     "baud_rate": 921600
   }
   ```

3. **Verify Arduino pins match your wiring**

### Node Launcher Configuration

**File:** `config/nodes.json`

```json
{
  "nodes": [
    {
      "name": "sensor_node",
      "path": "chassis_hardware/src/sensor_node.py",
      "enabled": true,
      "description": "Arduino sensor data publisher"
    }
  ]
}
```

**Adding new nodes:**

```json
{
  "name": "motor_node",
  "path": "chassis_hardware/src/motor_node.py",
  "enabled": true,
  "description": "Motor control node"
}
```

## Communication Protocol

### ZMQ Pattern: PUB/SUB

**Publishers** (Hardware interfaces):
- Sensor node (port 5555)
- Motor node (port 5556) - _planned_
- Vision node (port 5557) - _planned_

**Subscribers** (Control/logging):
- Control algorithms
- Data loggers
- Monitoring tools
- Web dashboard

### Message Format

All messages are JSON-serialized dictionaries with timestamps:

```json
{
  "field1": value,
  "field2": value,
  "timestamp": 1732745565.123
}
```

### Port Allocation

| Port | Publisher | Data | Status |
|------|-----------|------|--------|
| 5555 | sensor_node | Encoders, IMU | ✅ Active |
| 5556 | motor_node | Motor commands | 🔜 Planned |
| 5557 | vision_node | Camera data | 🔜 Planned |
| 5558 | odom_node | Odometry | 🔜 Planned |

## Development Workflow

### Running the System

```bash
# Start all nodes
./run_nodes.sh

# Output:
# Starting nodes from config/nodes.json
# ==================================
# Starting sensor_node: Arduino sensor data publisher
#   Path: /path/to/sensor_node.py
#   PID: 12345
```

### Monitoring Data

```bash
# Terminal 1: Run nodes
./run_nodes.sh

# Terminal 2: Monitor
cd tools/zmq_monitor
python monitor.py list                    # Discover publishers
python monitor.py monitor 5555            # Monitor sensors
```

### Adding a New Node

1. **Create node file:**
   ```bash
   touch chassis_hardware/src/my_node.py
   ```

2. **Implement ZMQ publisher:**
   ```python
   import zmq
   import time
   
   context = zmq.Context()
   socket = context.socket(zmq.PUB)
   socket.bind("tcp://*:5556")
   
   while True:
       data = {"value": 123, "timestamp": time.time()}
       socket.send_json(data)
       time.sleep(0.01)
   ```

3. **Add to config:**
   ```json
   {
     "name": "my_node",
     "path": "chassis_hardware/src/my_node.py",
     "enabled": true
   }
   ```

4. **Run:**
   ```bash
   ./run_nodes.sh
   ```

### Debugging

**Check active publishers:**
```bash
cd tools/zmq_monitor
python monitor.py list
```

**Monitor specific data:**
```bash
python monitor.py monitor 5555
```

**Check serial connection:**
```bash
# List ports
ls /dev/cu.*        # macOS
ls /dev/ttyUSB*     # Linux

# Test with original script
python rad.py
```

**Verify configuration:**
```bash
cat config/sensor_config.json
cat config/nodes.json
```

## Next Steps

### Planned Nodes

- [ ] **motor_node** - Motor control and command execution
- [ ] **odom_node** - Odometry calculation from encoders
- [ ] **nav_node** - Navigation controller
- [ ] **vision_node** - Camera/vision processing
- [ ] **logger_node** - Data logging to file

### Integration

- [ ] Web dashboard for monitoring
- [ ] ROS 2 bridge (see AGENTS.md)
- [ ] Real-time plotting
- [ ] Autonomous navigation stack

## Troubleshooting

**No serial data:**
1. Check Arduino USB connection
2. Verify port in `config/sensor_config.json`
3. Check baud rate matches Arduino (921600)
4. Test with `python rad.py`

**Permission denied on Linux:**
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

**No ZMQ messages:**
1. Check node is running: `ps aux | grep sensor_node`
2. Verify port: `python monitor.py list`
3. Check firewall settings

**Incorrect data values:**
1. Verify Arduino firmware
2. Check struct format (`<fff`)
3. Test binary protocol with `rad.py`

## Resources

- **ZMQ Guide:** https://zguide.zeromq.org/
- **PySerial Docs:** https://pyserial.readthedocs.io/
- **Project Config:** `config/README.md`
- **Monitor Tool:** `tools/zmq_monitor/README.md`

---

**Built with [Qoder](https://qoder.com)**
