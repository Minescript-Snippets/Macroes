import minescript as ms
import time
import random
import math
import sys

# ===== CROP PRESETS =====
# Each preset tunes the farming behavior for that crop type.
# You can add your own entries here or create them via the --custom flag.
CROP_PRESETS = {
    "wheat": {
        "name": "Wheat",
        "forward_blocks": 0,
        "target_yaw": 180,
        "target_pitch": 7,
        "enable_sprint": True,
        "auto_break": True,
        "pause_between_rows": (0.1, 0.3),
        "pause_during_movement": (0.05, 0.15),
        "diagonal_mode": False,
        "notes": "Strafe mode for wheat.",
    },
    "potato": {
        "name": "Potato",
        "forward_blocks": 3,
        "target_yaw": 180,
        "target_pitch": 7,
        "enable_sprint": True,
        "auto_break": True,
        "pause_between_rows": (0.1, 0.3),
        "pause_during_movement": (0.05, 0.15),
        "diagonal_mode": False,
        "notes": "Strafe mode for potato.",
    },
    "carrot": {
        "name": "Carrot",
        "forward_blocks": 0,
        "target_yaw": 180,
        "target_pitch": 7,
        "enable_sprint": True,
        "auto_break": True,
        "pause_between_rows": (0.1, 0.3),
        "pause_during_movement": (0.05, 0.15),
        "diagonal_mode": False,
        "notes": "Strafe mode for carrot",
    },
    "sugarcane": {
        "name": "Sugarcane",
        "forward_blocks": 3,
        "target_yaw": 55,
        "target_pitch": 0,  # Look straight ahead — cane is tall
        "enable_sprint": True,
        "auto_break": True,
        "pause_between_rows": (0.15, 0.4),
        "pause_during_movement": (0.05, 0.1),
        "diagonal_mode": True,
        "notes": "Diagonal mode for sugarcane.",
    },
    "pumpkin": {
        "name": "Pumpkin",
        "forward_blocks": 2,
        "target_yaw": 180,
        "target_pitch": 30,
        "enable_sprint": False,
        "auto_break": True,
        "pause_between_rows": (0.2, 0.5),
        "pause_during_movement": (0.1, 0.2),
        "diagonal_mode": True,
        "notes": "Does not work atm, maybe if you configure a huge amount of settings",
    },
    "melon": {
        "name": "Melon",
        "forward_blocks": 2,
        "target_yaw": 180,
        "target_pitch": 30,
        "enable_sprint": False,
        "auto_break": True,
        "pause_between_rows": (0.2, 0.5),
        "pause_during_movement": (0.1, 0.2),
        "diagonal_mode": True,
        "notes": "Does not work atm, maybe if you configure a huge amount of settings",
    },
    "mushroom": {
        "name": "Mushroom",
        "forward_blocks": 0,
        "target_yaw": 180,
        "target_pitch": 20,
        "enable_sprint": False,
        "auto_break": True,
        "pause_between_rows": (0.3, 0.6),
        "pause_during_movement": (0.1, 0.25),
        "diagonal_mode": False,
        "notes": "Strafe mode for mushrooms.",
    },
    "netherwart": {
        "name": "Netherwart",
        "forward_blocks": 0,
        "target_yaw": 180,
        "target_pitch": 15,
        "enable_sprint": True,
        "auto_break": True,
        "pause_between_rows": (0.1, 0.35),
        "pause_during_movement": (0.05, 0.15),
        "diagonal_mode": False,
        "notes": "Strafe sweep for netherwart.",
    },
    "cocoa": {
        "name": "Cocoa",
        "forward_blocks": 0,
        "target_yaw": 90,
        "target_pitch": -90,
        "enable_sprint": False,
        "auto_break": True,
        "pause_between_rows": (0.25, 0.5),
        "pause_during_movement": (0.1, 0.2),
        "diagonal_mode": False,
        "notes": "Looks straight up, and uses strafe at a 90 degree angle for cocoa.",
    },
    "wildrose": {
        "name": "Wild Rose",
        "forward_blocks": 3,
        "target_yaw": 55,
        "target_pitch": 0,
        "enable_sprint": True,
        "auto_break": True,
        "pause_between_rows": (0.1, 0.3),
        "pause_during_movement": (0.05, 0.15),
        "diagonal_mode": True,
        "notes": "Diagonal sweep for wild rose.",
    },
    "moonflower": {
        "name": "Moonflower",
        "forward_blocks": 3,
        "target_yaw": 55,
        "target_pitch": 0,
        "enable_sprint": True,
        "auto_break": True,
        "pause_between_rows": (0.1, 0.3),
        "pause_during_movement": (0.05, 0.15),
        "diagonal_mode": True,
        "notes": "Diagonal sweep for moonflower.",
    },
    "sunflower": {
        "name": "Sunflower",
        "forward_blocks": 3,
        "target_yaw": 55,
        "target_pitch": 0,
        "enable_sprint": True,
        "auto_break": True,
        "pause_between_rows": (0.1, 0.3),
        "pause_during_movement": (0.05, 0.15),
        "diagonal_mode": True,
        "notes": "Diagonal sweep for sunflower.",
    },
}

# ===== BASE CONFIGURATION =====
CONFIG = {
    # Coordinate trigger settings
    "trigger_coordinates": (238, 73, -101),
    "trigger_radius": 1,
    "trigger_command": "/warp garden",
    "enable_trigger": True,

    # Movement settings (overridden by crop preset)
    "forward_blocks": 3,
    "initial_direction": "right",

    # View direction settings
    "target_yaw": 180,
    "target_pitch": 7,
    "smooth_look_duration": 0.3,
    "smooth_look_steps": 60,

    # Breaking settings
    "auto_break": True,

    # Randomization settings
    "position_variance": 0.15,
    "pause_between_rows": (0.1, 0.3),
    "pause_during_movement": (0.05, 0.15),

    # Detection settings
    "check_interval": 0.05,
    "stuck_threshold": 0.02,
    "stuck_checks": 5,
    "stuck_time_threshold": 0.5,

    # Anti-macro detection
    "yaw_pitch_tolerance": 5.0,
    "block_placement_timeout": 2.0,
    "teleport_distance": 10000.0,

    # Safety
    "max_iterations": 1000,
    "enable_sprint": True,

    # Diagonal mode for spiral farms.
    "diagonal_mode": False,
}


def apply_crop_preset(preset_key):
    """Apply a crop preset's values on top of CONFIG."""
    preset = CROP_PRESETS[preset_key]
    CONFIG["forward_blocks"]         = preset["forward_blocks"]
    CONFIG["target_yaw"]             = preset["target_yaw"]
    CONFIG["target_pitch"]           = preset["target_pitch"]
    CONFIG["enable_sprint"]          = preset["enable_sprint"]
    CONFIG["auto_break"]             = preset["auto_break"]
    CONFIG["pause_between_rows"]     = preset["pause_between_rows"]
    CONFIG["pause_during_movement"]  = preset["pause_during_movement"]
    CONFIG["diagonal_mode"]          = preset["diagonal_mode"]


# ===== INTERACTIVE CROP SELECTOR =====
CROP_MENU = [
    ("wheat",      " 1. Wheat"),
    ("potato",     " 2. Potato"),
    ("carrot",     " 3. Carrot"),
    ("sugarcane",  " 4. Sugarcane"),
    ("pumpkin",    " 5. Pumpkin"),
    ("melon",      " 6. Melon"),
    ("mushroom",   " 7. Mushroom"),
    ("netherwart", " 8. Netherwart"),
    ("cocoa",      " 9. Cocoa"),
    ("wildrose",   "10. Wild Rose"),
    ("moonflower", "11. Moonflower"),
    ("sunflower",  "12. Sunflower"),
    ("custom",     "13. Custom (enter your own settings)"),
]

def print_crop_menu_ingame():
    """Print the crop selection menu to Minecraft chat via ms.echo."""
    ms.echo("[AutoFarm] ========= SELECT YOUR CROP =========")
    for key, label in CROP_MENU:
        if key == "custom":
            ms.echo(f"[AutoFarm] {label}")
        else:
            preset = CROP_PRESETS[key]
            mode = "diagonal" if preset["diagonal_mode"] else "standard"
            ms.echo(f"[AutoFarm] {label}  ({mode})")
    ms.echo("[AutoFarm] =====================================")
    ms.echo("[AutoFarm] Run again with e.g.  --1  for Wheat,  --7  for Mushroom,  --13  for Custom")


def collect_custom_config():
    """Interactively collect values for a custom crop configuration."""
    print("\n--- Custom Crop Configuration ---")
    print("Press Enter to keep the default value shown in [brackets].\n")

    def ask_float(prompt, default):
        raw = input(f"{prompt} [{default}]: ").strip()
        return float(raw) if raw else default

    def ask_int(prompt, default):
        raw = input(f"{prompt} [{default}]: ").strip()
        return int(raw) if raw else default

    def ask_bool(prompt, default):
        default_str = "y" if default else "n"
        raw = input(f"{prompt} [{'y' if default else 'n'}]: ").strip().lower()
        if raw in ("y", "yes", "1", "true"):
            return True
        if raw in ("n", "no", "0", "false"):
            return False
        return default

    CONFIG["forward_blocks"]        = ask_float("Forward blocks per row step", CONFIG["forward_blocks"])
    CONFIG["target_yaw"]            = ask_float("Target yaw (0-360)", CONFIG["target_yaw"])
    CONFIG["target_pitch"]          = ask_float("Target pitch (-90 to 90)", CONFIG["target_pitch"])
    CONFIG["enable_sprint"]         = ask_bool("Enable sprinting? (y/n)", CONFIG["enable_sprint"])
    CONFIG["auto_break"]            = ask_bool("Auto-break blocks? (y/n)", CONFIG["auto_break"])
    CONFIG["diagonal_mode"]         = ask_bool("Enable diagonal spiral mode? (y/n)", CONFIG["diagonal_mode"])

    min_row = ask_float("Min pause between rows (sec)", CONFIG["pause_between_rows"][0])
    max_row = ask_float("Max pause between rows (sec)", CONFIG["pause_between_rows"][1])
    CONFIG["pause_between_rows"] = (min(min_row, max_row), max(min_row, max_row))

    min_mv = ask_float("Min pause during movement (sec)", CONFIG["pause_during_movement"][0])
    max_mv = ask_float("Max pause during movement (sec)", CONFIG["pause_during_movement"][1])
    CONFIG["pause_during_movement"] = (min(min_mv, max_mv), max(min_mv, max_mv))

    CONFIG["max_iterations"] = ask_int("Max iterations", CONFIG["max_iterations"])

    print("\nCustom config applied!")


# ===== FARM AUTOMATION CLASS =====

class FarmAutomation:
    def __init__(self):
        self.running = False
        self.current_direction = CONFIG["initial_direction"]
        self.iterations = 0
        self.last_positions = []
        self.expected_yaw = CONFIG["target_yaw"]
        self.expected_pitch = CONFIG["target_pitch"]
        self.last_known_position = None
        self.stuck_timer = 0
        self.trigger_activated = False
        self.trigger_cooldown = 0
        self.movement_start_time = 0

    def log(self, message):
        ms.echo(f"[AutoFarm] {message}")

    def alert_and_stop(self, reason):
        self.log(f"!!! ALERT: {reason} !!!")
        self.log("Script stopped for safety!")
        self.running = False

    def get_position(self):
        player = ms.player()
        return player.position

    def distance_to_coordinates(self, pos, target_coords):
        return math.sqrt(
            (pos[0] - target_coords[0]) ** 2 +
            (pos[1] - target_coords[1]) ** 2 +
            (pos[2] - target_coords[2]) ** 2
        )

    def check_trigger_coordinates(self):
        if not CONFIG["enable_trigger"]:
            return
        current_time = time.time()
        if current_time - self.trigger_cooldown < 3.0:
            return
        current_pos = self.get_position()
        distance = self.distance_to_coordinates(current_pos, CONFIG["trigger_coordinates"])
        if distance <= CONFIG["trigger_radius"]:
            self.log(f"Hit trigger coordinates! Executing: {CONFIG['trigger_command']}")
            ms.execute(CONFIG["trigger_command"])
            self.trigger_cooldown = current_time
            time.sleep(1.0)

    def get_rotation(self):
        player = ms.player()
        return (player.yaw, player.pitch)

    def normalize_angle(self, angle):
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        return angle

    def angle_difference(self, angle1, angle2):
        diff = self.normalize_angle(angle2 - angle1)
        if diff > 180:
            diff -= 360
        return abs(diff)

    def smooth_look_to(self, target_yaw, target_pitch):
        target_yaw = self.normalize_angle(target_yaw)
        current_yaw, current_pitch = self.get_rotation()
        current_yaw = self.normalize_angle(current_yaw)

        yaw_diff = self.normalize_angle(target_yaw - current_yaw)
        if yaw_diff > 180:
            yaw_diff -= 360
        pitch_diff = target_pitch - current_pitch

        num_steps = CONFIG["smooth_look_steps"]
        total_duration = CONFIG["smooth_look_duration"]
        step_delay = total_duration / num_steps
        yaw_step = yaw_diff / num_steps
        pitch_step = pitch_diff / num_steps

        for step in range(num_steps):
            if not self.running:
                break
            new_yaw = self.normalize_angle(current_yaw + yaw_step * (step + 1))
            new_pitch = current_pitch + pitch_step * (step + 1)
            ms.player_set_orientation(new_yaw, new_pitch)
            time.sleep(step_delay)

        ms.player_set_orientation(target_yaw, target_pitch)
        self.expected_yaw = target_yaw
        self.expected_pitch = target_pitch

    def check_rotation_tampering(self):
        current_yaw, current_pitch = self.get_rotation()
        current_yaw = self.normalize_angle(current_yaw)
        yaw_diff = self.angle_difference(current_yaw, self.expected_yaw)
        pitch_diff = abs(current_pitch - self.expected_pitch)
        if yaw_diff > CONFIG["yaw_pitch_tolerance"] or pitch_diff > CONFIG["yaw_pitch_tolerance"]:
            self.alert_and_stop(
                f"Rotation changed! Yaw diff: {yaw_diff:.1f}°, Pitch diff: {pitch_diff:.1f}°"
            )
            return False
        return True

    def check_teleport(self, current_pos):
        if self.last_known_position is None:
            self.last_known_position = current_pos
            return True
        current_time = time.time()
        if current_time - self.trigger_cooldown < 3.0:
            self.last_known_position = current_pos
            return True
        distance = math.sqrt(
            (current_pos[0] - self.last_known_position[0]) ** 2 +
            (current_pos[1] - self.last_known_position[1]) ** 2 +
            (current_pos[2] - self.last_known_position[2]) ** 2
        )
        if distance > CONFIG["teleport_distance"]:
            self.alert_and_stop(f"Teleport detected! Distance: {distance:.1f} blocks")
            return False
        self.last_known_position = current_pos
        return True

    def add_human_variance(self, base_value):
        variance = random.uniform(-CONFIG["position_variance"], CONFIG["position_variance"])
        return base_value + variance

    def random_pause(self, pause_type="between_rows"):
        if pause_type == "between_rows":
            min_pause, max_pause = CONFIG["pause_between_rows"]
        else:
            min_pause, max_pause = CONFIG["pause_during_movement"]
        time.sleep(random.uniform(min_pause, max_pause))

    def is_stuck(self):
        if len(self.last_positions) < CONFIG["stuck_checks"]:
            return False
        if self.movement_start_time > 0:
            elapsed = time.time() - self.movement_start_time
            if elapsed < CONFIG["stuck_time_threshold"]:
                return False
        recent_positions = self.last_positions[-CONFIG["stuck_checks"]:]
        total_distance = 0
        for i in range(1, len(recent_positions)):
            x_diff = abs(recent_positions[i][0] - recent_positions[i - 1][0])
            z_diff = abs(recent_positions[i][2] - recent_positions[i - 1][2])
            total_distance += math.sqrt(x_diff ** 2 + z_diff ** 2)
        avg_distance_per_check = total_distance / (len(recent_positions) - 1)
        return avg_distance_per_check < CONFIG["stuck_threshold"]

    # ------------------------------------------------------------------
    # Standard left/right movement (original mode)
    # ------------------------------------------------------------------

    def move_direction(self, direction):
        """Move in a cardinal direction until stuck."""
        if direction == "right":
            ms.player_press_right(True)
        elif direction == "left":
            ms.player_press_left(True)
        elif direction == "forward":
            ms.player_press_forward(True)
        elif direction == "backward":
            ms.player_press_backward(True)

        if CONFIG["enable_sprint"] and direction in ["forward", "backward"]:
            ms.player_press_sprint(True)

        if CONFIG["auto_break"]:
            ms.player_press_attack(True)

        self.last_positions = []
        start_pos = self.get_position()
        start_time = time.time()
        self.movement_start_time = start_time

        try:
            while self.running:
                time.sleep(CONFIG["check_interval"])
                if not self.check_rotation_tampering():
                    break
                current_pos = self.get_position()
                if not self.check_teleport(current_pos):
                    break
                self.check_trigger_coordinates()

                if random.random() < 0.1:
                    self.random_pause("during_movement")

                self.last_positions.append(current_pos)
                if len(self.last_positions) > CONFIG["stuck_checks"]:
                    self.last_positions.pop(0)

                if len(self.last_positions) >= CONFIG["stuck_checks"]:
                    if self.is_stuck():
                        if direction in ["right", "left"]:
                            distance_moved = math.sqrt(
                                (current_pos[0] - start_pos[0]) ** 2 +
                                (current_pos[2] - start_pos[2]) ** 2
                            )
                            elapsed = time.time() - start_time
                            if elapsed > CONFIG["block_placement_timeout"] and distance_moved < 1.0:
                                self.alert_and_stop(
                                    "Blocked while moving sideways — possible block placement!"
                                )
                                break
                        break
        finally:
            ms.player_press_right(False)
            ms.player_press_left(False)
            ms.player_press_forward(False)
            ms.player_press_backward(False)
            if CONFIG["enable_sprint"]:
                ms.player_press_sprint(False)
            if CONFIG["auto_break"]:
                ms.player_press_attack(False)

    def move_forward_blocks(self, blocks):
        """Move forward a specific number of blocks."""
        start_pos = self.get_position()
        target_distance = self.add_human_variance(blocks)

        ms.player_press_forward(True)
        if CONFIG["enable_sprint"]:
            ms.player_press_sprint(True)
        if CONFIG["auto_break"]:
            ms.player_press_attack(True)

        self.last_positions = []
        self.movement_start_time = time.time()

        try:
            while self.running:
                time.sleep(CONFIG["check_interval"])
                if not self.check_rotation_tampering():
                    break
                current_pos = self.get_position()
                if not self.check_teleport(current_pos):
                    break
                self.check_trigger_coordinates()

                self.last_positions.append(current_pos)
                if len(self.last_positions) > CONFIG["stuck_checks"]:
                    self.last_positions.pop(0)

                distance_moved = math.sqrt(
                    (current_pos[0] - start_pos[0]) ** 2 +
                    (current_pos[2] - start_pos[2]) ** 2
                )

                if len(self.last_positions) >= CONFIG["stuck_checks"]:
                    if self.is_stuck():
                        break

                if distance_moved >= target_distance:
                    break

                if random.random() < 0.05:
                    self.random_pause("during_movement")
        finally:
            ms.player_press_forward(False)
            if CONFIG["enable_sprint"]:
                ms.player_press_sprint(False)
            if CONFIG["auto_break"]:
                ms.player_press_attack(False)

    def swap_direction(self):
        if self.current_direction == "right":
            self.current_direction = "left"
        else:
            self.current_direction = "right"
        return self.current_direction

    # ------------------------------------------------------------------
    # Diagonal spiral mode
    # Each leg runs until the player's XZ position stops changing for
    # less than stuck_time_threshold seconds.
    # ------------------------------------------------------------------

    # Diagonal leg definitions: (forward, backward, left, right, sprint)
    DIAGONAL_LEGS = [
        # W + D  (forward + right)
        {"forward": False,  "backward": False, "left": False, "right": True,  "label": "D"},
        # W + A  (forward + left)
        {"forward": True,  "backward": False, "left": True,  "right": False, "label": "W+A"},
        # S      (backward only)
        {"forward": False, "backward": True,  "left": False, "right": False, "label": "S"},
        # S + A  (backward + left)
        {"forward": False, "backward": False,  "left": True,  "right": False, "label": "A"},
    ]

    def _press_leg(self, leg, press):
        """Press or release all keys for a diagonal leg."""
        if leg["forward"]:
            ms.player_press_forward(press)
        if leg["backward"]:
            ms.player_press_backward(press)
        if leg["left"]:
            ms.player_press_left(press)
        if leg["right"]:
            ms.player_press_right(press)

    def move_diagonal_leg(self, leg):
        """
        Execute one leg of the diagonal spiral.
        Holds the leg's keys and breaks when the player stops moving.
        """
        self.log(f"Diagonal leg: {leg['label']}")
        self._press_leg(leg, True)
        if CONFIG["enable_sprint"]:
            ms.player_press_sprint(True)
        if CONFIG["auto_break"]:
            ms.player_press_attack(True)

        self.last_positions = []
        self.movement_start_time = time.time()

        try:
            while self.running:
                time.sleep(CONFIG["check_interval"])
                if not self.check_rotation_tampering():
                    break
                current_pos = self.get_position()
                if not self.check_teleport(current_pos):
                    break
                self.check_trigger_coordinates()

                if random.random() < 0.07:
                    self.random_pause("during_movement")

                self.last_positions.append(current_pos)
                if len(self.last_positions) > CONFIG["stuck_checks"]:
                    self.last_positions.pop(0)

                if len(self.last_positions) >= CONFIG["stuck_checks"]:
                    if self.is_stuck():
                        break
        finally:
            self._press_leg(leg, False)
            if CONFIG["enable_sprint"]:
                ms.player_press_sprint(False)
            if CONFIG["auto_break"]:
                ms.player_press_attack(False)

    # ------------------------------------------------------------------
    # Main run loops
    # ------------------------------------------------------------------

    def run_standard(self):
        """Original left/right sweep loop."""
        self.log("Mode: Standard sweep (left/right)")
        while self.running and self.iterations < CONFIG["max_iterations"]:
            self.iterations += 1
            self.move_direction(self.current_direction)
            if not self.running:
                break
            self.random_pause("between_rows")
            self.move_forward_blocks(CONFIG["forward_blocks"])
            if not self.running:
                break
            self.random_pause("between_rows")
            self.swap_direction()

    def run_diagonal(self):
        """Diagonal spiral loop: W+D → W+A → S → S+A → repeat."""
        self.log("Mode: Diagonal spiral (W+D → W+A → S → S+A)")
        leg_index = 0
        while self.running and self.iterations < CONFIG["max_iterations"]:
            self.iterations += 1
            leg = self.DIAGONAL_LEGS[leg_index % len(self.DIAGONAL_LEGS)]
            self.move_diagonal_leg(leg)
            if not self.running:
                break
            self.random_pause("between_rows")
            leg_index += 1

    def run(self):
        """Main entry point — selects the correct loop based on CONFIG."""
        self.running = True
        self.iterations = 0

        start_pos = self.get_position()
        self.last_known_position = start_pos
        self.log(f"Starting from: ({start_pos[0]:.1f}, {start_pos[1]:.1f}, {start_pos[2]:.1f})")

        if CONFIG["enable_trigger"]:
            tx, ty, tz = CONFIG["trigger_coordinates"]
            self.log(f"Trigger active at: ({tx:.1f}, {ty:.1f}, {tz:.1f})")
            self.log(f"Command: {CONFIG['trigger_command']}")

        self.log(f"Looking to yaw={CONFIG['target_yaw']}, pitch={CONFIG['target_pitch']}...")
        self.smooth_look_to(CONFIG["target_yaw"], CONFIG["target_pitch"])
        self.log("Ready! Starting farm automation...")

        try:
            if CONFIG["diagonal_mode"]:
                self.run_diagonal()
            else:
                self.run_standard()

            if self.iterations >= CONFIG["max_iterations"]:
                self.log(f"Reached max iterations ({CONFIG['max_iterations']}). Stopping.")
            else:
                self.log("Automation stopped.")
        except KeyboardInterrupt:
            self.log("Interrupted by user.")
        except Exception as e:
            self.log(f"Error: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        self.running = False
        ms.player_press_right(False)
        ms.player_press_left(False)
        ms.player_press_forward(False)
        ms.player_press_backward(False)
        ms.player_press_sprint(False)
        ms.player_press_attack(False)
        self.log("Cleanup complete.")
def list_crops():
    print("\nAvailable crop presets:")
    print("-" * 50)
    for key, preset in CROP_PRESETS.items():
        mode = "diagonal" if preset["diagonal_mode"] else "standard"
        print(f"  {key:<12} — {preset['name']} ({mode})")
        print(f"               {preset['notes']}")
    print()


def main():
    args = sys.argv[1:]

    # ---- Quick flags that exit early ----
    if "--help" in args or "-h" in args:
        print_help()
        return

    if "--list-crops" in args:
        list_crops()
        return

    # ---- Resolve crop from --1 .. --13 number flags or --crop <name> ----
    crop_key = None
    force_custom = "--custom" in args

    # Check for --1 through --13 shorthand
    for arg in args:
        if arg.startswith("--") and arg[2:].isdigit():
            num = int(arg[2:])
            if 1 <= num <= 13:
                key, _ = CROP_MENU[num - 1]
                if key == "custom":
                    force_custom = True
                else:
                    crop_key = key
                break

    # Also support --crop <name>
    if crop_key is None and not force_custom:
        i = 0
        while i < len(args):
            if args[i] == "--crop" and i + 1 < len(args):
                crop_key = args[i + 1].lower()
                if crop_key not in CROP_PRESETS:
                    ms.echo(f"[AutoFarm] Unknown crop '{crop_key}'. Use --list-crops to see options.")
                    sys.exit(1)
                i += 2
                continue
            i += 1

    # No crop specified — print the menu in chat and exit so the player can pick
    if not force_custom and crop_key is None:
        print_crop_menu_ingame()
        return

    if force_custom:
        collect_custom_config()
    else:
        apply_crop_preset(crop_key)
        ms.echo(f"[AutoFarm] Crop: {CROP_PRESETS[crop_key]['name']}  |  "
                f"Mode: {'diagonal spiral' if CONFIG['diagonal_mode'] else 'standard sweep'}")

    # ---- Parse remaining CLI overrides (applied after preset) ----
    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ("--help", "-h", "--list-crops", "--custom"):
            i += 1
            continue
        elif arg == "--crop":
            i += 2
            continue
        elif arg == "--forward" and i + 1 < len(args):
            CONFIG["forward_blocks"] = float(args[i + 1]); i += 2; continue
        elif arg == "--yaw" and i + 1 < len(args):
            CONFIG["target_yaw"] = float(args[i + 1]); i += 2; continue
        elif arg == "--pitch" and i + 1 < len(args):
            CONFIG["target_pitch"] = float(args[i + 1]); i += 2; continue
        elif arg == "--look-time" and i + 1 < len(args):
            CONFIG["smooth_look_duration"] = float(args[i + 1]); i += 2; continue
        elif arg == "--look-steps" and i + 1 < len(args):
            CONFIG["smooth_look_steps"] = int(args[i + 1]); i += 2; continue
        elif arg == "--start-right":
            CONFIG["initial_direction"] = "right"
        elif arg == "--start-left":
            CONFIG["initial_direction"] = "left"
        elif arg == "--no-sprint":
            CONFIG["enable_sprint"] = False
        elif arg == "--no-break":
            CONFIG["auto_break"] = False
        elif arg == "--diagonal":
            CONFIG["diagonal_mode"] = True
        elif arg == "--no-diagonal":
            CONFIG["diagonal_mode"] = False
        elif arg == "--max-iter" and i + 1 < len(args):
            CONFIG["max_iterations"] = int(args[i + 1]); i += 2; continue
        elif arg == "--no-trigger":
            CONFIG["enable_trigger"] = False
        elif arg == "--trigger-x" and i + 1 < len(args):
            x, y, z = CONFIG["trigger_coordinates"]
            CONFIG["trigger_coordinates"] = (float(args[i + 1]), y, z); i += 2; continue
        elif arg == "--trigger-y" and i + 1 < len(args):
            x, y, z = CONFIG["trigger_coordinates"]
            CONFIG["trigger_coordinates"] = (x, float(args[i + 1]), z); i += 2; continue
        elif arg == "--trigger-z" and i + 1 < len(args):
            x, y, z = CONFIG["trigger_coordinates"]
            CONFIG["trigger_coordinates"] = (x, y, float(args[i + 1])); i += 2; continue
        elif arg == "--trigger-radius" and i + 1 < len(args):
            CONFIG["trigger_radius"] = float(args[i + 1]); i += 2; continue
        elif arg == "--trigger-cmd" and i + 1 < len(args):
            CONFIG["trigger_command"] = args[i + 1]; i += 2; continue

        i += 1

    automation = FarmAutomation()
    automation.run()


if __name__ == "__main__":
    main()
