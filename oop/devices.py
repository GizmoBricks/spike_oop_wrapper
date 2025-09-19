from oop.parameters import Port, Direction, Stop, Color
import runloop
import device
import motor
import color_matrix
import color_sensor
import distance_sensor
import force_sensor

class Device:
    """
    Base class representing any LEGO® Powered Up / SPIKE™ Prime device.

    This class provides a unified interface for interacting with devices 
    connected to a specific hub port, such as motors, sensors, or lights.
    It wraps low-level `device` module calls with more descriptive methods.
    """
    
    def __init__(self, port: Port):
        """
        Initialize a device on the specified hub port.

        Args:
            port (Port): The hub port where the device is physically connected.

        Raises:
            RuntimeError: If no device is detected on the given port.
        """
        self.port = port
        
        try:
            self.get()
        except OSError:
            raise RuntimeError("Device is not connected to {port}".format(
                port=Port.__dict[self.port]))
        
    def get(self) -> tuple[int]:
        """
        Retrieve the raw data values from the device.

        Returns:
            tuple[int]: A tuple of integer values representing the device's 
                        current raw sensor or status data.

        Note:
            The meaning of the returned values depends on the device type 
            and its current mode.
        """
        return device.data(self.port)
        
    def get_duty_cycle(self) -> int:
        """
        Get the current duty cycle of the device.

        Returns:
            int: The duty cycle as a signed integer in the range -10000 to 10000, 
                 where positive values indicate forward power and negative values 
                 indicate reverse power.
        """
        return device.get_duty_cycle(self.port)

    def set_duty_cycle(self, duty_cycle: int):
        """
        Set the duty cycle (PWM power) for the device.

        Args:
            duty_cycle (int): The desired duty cycle, from -10000 (full reverse) 
                              to 10000 (full forward).

        Note:
            This method directly controls the power level without speed regulation.
        """
        device.set_duty_cycle(self.port, duty_cycle)

    def ready(self) -> bool:
        """
        Check whether the device is ready for operation.

        Returns:
            bool: True if the device is ready to receive commands, False otherwise.
        """
        return device.ready(self.port)
    
    def id(self):
        """
        Get the unique numeric ID of the connected LEGO® Powered Up / SPIKE™ Prime device.

        Returns:
            int: The numeric device ID.

        Known Powered Up device IDs:
            0   – No device / port empty
            1   – Wedo 2.0 Medium Motor
            2   – Powered Up Train Motor
            8   – Powered Up Light
            38  – BOOST Interactive Motor
            46  – Technic Large Motor
            47  – Technic Extra Large Motor
            48  – SPIKE Medium Angular Motor
            49  – SPIKE Large Angular Motor
            65  – SPIKE Small Angular Motor
            75  – Technic Medium Angular Motor
            76  – Technic Large Angular Motor
            34   – Wedo 2.0 Tilt Sensor
            35   – Wedo 2.0 Infrared Motion Sensor
            37   – BOOST Color Distance Sensor
            61   – SPIKE Color Sensor
            62   – SPIKE Ultrasonic Sensor
            63   – SPIKE Force Sensor
            64   – SPIKE 3x3 Color Light Matrix

        Note:
            This list is not exhaustive — LEGO occasionally adds new devices with 
            different IDs. The meaning of the ID is fixed per device type.
        """
        return(device.id(self.port))
    
    def set_mode(self, mode: int):
        """
        Set the operational mode of the connected LEGO® Powered Up / SPIKE™ Prime device.

        Args:
            mode (int): The mode index to activate.  
                        Available modes depend on the device type.  
                        Common examples include:

            **Motors (e.g., SPIKE Prime Medium/Large Angular Motor)**:
                0 – Power (duty cycle, -10000 to 10000)  
                1 – Speed (degrees/sec)  
                2 – Position (absolute, in degrees)  
                3 – Position (relative, in degrees)  
                4 – Position + Speed combined  
                5 – Position + Power combined  
                6 – Speed + Power combined  
                7 – Position + Speed + Power combined

            **Color Sensor**:
                0 – Reflected light intensity (0–100%)  
                1 – Ambient light intensity (0–100%)  
                2 – Color index (0–10, where 0 = none, 1 = black, etc.)  
                3 – Raw RGB values  
                4 – HSV values  
                5 – Calibration mode

            **Distance Sensor**:
                0 – Distance in mm  
                1 – Presence detection (boolean)  
                2 – Raw distance + partial reflectivity  
                3 – Single-shot measurement  
                4 – Continuous measurement

            **Force Sensor**:
                0 – Force in Newtons  
                1 – Boolean pressed/released  
                2 – Raw analog value

        Notes:
            - Mode numbers are defined by the LEGO Wireless Protocol (LPF2) and vary by device.
            - Setting an unsupported mode for a device will have no effect or may raise an error.
            - Changing the mode alters the data returned by `get()`.

        """
        device.set_mode(self.port, mode)
    
    def reset_mode(self):
        """
        Reset the device to its default mode.
        """
        device.reset_mode(self.port)
      
    #def write_mode(self, mode: int, data: str):
    #    "TODO: try to understand how the device.write_mode method can be used"
    #    raise NotImplementedError('The metod is not implemented yet')
    
    
    
class Motor(Device):
    """
    High-level control for LEGO® Powered Up / SPIKE™ Prime motors with built-in rotation sensors.

    This class extends `Device` to provide motion control methods such as
    running for a set time, angle, or to a target position, with optional
    acceleration, deceleration, and stop behaviors.
    """
    
    def __init__(self, port: Port,
                 positive_direction: Direction = Direction.CLOCKWISE,
                 default_stop: Stop = Stop.SMART_BRAKE,
                 acceleration: int = 1000,
                 deceleration: int = 1000):
        """
        Initialize a motor on the specified hub port.

        Args:
            port (Port): The hub port where the motor is connected.
            positive_direction (Direction): The direction the motor should turn
                when given a positive speed or angle.
                Common values:
                    - Direction.CLOCKWISE
                    - Direction.COUNTERCLOCKWISE
            default_stop (Stop): The default stop action when the motor halts.
                Available Stop modes:
                    0 – CONTINUE  
                        → Motor keeps running at its current velocity until it 
                          receives another command.
                    1 – COAST  
                        → Motor coasts freely until it comes to a stop.
                    2 – BRAKE  
                        → Motor brakes to a stop and continues to apply braking 
                          force after stopping.
                    3 – HOLD  
                        → Motor actively holds its position after stopping.
                    4 – SMART_COAST  
                        → Motor coasts freely until it comes to a stop. 
                          Compensates for inaccuracies in the next command.
                    5 – SMART_BRAKE  
                        → Motor brakes to a stop and continues braking afterward.  
                          Compensates for inaccuracies in the next command.
            acceleration (int): Acceleration in degrees/sec² (1–10000).
            deceleration (int): Deceleration in degrees/sec² (1–10000).

        Raises:
            RuntimeError: If the connected device is not recognized as a motor.
        """
        super().__init__(port)
        
        if positive_direction == 1:
            self.positive_direction = -1
        else:
            self.positive_direction = 1
        
        self.default_stop = default_stop
        self.acceleration = acceleration
        self.deceleration = deceleration
        
        try:
            self.angle()
        except OSError:
            raise RuntimeError(
                "Device connected to {port} is not a motor".format(
                    port=Port.__dict[self.port]))
    
    @staticmethod
    def _run_async(coro, wait: bool):
        """
        Internal helper to optionally run motor commands asynchronously.

        Args:
            coro: The coroutine returned by a motor control function.
            wait (bool): If True, waits for the command to complete before
                         continuing program execution. If False, returns
                         immediately and allows interruption by other commands.
        """
        if wait:
            runloop.run(coro)
        else:
            return coro
        
    def angle(self) -> int:
        """
        Get the cumulative (relative) rotation angle of the motor.

        Returns:
            int: The total rotation in degrees since the last reset.
                 Positive values follow the `positive_direction` setting.
        """
        return motor.relative_position(self.port) * self.positive_direction
    
    def absolute_angle(self) -> int:
        """
        Get the absolute rotation angle of the motor.

        Returns:
            int: The motor's position in degrees within its -179–180 range,
                 independent of resets and the 'positive_directions' settings.
        """
        return motor.absolute_position(self.port)
        
    def reset_angle(self, angle: int = 0):
        """
        Reset the cumulative rotation angle to a given value.

        Args:
            angle (int): The new cumulative angle in degrees.
                         Defaults to 0.
        """
        motor.reset_relative_position(self.port, angle * self.positive_direction)

    def speed(self) -> int:
        """
        Get the current rotational speed of the motor.

        Returns:
            int: Speed in degrees per second (positive or negative).
        """
        return motor.velocity(self.port) * self.positive_direction
    
    def stop(self, then: Stop | None = None):
        """
        Stop the motor using a specified stop mode.

        Args:
            then (Stop, optional): Stop behavior to apply.
                                   Defaults to `self.default_stop`.
        """
        
        motor.stop(self.port, stop=then or self.default_stop)
    
    def run(self, speed: int):
        """
        Run the motor continuously at a given speed.

        Args:
            speed (int): Speed in degrees per second.
                         Positive/negative follows `positive_direction`.
        """
        motor.run(self.port, speed*self.positive_direction)

    def run_time(self, speed:int,
                 time: int,
                 then: Stop | None = None,
                 wait: bool = True):
        """
        Run the motor at a given speed for a set duration.

        Args:
            speed (int): Speed in degrees per second.
            time (int): Duration in milliseconds.
            then (Stop, optional): Stop behavior after the run.
                                   Defaults to `self.default_stop`.
            wait (bool): If True, block until complete.
                         If False, run asynchronously and allow interruption.
        """
        coro = motor.run_for_time(self.port, time, speed*self.positive_direction, stop=then or self.default_stop)
        self._run_async(coro, wait)
        
    def run_angle(self, speed: int,
                  angle: int,
                  then: Stop | None = None,
                  wait: bool = True):
        """
        Run the motor at a given speed for a specific rotation angle.

        Args:
            speed (int): Speed in degrees per second.
            angle (int): Rotation in degrees (positive or negative).
            then (Stop, optional): Stop behavior after the run.
                                   Defaults to `self.default_stop`.
            wait (bool): If True, block until complete.
                         If False, run asynchronously and allow interruption.
        """
        coro = motor.run_for_degrees(self.port, angle*self.positive_direction, speed, stop=then or self.default_stop)
        self._run_async(coro, wait)

    def run_target(self, speed:int,
                   target: int,
                   then: Stop | None = None,
                   wait: bool = True):
        """
        Run the motor at a given speed until it reaches a target relative position.

        Args:
            speed (int): Speed in degrees per second.
            target (int): Target relative position in degrees from the current angle.
            then (Stop, optional): Stop behavior after the run.
                                   Defaults to `self.default_stop`.
            wait (bool): If True, block until complete.
                         If False, run asynchronously and allow interruption.
        """
        coro = motor.run_to_relative_position(self.port, target * self.positive_direction, speed, stop=then or self.default_stop)
        self._run_async(coro, wait)

    def run_absolute_angle(self, speed: int,
                           angle: int,
                           direction: Direction = Direction.CLOCKWISE,
                           then: Stop | None = None,
                           wait: bool = True):
        """
        Run the motor at a given speed to a specific absolute position.

        Args:
            speed (int): Speed in degrees per second.
            angle (int): Target absolute position in degrees, in the range -179 to 180.
                         Positive values follow the standard LEGO® SPIKE™ Prime convention.
            direction (Direction): The path the motor should take to reach the target.
                Available Direction modes:
                    0 – CLOCKWISE  
                        → Rotate clockwise until the target position is reached.
                    1 – COUNTERCLOCKWISE  
                        → Rotate counterclockwise until the target position is reached.
                    2 – SHORTEST_PATH  
                        → Rotate in whichever direction results in the shortest travel distance.
                    3 – LONGEST_PATH  
                        → Rotate in whichever direction results in the longest travel distance.
            then (Stop, optional): Stop behavior after the run.  
                Defaults to `self.default_stop`. See `__init__` docstring for full Stop mode list.
            wait (bool): If True, block until the movement is complete.  
                         If False, run asynchronously and allow interruption by other commands.

        Notes:
            - The `angle` parameter refers to the motor's absolute position within its -179° to 180° range.
            - The `direction` parameter determines the travel path, not just the final orientation.
            - Using SHORTEST_PATH or LONGEST_PATH can be useful for optimizing movement or testing.
        """        
        coro = motor.run_to_absolute_position(self.port, angle, speed, direction=direction, stop=then or self.default_stop)
        self._run_async(coro, wait)


class ColorMatrix(Device):
    """
    High-level control for the LEGO® SPIKE™ Essential Color Matrix.

    The Color Matrix is a 3×3 grid of RGB LEDs that can display colors
    at adjustable brightness levels. This class provides methods to
    set individual pixels, clear the display, and update the entire grid.
    """

    def __init__(self, port: Port):
        """
        Initialize a Color Matrix on the specified hub port.

        Args:
            port (Port): The hub port where the Color Matrix is connected.

        Raises:
            RuntimeError: If no Color Matrix is detected on the given port.
        """
        super().__init__(port)
        try:
            color_matrix.clear(self.port)
        except OSError:
            raise RuntimeError(
                "A Color Matrix is not connected to port {port}".format(
                    port=Port.__dict[self.port]
                )
            )

    def clear(self):
        """
        Turn off all pixels on the Color Matrix.

        This sets every pixel's brightness to 0, effectively blanking the display.
        """
        color_matrix.clear(self.port)

    def get_pixel(self, x: int, y: int) -> tuple[int, int]:
        """
        Retrieve the current color and brightness of a specific pixel.

        Args:
            x (int): The X coordinate of the pixel (0–2, left to right).
            y (int): The Y coordinate of the pixel (0–2, top to bottom).

        Returns:
            tuple[int, int]: A tuple `(color, brightness)` where:
                - `color` (int): Color index (0–10) or `Color` constant.
                - `brightness` (int): Brightness level (0–10).

        Notes:
            - Color indices follow the `Color` mapping, e.g.:
                0 – NONE, 1 – BLACK, 2 – PINK, 3 – PURPLE, 4 – BLUE,
                5 – LIGHT_BLUE, 6 – CYAN, 7 – GREEN, 8 – YELLOW,
                9 – ORANGE, 10 – RED.
            - Brightness 0 means off; 10 is maximum brightness.
        """
        return color_matrix.get_pixel(self.port, x, y)

    def set_pixel(self, x: int, y: int, color: int | Color, brightness: int = 10):
        """
        Set the color and brightness of a specific pixel.

        Args:
            x (int): The X coordinate of the pixel (0–2).
            y (int): The Y coordinate of the pixel (0–2).
            color (int | Color): Color index (0–10) or `Color` constant.
            brightness (int): Brightness level (0–10). Defaults to 10 (max).

        Notes:
            - Coordinates outside 0–2 will raise an error.
            - Brightness 0 turns the pixel off regardless of color.
        """
        color_matrix.set_pixel(self.port, x, y, (color, brightness))

    def show(self, pixels: list[tuple[int, int]]):
        """
        Set colors and brightness for all pixels in the Color Matrix at once.

        Args:
            pixels (list[tuple[int, int]]): A flat list of 9 tuples, each `(color, brightness)`:
                - `color` (int | Color): Color index (0–10) or `Color` constant.
                - `brightness` (int): Brightness level (0–10).

        Example:
            To set all pixels to red at full brightness:
            ```python
            matrix.show([(Color.RED, 10)] * 9)
            ```

        Notes:
            - The list must contain exactly 9 pixel tuples, ordered row by row.
            - This method is more efficient than calling `set_pixel()` repeatedly.
        """
        color_matrix.show(self.port, pixels)


class ColorSensor(Device):
    """
    High-level control for the LEGO® SPIKE™ Prime.

    The Color Sensor can detect colors, measure reflected light intensity,
    and return raw RGB + intensity values. This class provides a simple
    interface to access those readings.
    """

    def __init__(self, port: int):
        """
        Initialize a Color Sensor on the specified hub port.

        Args:
            port (int): The hub port where the Color Sensor is connected.

        Raises:
            RuntimeError: If no Color Sensor is detected on the given port.
        """
        super().__init__(port)
        try:
            color_sensor.color(self.port)
        except OSError:
            raise RuntimeError(
                "A Color Sensor is not connected to port {port}".format(
                    port=Port.__dict[self.port]
                )
            )

    def color(self) -> int:
        """
        Detect the currently visible color.

        Returns:
            int: Color index (0–10):
                0 – NONE  
                1 – BLACK  
                2 – PINK  
                3 – PURPLE  
                4 – BLUE  
                5 – LIGHT_BLUE  
                6 – CYAN  
                7 – GREEN  
                8 – YELLOW  
                9 – ORANGE  
                10 – RED

        Notes:
            - The detected color depends on lighting conditions and surface properties.
            - For more precise readings, use `rgbi()` and process the raw values.
        """
        return color_sensor.color(self.port)

    def reflection(self) -> int:
        """
        Measure the reflected light intensity from the surface in front of the sensor.

        Returns:
            int: Reflection percentage (0–100), where:
                - 0 = no reflection (completely dark)
                - 100 = maximum reflection (very bright/white surface)

        Notes:
            - This mode uses a built-in light source to illuminate the surface.
            - Useful for line-following and surface contrast detection.
        """
        return color_sensor.reflection(self.port)

    def rgbi(self) -> tuple[int, int, int, int]:
        """
        Get the raw Red, Green, Blue, and overall light Intensity values.

        Returns:
            tuple[int, int, int, int]: `(R, G, B, I)` where:
                - R, G, B: Raw color channel intensities (0–1023)
                - I: Overall light intensity (0–1023), representing the total
                     amount of light detected across all wavelengths.

        Notes:
            - These values are unprocessed and can be used for custom color
              detection or calibration algorithms.
            - Intensity is useful for detecting brightness changes regardless
              of color.
        """
        return color_sensor.rgbi(self.port)


class DistanceSensor(Device):
    """
    High-level control for the LEGO® SPIKE™ Prime.

    This sensor uses ultrasonic pulses to measure the distance to the nearest object.
    It also features two circular "eyes," each divided into two controllable LEDs
    (top and bottom), which can be used for visual feedback.
    """

    def __init__(self, port: int):
        """
        Initialize a Distance Sensor on the specified hub port.

        Args:
            port (int): The hub port where the Distance Sensor is connected.

        Raises:
            RuntimeError: If no Distance Sensor is detected on the given port.
        """
        super().__init__(port)
        try:
            distance_sensor.clear(self.port)
        except OSError:
            raise RuntimeError(
                "A Distance Sensor is not connected to port {port}".format(
                    port=Port.__dict[self.port]
                )
            )

    def clear(self):
        """
        Turn off all four LEDs on the Distance Sensor's "eyes."
        """
        distance_sensor.clear(self.port)

    def distance(self) -> int:
        """
        Measure the distance to the nearest object.

        Returns:
            int: Distance in millimeters (mm).  
                 Returns `2000` if no object is detected within range.

        Notes:
            - Typical measurement range: ~50 mm to 2000 mm.
            - Accuracy can be affected by object size, shape, and surface reflectivity.
            - A return value of `2000` means "out of range."
        """
        dist = distance_sensor.distance(self.port)
        return 2000 if dist == -1 else dist

    def get_pixel(self, x: int, y: int) -> int:
        """
        Get the brightness of a specific LED segment in the sensor's "eyes."

        Args:
            x (int): Eye index:
                - 0 = left eye
                - 1 = right eye
            y (int): LED segment within the eye:
                - 0 = top LED
                - 1 = bottom LED

        Returns:
            int: Brightness level (0–100), where 0 = off and 100 = maximum brightness.
        """
        return distance_sensor.get_pixel(self.port, x, y)

    def set_pixel(self, x: int, y: int, intensity: int):
        """
        Set the brightness of a specific LED segment in the sensor's "eyes."

        Args:
            x (int): Eye index:
                - 0 = left eye
                - 1 = right eye
            y (int): LED segment within the eye:
                - 0 = top LED
                - 1 = bottom LED
            intensity (int): Brightness level (0–100), where 0 = off and 100 = maximum brightness.
        """
        distance_sensor.set_pixel(self.port, x, y, intensity)

    def show(self, pixels: list[int]):
        """
        Set the brightness of all four LEDs at once.

        Args:
            pixels (list[int]): A list of exactly 4 brightness values (0–100),
                                in the order:
                                [left eye top, right eye top,
                                 left eye bottom, right eye bottom]

        Example:
            To turn all LEDs to maximum brightness:
            ```python
            sensor.show([100, 100, 100, 100])
            ```

        Notes:
            - Brightness 0 turns an LED off.
            - This method is more efficient than setting each LED individually.
        """
        distance_sensor.show(self.port, pixels)

class ForceSensor(Device):
    """
    High-level control for the LEGO® SPIKE™ Prime / Powered Up Force Sensor.

    The Force Sensor can measure the amount of force applied to its surface
    and detect simple pressed/released states. It is useful for touch-based
    interactions, measuring push strength, or detecting collisions.
    """

    def __init__(self, port: int):
        """
        Initialize a Force Sensor on the specified hub port.

        Args:
            port (int): The hub port where the Force Sensor is connected.

        Raises:
            RuntimeError: If no Force Sensor is detected on the given port.
        """
        super().__init__(port)
        try:
            force_sensor.pressed(self.port)
        except OSError:
            raise RuntimeError(
                "A Force Sensor is not connected to port {port}".format(
                    port=Port.__dict[self.port]
                )
            )

    def force(self) -> float:
        """
        Measure the amount of force currently applied to the sensor.

        Returns:
            float: Force in Newtons (N), typically in the range 0–10 N.

        Notes:
            - 1 Newton ≈ the force needed to hold up a 100 g weight.
            - The maximum measurable force depends on the sensor's design.
            - Useful for detecting varying pressure levels, not just on/off states.
        """
        return force_sensor.force(self.port)/10

    def pressed(self) -> bool:
        """
        Check whether the sensor is currently pressed.

        Returns:
            bool: True if the sensor is pressed beyond its threshold, False otherwise.

        Notes:
            - This is a simple boolean state, independent of the exact force value.
            - Ideal for detecting button-like interactions.
        """
        return force_sensor.pressed(self.port)

    def raw(self) -> int:
        """
        Get the raw analog reading from the sensor.

        Returns:
            int: Raw sensor value, where higher values indicate more force.

        Notes:
            - This is the unprocessed reading from the sensor hardware.
            - Can be used for custom calibration or non-linear mapping.
        """
        return force_sensor.raw(self.port)
    
    
class DCMotor(Device):
    """
    High-level control for a LEGO® Powered Up DC Motor.

    Unlike angular motors, DC motors do not have built-in rotation sensors
    for speed or position feedback. They are controlled purely by setting
    a duty cycle (PWM power level), making them suitable for continuous
    rotation applications where precise positioning is not required.
    """

    def __init__(self, port, positive_direction: Direction = Direction.CLOCKWISE):
        """
        Initialize a DC Motor on the specified hub port.

        Args:
            port (Port): The hub port where the DC Motor is connected.
            positive_direction (Direction): The direction the motor should turn
                when given a positive duty cycle value.
                Available Direction modes:
                    0 – CLOCKWISE  
                        → Positive values rotate clockwise.
                    1 – COUNTERCLOCKWISE  
                        → Positive values rotate counterclockwise.

        Raises:
            RuntimeError: If the connected device is not recognized as a DC Motor
                          (device ID must be 1).
        """
        super().__init__(port)
        if positive_direction == 1:
            self.positive_direction = -1
        else:
            self.positive_direction = 1

        if super().id() not in (1, 2):
            raise RuntimeError(
                "A motor is not connected to port {port}".format(
                    port=Port.__dict[self.port]
                )
            )

    def run(self, dc: int):
        """
        Run the motor at a given duty cycle (PWM power level).

        Args:
            dc (int): Duty cycle percentage (-100 to 100), where:
                - Positive values follow `positive_direction`.
                - Negative values reverse it.
                - Values between -35 and 35 (excluding 0) are automatically
                  raised to ±35 to overcome motor stall torque.

        Notes:
            - This method directly sets the PWM duty cycle without speed regulation.
            - The built-in minimum threshold ensures the motor starts reliably.
            - For continuous rotation, call `run()` repeatedly or once and let it spin.
        """
        if -35 < dc < 35 and dc != 0:
            dc = 35
        super().set_duty_cycle(100 * dc * self.positive_direction)

    def stop(self):
        """
        Stop the motor by setting its duty cycle to zero.

        Notes:
            - This does not actively brake the motor; it simply removes power.
            - The motor will coast to a stop unless mechanically braked.
        """
        super().set_duty_cycle(0)
        

class Light(Device):
    """
    High-level control for a LEGO® Powered Up Light element.

    This class controls a simple light that supports adjustable brightness
    but no color changes. Brightness is set using a duty cycle (PWM) value.
    """

    def __init__(self, port):
        """
        Initialize a Light on the specified hub port.

        Args:
            port (Port): The hub port where the Light element is connected.
        """
        super().__init__(port)
                
        if super().id() != 8:
            raise RuntimeError(
                "A light is not connected to port {port}".format(
                    port=Port.__dict[self.port]
                )
            )

    def on(self, brightness: int = 100):
        """
        Turn the light on at a specified brightness level.

        Args:
            brightness (int): Brightness percentage (0–100), where:
                - 0 = off
                - 100 = maximum brightness
              Defaults to 100.

        Notes:
            - Internally, this sets the PWM duty cycle to `brightness × 100`
              because the underlying API expects a value in the range 0–10000.
            - Values outside 0–100 may cause unexpected behavior.
        """
        super().set_duty_cycle(100 * brightness)

    def off(self):
        """
        Turn the light off.

        Notes:
            - This sets the PWM duty cycle to 0, cutting power to the light.
            - Equivalent to calling `on(0)`.
        """
        super().set_duty_cycle(0)
        
class ColorDistanceSensor(Device):
    """
    High-level control for the LEGO® Powered Up Color & Distance Sensor (88007).

    ⚠ Firmware note:
        As of SPIKE™ 3 firmware, this sensor can only detect colors.
        Distance, reflection, and ambient light modes are not functional.

    ⚠ LED mode limitation:
        The built-in RGB LED is controlled by changing the sensor's mode:
            - mode=0 → Color sensing mode
            - mode=2 → LED green
            - mode=3 → LED red
            - mode=4 → LED blue
        When the mode is set to 2, 3, or 4, the sensor **cannot** detect colors.
        To resume color sensing, you must switch back to mode 0.
    """

    def __init__(self, port):
        """
        Initialize a Color & Distance Sensor on the specified hub port.

        Args:
            port (Port): The hub port where the sensor is connected.

        Raises:
            RuntimeError: If the connected device is not recognized as a
                          Color & Distance Sensor (device ID must be 37).
        """
        super().__init__(port)

        if super().id() != 37:
            raise RuntimeError(
                "A Color & Distance sensor is not connected to port {port}".format(
                    port=Port.__dict[self.port]
                )
            )

    def color(self) -> int:
        """
        Detect the currently visible color.

        Returns:
            int: Color index (0–10) or `Color` constant:
                0 – NONE  
                1 – BLACK  
                2 – PINK  
                3 – PURPLE  
                4 – BLUE  
                5 – LIGHT_BLUE  
                6 – CYAN  
                7 – GREEN  
                8 – YELLOW  
                9 – ORANGE  
                10 – RED

        Notes:
            - Detection depends on lighting and surface properties.
            - Only works when the sensor is in **mode 0**.
            - If the LED is set via mode 2, 3, or 4, color sensing will not work.
        """
        return super().get()[0]

    def led_green(self):
        """
        Set the sensor's built-in LED to green.

        Notes:
            - Uses `set_mode(mode=2)` internally.
            - While in this mode, color sensing is disabled.
            - Call `set_color_mode()` to return to sensing mode.
        """
        super().set_mode(2)

    def led_red(self):
        """
        Set the sensor's built-in LED to red.

        Notes:
            - Uses `set_mode(mode=3)` internally.
            - While in this mode, color sensing is disabled.
            - Call `set_color_mode()` to return to sensing mode.
        """
        super().set_mode(3)

    def led_blue(self):
        """
        Set the sensor's built-in LED to blue.

        Notes:
            - Uses `set_mode(mode=4)` internally.
            - While in this mode, color sensing is disabled.
            - Call `set_color_mode()` to return to sensing mode.
        """
        super().set_mode(4)

    def set_color_mode(self):
        """
        Switch the sensor back to color sensing mode.

        Notes:
            - Uses `set_mode(mode=0)` internally.
            - Must be called after using `led_green()`, `led_red()`, or `led_blue()`
              if you want to resume color detection.
        """
        super().set_mode(0)

