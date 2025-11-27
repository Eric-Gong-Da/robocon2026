# Configuration

## nodes.json

Configuration file for all system nodes.

## sensor_config.json

Configuration for the sensor node (Arduino encoder and IMU reader).

### Structure

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

---

## nodes.json

Configuration file for all system nodes.

### Structure

```json
{
  "nodes": [
    {
      "name": "node_name",
      "path": "relative/path/to/node.py",
      "enabled": true,
      "description": "Node description"
    }
  ]
}
```

### Fields

- **name**: Unique identifier for the node
- **path**: Relative path from project root to the Python script
- **enabled**: `true` to run, `false` to skip (optional, default: `true`)
- **description**: Human-readable description (optional)

### Example

```json
{
  "nodes": [
    {
      "name": "sensor_node",
      "path": "chassis_hardware/src/sensor_node.py",
      "enabled": true,
      "description": "Arduino sensor data publisher"
    },
    {
      "name": "motor_node",
      "path": "chassis_hardware/src/motor_node.py",
      "enabled": false,
      "description": "Motor control node (disabled)"
    }
  ]
}
```

## Usage

1. **Add a new node:**
   ```json
   {
     "name": "my_node",
     "path": "path/to/my_node.py",
     "enabled": true,
     "description": "My custom node"
   }
   ```

2. **Disable a node temporarily:**
   Set `"enabled": false`

3. **Run all enabled nodes:**
   ```bash
   ./run_nodes.sh
   ```

4. **Stop all nodes:**
   Press `Ctrl+C`

## Notes

- All paths are relative to project root
- Nodes run in parallel as background processes
- Output from all nodes is shown in the terminal
- Ctrl+C stops all running nodes gracefully