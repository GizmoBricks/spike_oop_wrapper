import math
from oop.parameters import Stop
from oop.devices import Motor


class DriveBase:
    """
    High-level differential drive control for two-wheeled robots.

    This class wraps two `Motor` instances (left and right) and provides
    movement commands similar to the Pybricks `DriveBase` API.

    It computes distances and turns based on wheel diameter and axle track.

    **Why it is done this way:**
    - Uses your existing synchronous `Motor` class for SPIKE 3.
    - Avoids async/threading for REPL and camp-friendly use.
    - Keeps math simple and transparent for educational purposes.
    """

    def __init__(self,
                 left_motor,
                 right_motor,
                 wheel_diameter: float,
                 axle_track: float,
                 default_stop: Stop = Stop.SMART_BRAKE):
        """
        Initialize the drive base.

        Args:
            left_motor (Motor): Motor instance for the left wheel.
            right_motor (Motor): Motor instance for the right wheel.
            wheel_diameter (float): Diameter of the wheels in millimeters.
            axle_track (float): Distance between the midpoints of the two wheels in millimeters.
            default_stop (Stop): Default stop mode for drive commands.
        """
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.wheel_diameter = wheel_diameter
        self.axle_track = axle_track
        self.default_stop = default_stop

        # Internal state for odometry
        self._reset_odometry()

    # ---------------------------
    # Internal helpers
    # ---------------------------

    def _reset_odometry(self):
        self.left_motor.reset_angle(0)
        self.right_motor.reset_angle(0)

    def _mm_to_degrees(self, mm: float) -> float:
        """Convert linear distance in mm to motor rotation in degrees."""
        circumference = math.pi * self.wheel_diameter
        return (mm / circumference) * 360

    def _degrees_to_mm(self, deg: float) -> float:
        """Convert motor rotation in degrees to linear distance in mm."""
        circumference = math.pi * self.wheel_diameter
        return (deg / 360) * circumference

    # ---------------------------
    # Public API
    # ---------------------------

    def straight(self, distance_mm: float, speed_mm_s: float = 200, wait: bool = True):
        """Drive straight for a given distance."""
        angle_deg = int(self._mm_to_degrees(distance_mm))
        speed_deg_s = int(self._mm_to_degrees(speed_mm_s))
        
        self.left_motor.run_angle(int(round(speed_deg_s)), int(round(angle_deg)), then=self.default_stop, wait=False)
        self.right_motor.run_angle(int(round(speed_deg_s)), int(round(angle_deg)), then=self.default_stop, wait=wait)

    def turn(self, angle_deg: float, speed_deg_s: float = 90, wait: bool = True):
        """Turn the robot in place."""
        turn_circumference = math.pi * self.axle_track
        arc_length_mm = (angle_deg / 360) * turn_circumference
        wheel_rotation_deg = self._mm_to_degrees(arc_length_mm)
        wheel_speed_deg_s = self._mm_to_degrees(
            (speed_deg_s / 360) * turn_circumference
        )
        self.left_motor.run_angle(int(round(wheel_speed_deg_s)), int(round(wheel_rotation_deg)), then=self.default_stop, wait=False)
        self.right_motor.run_angle(int(round(wheel_speed_deg_s)), int(round(-wheel_rotation_deg)), then=self.default_stop, wait=wait)

    def drive(self, speed_mm_s: float, turn_rate_deg_s: float):
        """Drive continuously with a given forward speed and turn rate."""
        turn_circumference = math.pi * self.axle_track
        turn_mm_s = (turn_rate_deg_s / 360) * turn_circumference
        left_speed_mm_s = speed_mm_s - (turn_mm_s / 2)
        right_speed_mm_s = speed_mm_s + (turn_mm_s / 2)
        self.left_motor.run(int(round(self._mm_to_degrees(left_speed_mm_s))))
        self.right_motor.run(int(round(self._mm_to_degrees(right_speed_mm_s))))

    def drive_arc(self, radius_mm: float, angle_deg: float, speed_mm_s: float = 200, wait: bool = True):
        """
        Drive along an arc.

        Args:
            radius_mm (float): Radius of the arc's centerline in mm.
                               Positive = turn right, negative = turn left.
            angle_deg (float): Arc angle in degrees. Positive = forward, negative = backward.
            speed_mm_s (float): Linear speed along the centerline in mm/s.
            wait (bool): If True, block until complete.
        """
        # Arc length along the centerline
        arc_length_mm = (abs(angle_deg) / 360) * (2 * math.pi * abs(radius_mm))

        # Speeds and distances for each wheel
        left_radius = radius_mm - (self.axle_track / 2)
        right_radius = radius_mm + (self.axle_track / 2)

        left_arc_mm = (abs(angle_deg) / 360) * (2 * math.pi * abs(left_radius))
        right_arc_mm = (abs(angle_deg) / 360) * (2 * math.pi * abs(right_radius))

        # Convert to motor degrees
        left_arc_deg = self._mm_to_degrees(left_arc_mm)
        right_arc_deg = self._mm_to_degrees(right_arc_mm)

        # Wheel speeds in deg/s
        left_speed_deg_s = self._mm_to_degrees(speed_mm_s * (left_radius / radius_mm))
        right_speed_deg_s = self._mm_to_degrees(speed_mm_s * (right_radius / radius_mm))

        # Direction handling
        if angle_deg < 0:
            left_arc_deg, right_arc_deg = -left_arc_deg, -right_arc_deg
            left_speed_deg_s, right_speed_deg_s = -left_speed_deg_s, -right_speed_deg_s

        self.left_motor.run_angle(int(round(left_speed_deg_s)), int(round(left_arc_deg)), then=self.default_stop, wait=False)
        self.right_motor.run_angle(int(round(right_speed_deg_s)), int(round(right_arc_deg)), then=self.default_stop, wait=wait)

    def stop(self, then: Stop | None = None):
        """Stop both motors."""
        self.left_motor.stop(then or self.default_stop)
        self.right_motor.stop(then or self.default_stop)

    def distance(self) -> float:
        """Get the average distance traveled since last reset."""
        left_mm = self._degrees_to_mm(self.left_motor.angle())
        right_mm = self._degrees_to_mm(self.right_motor.angle())
        return (left_mm + right_mm) / 2

    def angle(self) -> float:
        """Get the robot's heading change since last reset."""
        left_mm = self._degrees_to_mm(self.left_motor.angle())
        right_mm = self._degrees_to_mm(self.right_motor.angle())
        turn_circumference = math.pi * self.axle_track
        return ((right_mm - left_mm) / turn_circumference) * 360

    def reset(self):
        """Reset odometry (distance and angle)."""
        self._reset_odometry()
        
        
class Car:
    """
    High-level control for a car-like robot with one drive motor and one steering motor.
    """

    def __init__(self,
                 drive_motor,
                 steer_motor,
                 wheel_diameter: float,
                 wheelbase: float,
                 default_stop: Stop = Stop.SMART_BRAKE,
                 max_steering_angle: float = 45,
                 auto_calibrate: bool = True,
                 search_speed: int = 50,
                 stall_time_ms: int = 200):
        """
        Initialize the car.

        Args:
            drive_motor (Motor): Motor instance for driving.
            steer_motor (Motor): Motor instance for steering.
            wheel_diameter (float): Diameter of the drive wheels in mm.
            wheelbase (float): Distance between front and rear axles in mm.
            default_stop (Stop): Default stop mode for drive commands.
            max_steering_angle (float): Maximum steering angle in degrees (left/right).
            auto_calibrate (bool): If True, run steering calibration on init.
            search_speed (int): Speed in deg/s for calibration search.
            stall_time_ms (int): Stall detection time in ms for calibration.
        """
        self.drive_motor = drive_motor
        self.steer_motor = steer_motor
        self.wheel_diameter = wheel_diameter
        self.wheelbase = wheelbase
        self.default_stop = default_stop
        self.max_steering_angle = max_steering_angle

        self._steering_center = 0  # stored center position in deg

        self.reset_odometry()

        if auto_calibrate:
            self.calibrate_steering(search_speed=search_speed, stall_time_ms=stall_time_ms)
        else:
            self.center_steering()

    # ---------------------------
    # Internal helpers
    # ---------------------------

    def _mm_to_degrees(self, mm: float) -> float:
        circumference = math.pi * self.wheel_diameter
        return (mm / circumference) * 360

    def _degrees_to_mm(self, deg: float) -> float:
        circumference = math.pi * self.wheel_diameter
        return (deg / 360) * circumference

    # ---------------------------
    # Steering control
    # ---------------------------

    def calibrate_steering(self, search_speed: int = 50, stall_time_ms: int = 200):
        """
        Automatically calibrate steering by finding mechanical limits.

        Args:
            search_speed (int): Speed in deg/s to move toward each limit.
            stall_time_ms (int): Time in ms that speed must remain near zero to detect stall.
        """
        import time

        def find_limit(speed: int) -> int:
            """Run steering until stall, return position."""
            self.steer_motor.run(speed)
            stalled_since = None
            while True:
                if abs(self.steer_motor.speed()) < 5:  # near zero speed
                    if stalled_since is None:
                        stalled_since = time.ticks_ms()
                    elif time.ticks_diff(time.ticks_ms(), stalled_since) >= stall_time_ms:
                        self.steer_motor.stop(Stop.HOLD)
                        return self.steer_motor.angle()
                else:
                    stalled_since = None

        # Find left limit
        left_limit = find_limit(-abs(search_speed))
        time.sleep_ms(200)  # small pause

        # Find right limit
        right_limit = find_limit(abs(search_speed))
        time.sleep_ms(200)

        # Compute center
        self._steering_center = int(round((left_limit + right_limit) / 2))
        self.center_steering()

    def center_steering(self):
        """Move steering to stored center position."""
        self.steer_motor.run_target(100, self._steering_center, then=Stop.HOLD, wait=True)

    def steer(self, angle: float, speed: int = 100, wait: bool = True):
        """Turn the steering to a given angle relative to center."""
        angle = max(-self.max_steering_angle, min(self.max_steering_angle, angle))
        target_angle = self._steering_center + int(round(angle))
        self.steer_motor.run_target(speed, target_angle, then=Stop.HOLD, wait=wait)

    # ---------------------------
    # Driving control
    # ---------------------------

    def drive_straight(self, distance_mm: float, speed_mm_s: float = 200, wait: bool = True):
        angle_deg = self._mm_to_degrees(distance_mm)
        speed_deg_s = self._mm_to_degrees(speed_mm_s)
        self.drive_motor.run_angle(int(round(speed_deg_s)), int(round(angle_deg)),
                                   then=self.default_stop, wait=wait)

    def drive_arc(self, radius_mm: float, arc_angle_deg: float, speed_mm_s: float = 200, wait: bool = True):
        steering_angle = math.degrees(math.atan(self.wheelbase / abs(radius_mm)))
        if radius_mm < 0:
            steering_angle = -steering_angle

        self.steer(steering_angle, wait=True)

        arc_length_mm = (abs(arc_angle_deg) / 360) * (2 * math.pi * abs(radius_mm))
        drive_angle_deg = self._mm_to_degrees(arc_length_mm)
        drive_speed_deg_s = self._mm_to_degrees(speed_mm_s)

        if arc_angle_deg < 0:
            drive_angle_deg = -drive_angle_deg
            drive_speed_deg_s = -drive_speed_deg_s

        self.drive_motor.run_angle(int(round(drive_speed_deg_s)), int(round(drive_angle_deg)),
                                   then=self.default_stop, wait=wait)

        self.center_steering()

    # ---------------------------
    # Odometry
    # ---------------------------

    def distance(self) -> float:
        return self._degrees_to_mm(self.drive_motor.angle())

    def reset_odometry(self):
        self.drive_motor.reset_angle(0)


if __name__ == "__main__":
    left_motor = Motor(1, 1)
    right_motor = Motor(0)
    db = DriveBase(left_motor, right_motor, 56, 16*8)
    
    db.straight(100)
    db.turn(-90)
