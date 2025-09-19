# OOP Spike 3 module

Python object-oriented wrapper for LEGO® Spike™ 3.
Allows return object-oriented programing to Spike™ Prime 3 without changing firmware. 


Example of typical program with the oop wrapper:
```python
from oop.parameters import Port, Direction, Stop
from oop.devices import Motor
from oop.robotics import DriveBase

left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=8*16)

for _ in range(4):
    robot.straight(100)
    robot.turn(90)

```

## Overview



---

## 🎯 Goals



---

## 🧠 Why This Wrapper?



### ✅ No Firmware Changes


---

## 📁 Module Structure

The module is organized into five main files:

| File Name           | Purpose                                                                 |
|---------------------|-------------------------------------------------------------------------|
| `__init__.py`       | Empty file that marks the folder as a Python package                    |
| `devices.py`        | Classes for motors and sensors (SPIKE and Powered Up)                   |
| `parameters.py`     | Constants for ports, directions, colors, icons, and other settings      |
| `hub.py`            | Classes for controlling the SPIKE Prime Hub (buttons, display, speaker) |
| `robotics.py`       | Classes for driving robots (`DriveBase`, `Car`) with movement logic     |


---

## 🚀 Getting Started



Example:

```python
```

LEGO® is a trademark of the LEGO Group of companies which does not sponsor, authorize or endorse this project.
