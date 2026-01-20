# Macro decided to automate farming within a pattern, meaning it will go from right, forward, left. etc(You will need to setup a farm suitable for it) 
# Code is not made for any specific server, failsafes are basic. (Teleport checks, Yaw/Pitch change checks)
# Getting banned, warned. etc, is your own fault, and only yours.

import minescript as ms
import time
import random
import math
import sys

# ===== CONFIGURATION =====
CONFIG = {
    # Coordinate trigger settings
    "trigger_coordinates": (136.7, 70, -142.7),  # (x, y, z) coordinates to run command
    "trigger_radius": 1.5,  # Distance from trigger point to activate (blocks)
    "trigger_command": "/warp garden",  # Command to run 
    "enable_trigger": True,  # Set to False to disable coordinate tping
    
    # Movement settings
    "forward_blocks": 8.5,
    "initial_direction": "left",
    
    # View direction settings (yaw, pitch)
    "target_yaw": -90.0,  # Target yaw angle (0-360)
    "target_pitch": 0.0,  # Target pitch angle (-90 to 90)
    "smooth_look_duration": 1.0,  # Total time to reach target (seconds)
    "smooth_look_steps": 60,  # Number of steps for smooth rotation
    
    # Breaking settings
    "auto_break": True,
    
    # Randomization settings
    "position_variance": 0.15,
    "pause_between_rows": (0.1, 0.3),
    "pause_during_movement": (0.05, 0.15),
    
    # Detection settings
    "check_interval": 0.05,
    "stuck_threshold": 0.05,
    "stuck_checks": 3,
    
    # Anti-macro detection
    "yaw_pitch_tolerance": 5.0,  # Degrees of allowed deviation before alert
    "block_placement_timeout": 2.0,  # Seconds stuck before assuming block placed
    "teleport_distance": 10.0,  # Distance threshold for teleport detection
    
    # Safety
    "max_iterations": 1000,
    "enable_sprint": True,
}

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
        self.trigger_activated = False  # Track if trigger was recently activated
        self.trigger_cooldown = 0  # Cooldown timer to prevent repeated triggers
        
    def log(self, message):
        """Log message to chat"""
        ms.echo(f"[AutoFarm] {message}")
        
    def alert_and_stop(self, reason):
        """Alert user and stop the script"""
        self.log(f"!!! ALERT: {reason} !!!")
        self.log("Script stopped for safety!")
        self.running = False
        
    def get_position(self):
        """Get current player position"""
        player = ms.player()
        return player.position
    
    def distance_to_coordinates(self, pos, target_coords):
        """Calculate distance between two 3D points"""
        return math.sqrt(
            (pos[0] - target_coords[0]) ** 2 +
            (pos[1] - target_coords[1]) ** 2 +
            (pos[2] - target_coords[2]) ** 2
        )
    
    def check_trigger_coordinates(self):
        """Check if player hit trigger coordinates and execute command"""
        if not CONFIG["enable_trigger"]:
            return
        
        # Cooldown check - prevent triggering multiple times in quick succession
        current_time = time.time()
        if current_time - self.trigger_cooldown < 5.0:  # 5 second cooldown
            return
            
        current_pos = self.get_position()
        trigger_coords = CONFIG["trigger_coordinates"]
        distance = self.distance_to_coordinates(current_pos, trigger_coords)
        
        if distance <= CONFIG["trigger_radius"]:
            self.log(f"Hit trigger coordinates! Executing: {CONFIG['trigger_command']}")
            ms.execute(CONFIG["trigger_command"])
            self.trigger_cooldown = current_time
            # Give time for warp to complete
            time.sleep(1.0)
        
    def get_rotation(self):
        """Get current player rotation (yaw, pitch)"""
        player = ms.player()
        return (player.yaw, player.pitch)
        
    def normalize_angle(self, angle):
        """Normalize angle to 0-360 range"""
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        return angle
        
    def angle_difference(self, angle1, angle2):
        """Calculate shortest difference between two angles"""
        diff = self.normalize_angle(angle2 - angle1)
        if diff > 180:
            diff -= 360
        return abs(diff)
        
    def smooth_look_to(self, target_yaw, target_pitch):
        """Smoothly rotate view to target yaw and pitch"""
        target_yaw = self.normalize_angle(target_yaw)
        
        # Get current rotation
        current_yaw, current_pitch = self.get_rotation()
        current_yaw = self.normalize_angle(current_yaw)
        
        # Calculate total differences
        yaw_diff = self.normalize_angle(target_yaw - current_yaw)
        if yaw_diff > 180:
            yaw_diff -= 360
        
        pitch_diff = target_pitch - current_pitch
        
        # Calculate step sizes and timing
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
        """Check if rotation has been changed by external force"""
        current_yaw, current_pitch = self.get_rotation()
        current_yaw = self.normalize_angle(current_yaw)
        
        yaw_diff = self.angle_difference(current_yaw, self.expected_yaw)
        pitch_diff = abs(current_pitch - self.expected_pitch)
        
        if yaw_diff > CONFIG["yaw_pitch_tolerance"] or pitch_diff > CONFIG["yaw_pitch_tolerance"]:
            self.alert_and_stop(f"Rotation changed! Yaw diff: {yaw_diff:.1f}°, Pitch diff: {pitch_diff:.1f}°")
            return False
        return True
        
    def check_teleport(self, current_pos):
        """Check if player has been teleported"""
        if self.last_known_position is None:
            self.last_known_position = current_pos
            return True
        
        # Skip teleport check if trigger was recently activated (within 3 seconds)
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
        """Add random variance to make movement more human-like"""
        variance = random.uniform(-CONFIG["position_variance"], CONFIG["position_variance"])
        return base_value + variance
        
    def random_pause(self, pause_type="between_rows"):
        """Add a random pause to try and show human reaction time"""
        if pause_type == "between_rows":
            min_pause, max_pause = CONFIG["pause_between_rows"]
        else:
            min_pause, max_pause = CONFIG["pause_during_movement"]
        
        pause_duration = random.uniform(min_pause, max_pause)
        time.sleep(pause_duration)
        
    def is_stuck(self):
        """Check if player is stuck (not moving)"""
        if len(self.last_positions) < CONFIG["stuck_checks"]:
            return False
            
        recent_positions = self.last_positions[-CONFIG["stuck_checks"]:]
        for i in range(1, len(recent_positions)):
            x_diff = abs(recent_positions[i][0] - recent_positions[i-1][0])
            z_diff = abs(recent_positions[i][2] - recent_positions[i-1][2])
            
            if x_diff > CONFIG["stuck_threshold"] or z_diff > CONFIG["stuck_threshold"]:
                return False
                
        return True
        
    def move_direction(self, direction):
        """Move in specified direction until stuck"""
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
        
        try:
            while self.running:
                time.sleep(CONFIG["check_interval"])
                
                # Anti-macro checks
                if not self.check_rotation_tampering():
                    break
        
                current_pos = self.get_position()
                if not self.check_teleport(current_pos):
                    break
            
                # Check for coordinate trigger
                self.check_trigger_coordinates()
                
                if random.random() < 0.1:
                    self.random_pause("during_movement")
                
                self.last_positions.append(current_pos)
                
                if len(self.last_positions) > CONFIG["stuck_checks"]:
                    self.last_positions.pop(0)
                
                if len(self.last_positions) >= CONFIG["stuck_checks"]:
                    if self.is_stuck():
                        # Check for block placement when moving sideways
                        if direction in ["right", "left"]:
                            distance_moved = math.sqrt(
                                (current_pos[0] - start_pos[0]) ** 2 +
                                (current_pos[2] - start_pos[2]) ** 2
                            )
                            elapsed = time.time() - start_time
                            
                            # If stuck quickly and haven't moved much, possible block placement
                            if elapsed > CONFIG["block_placement_timeout"] and distance_moved < 1.0:
                                self.alert_and_stop("Blocked while moving sideways - possible block placement!")
                                break
                        
                        # Normal stuck detection - reached end
                        break
                    
        finally:
            if direction == "right":
                ms.player_press_right(False)
            elif direction == "left":
                ms.player_press_left(False)
            elif direction == "forward":
                ms.player_press_forward(False)
            elif direction == "backward":
                ms.player_press_backward(False)
                
            if CONFIG["enable_sprint"]:
                ms.player_press_sprint(False)
            
            if CONFIG["auto_break"]:
                ms.player_press_attack(False)
                
    def move_forward_blocks(self, blocks):
        """Move forward a specific number of blocks"""
        start_pos = self.get_position()
        target_distance = blocks
        target_distance = self.add_human_variance(target_distance)
        
        ms.player_press_forward(True)
        if CONFIG["enable_sprint"]:
            ms.player_press_sprint(True)
        
        if CONFIG["auto_break"]:
            ms.player_press_attack(True)
        
        self.last_positions = []
            
        try:
            while self.running:
                time.sleep(CONFIG["check_interval"])
                
                # Anti-macro checks
                if not self.check_rotation_tampering():
                    break
                
                current_pos = self.get_position()
                if not self.check_teleport(current_pos):
                    break
                
                # Check for coordinate trigger
                self.check_trigger_coordinates()
                
                self.last_positions.append(current_pos)
                if len(self.last_positions) > CONFIG["stuck_checks"]:
                    self.last_positions.pop(0)
                
                distance_moved = math.sqrt(
                    (current_pos[0] - start_pos[0]) ** 2 +
                    (current_pos[2] - start_pos[2]) ** 2
                )
                
                # Normal stuck detection - just stop, don't alert
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
        """Swap between left and right direction"""
        if self.current_direction == "right":
            self.current_direction = "left"
        else:
            self.current_direction = "right"
        return self.current_direction
        
    def run(self):
        """Main automation loop"""
        self.running = True
        self.iterations = 0
        
        start_pos = self.get_position()
        self.last_known_position = start_pos
        self.log(f"Starting from: ({start_pos[0]:.1f}, {start_pos[1]:.1f}, {start_pos[2]:.1f})")
        
        if CONFIG["enable_trigger"]:
            trigger_coords = CONFIG["trigger_coordinates"]
            self.log(f"Trigger active at: ({trigger_coords[0]:.1f}, {trigger_coords[1]:.1f}, {trigger_coords[2]:.1f})")
            self.log(f"Command: {CONFIG['trigger_command']}")
        
        # Smoothly look to target direction
        self.log(f"Looking to yaw={CONFIG['target_yaw']}, pitch={CONFIG['target_pitch']}...")
        self.smooth_look_to(CONFIG["target_yaw"], CONFIG["target_pitch"])
        self.log("Ready! Starting farm automation...")
        
        try:
            while self.running and self.iterations < CONFIG["max_iterations"]:
                self.iterations += 1
                
                # Move in current direction
                self.move_direction(self.current_direction)
                
                if not self.running:
                    break
                
                self.random_pause("between_rows")
                
                # Move forward
                self.move_forward_blocks(CONFIG["forward_blocks"])
                
                if not self.running:
                    break
                
                self.random_pause("between_rows")
                
                # Swap direction
                self.swap_direction()
                
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
        """Release all keys and clean up"""
        self.running = False
        ms.player_press_right(False)
        ms.player_press_left(False)
        ms.player_press_forward(False)
        ms.player_press_backward(False)
        ms.player_press_sprint(False)
        ms.player_press_attack(False)
        self.log("Cleanup complete.")

# ===== COMMAND LINE INTERFACE =====
def print_help():
    """Print help information"""
    help_text = """
Auto Farm Movement Script
Usage: \\farm_auto_move [options]

Options:
  --forward <blocks>    : Blocks to move forward (default: 8.5)
  --yaw <angle>        : Target yaw angle 0-360 (default: -90)
  --pitch <angle>      : Target pitch angle -90 to 90 (default: 4)
  --look-time <sec>    : Time to rotate to target (default: 1.0)
  --look-steps <n>     : Smoothness steps (default: 60)
  --start-right        : Start moving right (default)
  --start-left         : Start moving left
  --no-sprint          : Disable sprinting
  --no-break           : Disable auto-breaking
  
  Coordinate Trigger Options:
  --trigger-x <x>      : Set trigger X coordinate (default: 136.7)
  --trigger-y <y>      : Set trigger Y coordinate (default: 70)
  --trigger-z <z>      : Set trigger Z coordinate (default: -142.7)
  --trigger-radius <r> : Distance from trigger point to activate (default: 1.5)
  --trigger-cmd <cmd>  : Command to run at trigger (default: /warp garden)
  --no-trigger         : Disable coordinate trigger
  
  --help               : Show this help

Examples:
  \\farm_auto_move
  \\farm_auto_move --yaw 180 --pitch 10
  \\farm_auto_move --trigger-x 100 --trigger-y 64 --trigger-z -200
  \\farm_auto_move --trigger-cmd "/tp @s 0 64 0"
  \\farm_auto_move --trigger-radius 3 --trigger-cmd "/warp home"
"""
    print(help_text)

def main():
    """Main entry point"""
    args = sys.argv[1:]
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg in ["--help", "-h"]:
            print_help()
            return
        elif arg == "--forward":
            if i + 1 < len(args):
                CONFIG["forward_blocks"] = float(args[i + 1])
                i += 1
        elif arg == "--yaw":
            if i + 1 < len(args):
                CONFIG["target_yaw"] = float(args[i + 1])
                i += 1
        elif arg == "--pitch":
            if i + 1 < len(args):
                CONFIG["target_pitch"] = float(args[i + 1])
                i += 1
        elif arg == "--look-time":
            if i + 1 < len(args):
                CONFIG["smooth_look_duration"] = float(args[i + 1])
                i += 1
        elif arg == "--look-steps":
            if i + 1 < len(args):
                CONFIG["smooth_look_steps"] = int(args[i + 1])
                i += 1
        elif arg == "--start-right":
            CONFIG["initial_direction"] = "right"
        elif arg == "--start-left":
            CONFIG["initial_direction"] = "left"
        elif arg == "--no-sprint":
            CONFIG["enable_sprint"] = False
        elif arg == "--no-break":
            CONFIG["auto_break"] = False
        elif arg == "--max-iter":
            if i + 1 < len(args):
                CONFIG["max_iterations"] = int(args[i + 1])
                i += 1
        # Coordinate trigger options
        elif arg == "--no-trigger":
            CONFIG["enable_trigger"] = False
        elif arg == "--trigger-x":
            if i + 1 < len(args):
                x, y, z = CONFIG["trigger_coordinates"]
                CONFIG["trigger_coordinates"] = (float(args[i + 1]), y, z)
                i += 1
        elif arg == "--trigger-y":
            if i + 1 < len(args):
                x, y, z = CONFIG["trigger_coordinates"]
                CONFIG["trigger_coordinates"] = (x, float(args[i + 1]), z)
                i += 1
        elif arg == "--trigger-z":
            if i + 1 < len(args):
                x, y, z = CONFIG["trigger_coordinates"]
                CONFIG["trigger_coordinates"] = (x, y, float(args[i + 1]))
                i += 1
        elif arg == "--trigger-radius":
            if i + 1 < len(args):
                CONFIG["trigger_radius"] = float(args[i + 1])
                i += 1
        elif arg == "--trigger-cmd":
            if i + 1 < len(args):
                CONFIG["trigger_command"] = args[i + 1]
                i += 1
        i += 1
    automation = FarmAutomation()
    automation.run()
    
if __name__ == "__main__":
    main()
