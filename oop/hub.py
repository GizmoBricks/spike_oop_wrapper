from oop.parameters import Buttons, Color, Icon, Orientation
from hub import button, light, light_matrix, motion_sensor, sound
import time


class Button:
    """Simple synchronous SPIKE 3 hub button handler.

    This class wraps the minimal `hub.button` API available in SPIKE 3 firmware
    to provide only the most essential button operations:
      - Check if a button is pressed
      - Get press duration in milliseconds
      - Wait for a press or release
      - Detect long presses

    **Why it is done this way:**
    SPIKE 3 MicroPython does not support `_thread` and has limited async
    capabilities. This class is designed for use in a fully synchronous
    program, where button checks are performed in the main loop. It avoids
    background tasks entirely, ensuring compatibility and simplicity for
    educational and camp environments.

    ⚠️ **Important note on button behavior:**
    The Center (Power) and Bluetooth (Connect) buttons only respond correctly
    if the hub's graphical user interface (UI) is not running. This typically
    means using the hub in REPL mode—for example, when connected via Thonny IDE.
    If the UI is active (e.g. after running a program from the SPIKE app), these
    buttons may be intercepted by the OS and not register properly.
    """

    def __init__(self, btn_id: Buttons|int, long_press_ms: int = 1000):
        """Initialize a Button instance.

        Args:
            btn_id (int): One of the constants from `Buttons` in
                `oop.parameters`. The mapping is:

                    Buttons.LEFT   = 0  → Left button  
                    Buttons.CENTER = 1  → Center/Power button  
                    Buttons.RIGHT  = 2  → Right button  
                    Buttons.BT     = 3  → Bluetooth/Connect button
                    
            long_press_ms (int, optional): Duration threshold in milliseconds
                to consider a press as a long press. Defaults to 1000.

        ⚠️ **UI limitation:**
        The Center and BT buttons will only function reliably if the hub's UI
        is not active. For consistent behavior, use this class in REPL mode,
        such as when running code via Thonny IDE.
        """
        self.btn_id = btn_id
        self.long_press_ms = long_press_ms

    def is_pressed(self) -> bool:
        """Check if the button is currently pressed.

        Returns:
            bool: True if the button is pressed, False otherwise.
        """
        return button.pressed(self.btn_id) > 0

    def press_duration(self) -> int:
        """Get the current press duration.

        Returns:
            int: Number of milliseconds the button has been held down.
                 Returns 0 if not pressed.
        """
        return button.pressed(self.btn_id)

    def wait_for_press(self):
        """Block execution until the button is pressed."""
        while not self.is_pressed():
            pass

    def wait_for_release(self):
        """Block execution until the button is released."""
        while self.is_pressed():
            pass

    def is_long_press(self) -> bool:
        """Check if the button is currently held long enough to be a long press.

        Returns:
            bool: True if held for at least `long_press_ms`, False otherwise.
        """
        return self.press_duration() >= self.long_press_ms
    
    
class Light:
    """Simple synchronous SPIKE 3 hub light controller.

    This class wraps the minimal `hub.light` API available in SPIKE 3 firmware
    to provide a clean, object‑oriented interface for controlling the hub lights.
    """

    # Light ID constants (matching hub.light)
    POWER = 0    # The light around the center/power button
    CONNECT = 1  # The light around the Bluetooth connect button

    def __init__(self, light_id: int):
        """Initialize a HubLight instance.

        Args:
            light_id (int): One of the constants from this class:
                POWER   = 0 → Center/Power button light  
                CONNECT = 1 → Bluetooth/Connect button light
        """
        self.light_id = light_id

    def set_color(self, color_id: int):
        """Set the light to a given color.

        Args:
            color_id (int): A color constant from the `Color` module,
                e.g., `Color.RED`, `Color.GREEN`, `Color.BLUE`.
        """
        light.color(self.light_id, color_id)

    def off(self):
        """Turn the light off."""
        light.color(self.light_id, Color.BLACK)
        
        
class Sound:
    """Simple synchronous SPIKE 3 hub sound controller with note playback.

    Features:
      - Beep playback with instance defaults
      - Stop and volume control
      - Pybricks-style note sequence playback with rests
      - Shorthand note support:
          "C"   -> "C<default_octave>/1"
          "C4"  -> "C4/1"
          "R"   -> "R/1"
      - Dotted notes: "C4/4." = 1.5 × quarter note
      - Triplets: "C4/8t" = 2/3 × eighth note
      - Named tune library (includes Mario theme intro)
    """

    # Sound channel constants
    ANY = -2
    DEFAULT = -1

    # Waveform constants
    WAVEFORM_SINE = 0
    WAVEFORM_SAWTOOTH = 3
    WAVEFORM_SQUARE = 2
    WAVEFORM_TRIANGLE = 1

    # Base frequencies for notes in the 4th octave (C4 = middle C)
    _NOTE_FREQS = {
        "C": 261.63,
        "C#": 277.18, "Db": 277.18,
        "D": 293.66,
        "D#": 311.13, "Eb": 311.13,
        "E": 329.63,
        "F": 349.23,
        "F#": 369.99, "Gb": 369.99,
        "G": 392.00,
        "G#": 415.30, "Ab": 415.30,
        "A": 440.00,
        "A#": 466.16, "Bb": 466.16,
        "B": 493.88
    }

    # Named tune library
    TUNES = {
        "scale_c_major": ["C4/4", "D4/4", "E4/4", "F4/4", "G4/4", "A4/4", "B4/4", "C5/2"],
        # Super Mario Bros. main theme (intro excerpt), simplified
        # Tempo hint: ~200
        "mario_theme_intro": [
            "E5/8","E5/8","R/8","E5/8","R/8","C5/8","E5/8","G5/8","R/8","G4/8",
            "R/8","C5/8","R/8","G4/8","R/8","E4/8","R/8","A4/8","B4/8","Bb4/8","A4/8",
            "G4/8","E5/8","G5/8","A5/8","F5/8","G5/8","R/8","E5/8","C5/8","D5/8","B4/8"
        ],
        "twinkle_start": ["C4/4", "C4/4", "G4/4", "G4/4", "A4/4", "A4/4", "G4/2"],
        "happy_birthday": ["C4/4", "C4/8", "D4/4", "C4/4", "F4/4", "E4/2",
                           "C4/4", "C4/8", "D4/4", "C4/4", "G4/4", "F4/2",
                           "C4/4", "C4/8", "C5/4", "A4/4", "F4/4", "E4/4", "D4/4",
                           "Bb4/4", "Bb4/8", "A4/4", "F4/4", "G4/4", "F4/2"],
        "star_wars_main": ["C4/2", "G4/2", "F4/8", "E4/8", "D4/8", "C5/2", "G4/4",
                           "F4/8", "E4/8", "D4/8", "C5/2", "G4/4", "F4/8", "E4/8",
                           "F4/8", "D4/2"]
    }

    def __init__(self,
                 duration: int = 500,
                 volume: int = 100,
                 attack: int = 0,
                 decay: int = 0,
                 sustain: int = 100,
                 release: int = 0,
                 transition: int = 10,
                 waveform: int = WAVEFORM_SINE,
                 channel: int = DEFAULT,
                 default_octave: int = 4):
        self.default_duration = duration
        self.default_volume = volume
        self.default_attack = attack
        self.default_decay = decay
        self.default_sustain = sustain
        self.default_release = release
        self.default_transition = transition
        self.default_waveform = waveform
        self.channel = channel
        self.default_octave = default_octave

    def beep(self, freq: int|float,
             duration: int = None,
             volume: int = None,
             attack: int = None,
             decay: int = None,
             sustain: int = None,
             release: int = None,
             transition: int = None,
             waveform: int = None):
        sound.beep(
            freq=int(freq),
            duration=duration if duration is not None else self.default_duration,
            volume=volume if volume is not None else self.default_volume,
            attack=attack if attack is not None else self.default_attack,
            decay=decay if decay is not None else self.default_decay,
            sustain=sustain if sustain is not None else self.default_sustain,
            release=release if release is not None else self.default_release,
            transition=transition if transition is not None else self.default_transition,
            waveform=waveform if waveform is not None else self.default_waveform,
            channel=self.channel
        )

    def stop(self):
        sound.stop()

    def set_volume(self, volume_level: int):
        sound.volume(volume_level)

    def play_notes(self, notes, tempo=120):
        beat_duration_ms = 60000 / tempo  # quarter note duration in ms

        for note_str in notes:
            # Expand shorthand if missing "/"
            if "/" not in note_str:
                if note_str.upper() == "R":
                    note_str = "R/1"
                elif note_str[-1].isdigit():
                    note_str = f"{note_str}/1"  # explicit octave, default to whole note
                else:
                    note_str = f"{note_str}{self.default_octave}/1"  # no octave, use default

            # Handle dotted and triplet markers: ".t", ".", "t"
            dotted = note_str.endswith(".") or ".t" in note_str
            triplet = note_str.endswith("t") or note_str.endswith(".t")
            clean_str = note_str.replace(".t", "").rstrip(".t")
            if clean_str.endswith("."):
                clean_str = clean_str[:-1]

            try:
                pitch, length = clean_str.split("/")
            except ValueError:
                raise ValueError(f"Invalid note format: {note_str}")

            note_fraction = int(length)
            duration_ms = int((4 / note_fraction) * beat_duration_ms)
            if dotted:
                duration_ms = int(duration_ms * 1.5)
            if triplet:
                duration_ms = int(duration_ms * (2 / 3))

            if pitch.upper() == "R":
                time.sleep(duration_ms / 1000)
                continue

            name = pitch[:-1]
            octave = int(pitch[-1])

            if name not in self._NOTE_FREQS:
                raise ValueError(f"Unknown note name: {name}")

            base_freq = self._NOTE_FREQS[name]
            freq = base_freq * (2 ** (octave - 4))

            self.beep(freq=freq, duration=duration_ms)
            time.sleep(duration_ms / 1000)

    # ----- Tune library helpers -----
    def play_tune(self, name: str, tempo=120):
        """Play a tune from the built-in library."""
        if name not in self.TUNES:
            raise ValueError(f"Tune '{name}' not found in library.")
        self.play_notes(self.TUNES[name], tempo=tempo)

    def add_tune(self, name: str, notes: list):
        """Add or overwrite a tune in the library."""
        self.TUNES[name] = notes
        

class LightMatrix:
    """Synchronous SPIKE 3 Light Matrix wrapper.

    This class provides an object-oriented interface to the built-in
    `hub.light_matrix` module, allowing you to control the 5×5 LED display
    on the SPIKE 3 hub without using any asynchronous code.

    **Why it is done this way:**
    SPIKE 3 MicroPython has no `_thread` support and limited async features.
    This wrapper is designed for simple, synchronous use in REPL mode or
    in programs where you explicitly control the main loop.

    **Firmware/UI note:**
    The Light Matrix works in both REPL and normal program modes, but
    certain button interactions (Center, BT) may not behave as expected
    if the hub's UI is active. For consistent low-level control, run in
    REPL mode (e.g., via Thonny IDE).
    """
    
    # Orientation constants (matching hub.light_matrix orientation values)
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3
    

    def __init__(
        self,
        orientation: int = UP,
        clear: bool = True,
        show_icon=None
    ):
        """Initialize the Light Matrix.

        Args:
            orientation (int, optional): One of the class constants
                `UP`, `RIGHT`, `DOWN`, or `LEFT` to set which side is the top
                of the display. Defaults to `LightMatrix.UP`.
            clear (bool, optional): If True, clears the display on init.
                Defaults to True.
            show_icon (optional): Passed directly to `show_image()` if provided.
        """
        self.set_orientation(orientation)
        if clear:
            self.clear()
        if show_icon is not None:
            self.show_image(show_icon)

    def clear(self) -> None:
        """Turn off all pixels on the Light Matrix."""
        light_matrix.clear()

    def get_orientation(self) -> int:
        """Get the current Light Matrix orientation.

        Returns:
            int: One of the constants from `Orientation`.
        """
        return light_matrix.get_orientation()

    def set_orientation(self, top: int) -> int:
        """Set the Light Matrix orientation.

        Args:
            top (int): One of the constants from `Orientation`.

        Returns:
            int: The new orientation value.
        """
        return light_matrix.set_orientation(top)

    def get_pixel(self, x: int, y: int) -> int:
        """Get the brightness of a specific pixel.

        Args:
            x (int): Column index (0–4).
            y (int): Row index (0–4).

        Returns:
            int: Brightness (0–100).
        """
        return light_matrix.get_pixel(x, y)

    def set_pixel(self, x: int, y: int, intensity: int) -> None:
        """Set the brightness of a specific pixel.

        Args:
            x (int): Column index (0–4).
            y (int): Row index (0–4).
            intensity (int): Brightness (0–100).
        """
        light_matrix.set_pixel(x, y, intensity)

    def show(self, pixels: list[int]) -> None:
        """Update all pixels at once.

        Args:
            pixels (list[int]): List of 25 brightness values (0–100).
        """
        light_matrix.show(pixels)

    def show_image(self, image) -> None:
        """Display one built-in image.

        Args:
            image (int | str): Either an `Icon` constant or a string name
                (case-insensitive) from `Icon`.
        """
        if isinstance(image, str):
            icon_value = getattr(Icon, image.upper(), None)
            if icon_value is None:
                raise ValueError(f"Unknown icon name: {image}")
            image = icon_value
        light_matrix.show_image(image)

    def animate(self, images, delay_ms: int = 500, clear_between: bool = False) -> None:
        """Display multiple images in sequence.

        Args:
            images (list | tuple): Sequence of `Icon` constants or string names.
            delay_ms (int, optional): Delay between frames in milliseconds.
                Defaults to 500.
            clear_between (bool, optional): If True, clears the display between
                frames. Defaults to False.
        """
        for img in images:
            self.show_image(img)
            time.sleep_ms(delay_ms)
            if clear_between:
                self.clear()

    def write(self, text: str, intensity: int = 100, time_per_character: int = 500) -> None:
        """Scroll text across the Light Matrix.

        Args:
            text (str): The text to display.
            intensity (int, optional): Brightness (0–100). Defaults to 100.
            time_per_character (int, optional): Duration per character in ms. Defaults to 500.
        """
        light_matrix.write(text, intensity, time_per_character)
        
        
class MotionSensor:
    """Synchronous SPIKE 3 Motion Sensor wrapper.

    This class provides an object-oriented interface to the built-in
    `hub.motion_sensor` module, allowing you to read acceleration,
    angular velocity, gestures, tilt, and orientation without using
    asynchronous code.

    **Why it is done this way:**
    SPIKE 3 MicroPython has no `_thread` support and limited async features.
    This wrapper is designed for simple, synchronous use in REPL mode or
    in programs where you explicitly control the main loop.
    """

    # Gesture constants (matching hub.motion_sensor values)
    TAPPED = 0
    DOUBLE_TAPPED = 1
    SHAKEN = 2
    FALLING = 3
    UNKNOWN = -1

    # Human-readable gesture names
    GESTURE_NAMES = {
        TAPPED: "TAPPED",
        DOUBLE_TAPPED: "DOUBLE_TAPPED",
        SHAKEN: "SHAKEN",
        FALLING: "FALLING",
        UNKNOWN: "UNKNOWN"
    }

    # Human-readable orientation names (reverse lookup from Orientation constants)
    ORIENTATION_NAMES = {value: name for name, value in Orientation.__dict__.items()
                         if not name.startswith("__") and isinstance(value, int)}

    def __init__(
        self,
        set_yaw_face: int = Orientation.TOP,
        reset_yaw: bool = False,
        reset_tap_count: bool = True
    ):
        """Initialize the Motion Sensor.

        Args:
            set_yaw_face (int, optional): One of the constants from `Orientation`
                to define which hub face is used as the yaw reference.
                Defaults to `Orientation.TOP`.
            reset_yaw (bool, optional): If True, resets yaw to 0° on init.
                Defaults to False.
            reset_tap_count (bool, optional): If True, resets tap count on init.
                Defaults to True.
        """
        self.set_yaw_face(set_yaw_face)
        if reset_yaw:
            self.reset_yaw(0)
        if reset_tap_count:
            self.reset_tap_count()

    def acceleration(self, raw_unfiltered: bool = False) -> tuple[int, int, int]:
        """Get acceleration in milli-G (1/1000 G) for x, y, z axes."""
        return motion_sensor.acceleration(raw_unfiltered)

    def angular_velocity(self, raw_unfiltered: bool = False) -> tuple[int, int, int]:
        """Get angular velocity in decidegrees/sec for x, y, z axes."""
        return motion_sensor.angular_velocity(raw_unfiltered)

    def gesture(self, as_name: bool = False):
        """Get the last detected gesture.

        Args:
            as_name (bool, optional): If True, return the gesture name as a string
                instead of the numeric constant. Defaults to False.

        Returns:
            int | str: Gesture constant or name.
        """
        g = motion_sensor.gesture()
        return self.GESTURE_NAMES.get(g, "UNKNOWN") if as_name else g

    def wait_for_gesture(self, target_gesture=None, as_name: bool = False):
        """Block until a gesture is detected.

        Args:
            target_gesture (int | str | None, optional):
                - If None, waits for any gesture except UNKNOWN.
                - If int, waits for that gesture constant.
                - If str, waits for gesture with that name (case-insensitive).
            as_name (bool, optional): If True, return gesture name instead of constant.

        Returns:
            int | str: The detected gesture (constant or name).
        """
        if isinstance(target_gesture, str):
            # Convert string name to constant
            target_gesture = {v: k for k, v in self.GESTURE_NAMES.items()}.get(
                target_gesture.upper(), None
            )
            if target_gesture is None:
                raise ValueError(f"Unknown gesture name: {target_gesture}")

        while True:
            g = motion_sensor.gesture()
            if g != self.UNKNOWN:
                if target_gesture is None or g == target_gesture:
                    return self.GESTURE_NAMES.get(g, "UNKNOWN") if as_name else g

    def get_yaw_face(self, as_name: bool = False):
        """Get the current yaw reference face.

        Args:
            as_name (bool, optional): If True, return the orientation name
                instead of the numeric constant.

        Returns:
            int | str: Orientation constant or name.
        """
        face = motion_sensor.get_yaw_face()
        return self.ORIENTATION_NAMES.get(face, "UNKNOWN") if as_name else face

    def quaternion(self) -> tuple[float, float, float, float]:
        """Get the orientation quaternion (w, x, y, z)."""
        return motion_sensor.quaternion()

    def reset_tap_count(self) -> None:
        """Reset the tap count."""
        motion_sensor.reset_tap_count()

    def reset_yaw(self, angle: int = 0) -> None:
        """Set the yaw offset to a specific angle."""
        motion_sensor.reset_yaw(angle)

    def set_yaw_face(self, up: int) -> bool:
        """Set which face is used as the yaw reference."""
        return motion_sensor.set_yaw_face(up)

    def stable(self) -> bool:
        """Check if the hub is resting flat."""
        return motion_sensor.stable()

    def tap_count(self) -> int:
        """Get the number of taps since last reset."""
        return motion_sensor.tap_count()

    def tilt_angles(self) -> tuple[int, int, int]:
        """Get yaw, pitch, roll in decidegrees."""
        return motion_sensor.tilt_angles()

    def up_face(self, as_name: bool = False):
        """Get which face is currently facing up.

        Args:
            as_name (bool, optional): If True, return the orientation name
                instead of the numeric constant.

        Returns:
            int | str: Orientation constant or name.
        """
        face = motion_sensor.up_face()
        return self.ORIENTATION_NAMES.get(face, "UNKNOWN") if as_name else face
        
    
if __name__ == "__main__":
    power_light = Light(Light.POWER)
    bt_light = Light(Light.CONNECT)
    
    left_btn = Button(Buttons.LEFT, long_press_ms=1500)
    
    power_light.set_color(Color.RED)
    bt_light.set_color(Color.GREEN)

    print("Press the LEFT button...")
    left_btn.wait_for_press()
    print("Button pressed!")

    left_btn.wait_for_release()
    print("Button released!")
    
    power_light.off()
    bt_light.off()
        

