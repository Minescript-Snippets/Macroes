# Macro decided to automate mining with a smooth loo, meaning it will smoothly go to blocks. 
# Cluster detection by default on, meaning it looks at clustered blocks first(toggleable from that to distance based)
# Code is not made for any server, instead singleplayer. Meaning it does not have failsafes against checks.
# Getting banned, warned. etc is your own fault.

import minescript
import math
import time
from rotation import *

# ============================================
# CONFIGURATION OPTIONS
# ============================================
CONFIG = {
    # Block type to search for and break (use Minecraft block ID)
    # Examples: 'minecraft:iron_block', 'minecraft:diamond_ore', 
    #           'minecraft:gold_block', 'minecraft:stone', etc.
    # For crops, use base name like 'minecraft:wheat' (will match all ages)
    'target_block': 'minecraft:iron_block',
    
    # If True, match blocks ignoring their state (useful for crops with age)
    # e.g., 'minecraft:wheat' will match 'minecraft:wheat[age=0]' through 'minecraft:wheat[age=7]'
    'ignore_block_state': False,
    
    # Search distance in blocks (4.5 is typical survival reach, 5.0 for creative)
    'search_distance': 5,
    
    # Rotation speed: controls how fast camera rotates (passed to rotation.py)
    # Higher = faster rotation
    'rotation_speed': 1,
    
    # Cooldown in seconds before scanning for next block
    'block_cooldown': 0.1,
    
    # If True, automatically rescan after each block is broken
    # This allows continuous mining as new blocks come into range
    'auto_rescan': True,
    
    # Key to press to trigger a new scan session (uses GLFW key codes)
    # Common keys: 89 = Y, 82 = R, 71 = G, 84 = T
    # See: https://www.glfw.org/docs/3.3/group__keys.html
    'rescan_key': 89,  # Y key
    
    # If True, visit blocks based on angular proximity (more realistic)
    # If False, visit blocks based on distance
    'use_cluster_mode': True,
    
    # If True, break blocks after looking at them
    'break_blocks': True,
    
    # Pause in seconds after looking at block before breaking it
    'break_delay': 0,
    
    # If True, intelligently target the visible face of blocks
    # (useful for partially obscured blocks)
    'use_smart_targeting': True,

    # Interpolation function for smooth camera rotation
    # Options: linear, easeInOut, easeOutQuad (from rotation.py)
    # easeInOut provides smooth acceleration and deceleration
    'interpolation': easeInOut,
}
# ============================================

def find_all_blocks(max_distance=5, block_type='minecraft:iron_block', ignore_state=False):
    """Find all blocks of specified type within max_distance (player hit range)."""
    player_pos = minescript.player_position()
    px, py, pz = player_pos
    
    search_mode = "with state ignored" if ignore_state else "exact match"
    minescript.echo(f"Searching for {block_type} within {max_distance} blocks ({search_mode})...")
    
    # Search in a smaller cube around the player (within reach)
    search_range = max_distance
    blocks_found = []
    
    # Generate list of positions to check
    positions_to_check = []
    for x in range(int(px - search_range), int(px + search_range + 1)):
        for y in range(int(py - search_range), int(py + search_range + 1)):
            for z in range(int(pz - search_range), int(pz + search_range + 1)):
                distance = math.sqrt((x - px)**2 + (y - py)**2 + (z - pz)**2)
                if distance <= max_distance:
                    positions_to_check.append([x, y, z])
    
    minescript.echo(f"Checking {len(positions_to_check)} positions...")
    
    # Use getblocklist for batch checking (much faster)
    if positions_to_check:
        block_types = minescript.getblocklist(positions_to_check)
        
        for i, found_block_type in enumerate(block_types):
            # Check if block matches
            is_match = False
            
            if ignore_state:
                # Extract base block name (before '[' if present)
                found_base = found_block_type.split('[')[0]
                target_base = block_type.split('[')[0]
                is_match = (found_base == target_base)
            else:
                # Exact match
                is_match = (found_block_type == block_type)
            
            if is_match:
                x, y, z = positions_to_check[i]
                distance = math.sqrt((x - px)**2 + (y - py)**2 + (z - pz)**2)
                blocks_found.append({
                    'position': (x, y, z),
                    'distance': distance,
                    'full_type': found_block_type  # Store the full block type with state
                })
        
        minescript.echo(f"Search complete. Found {len(blocks_found)} block(s)")
    
    return blocks_found

def find_visible_block_point(player_pos, block_pos):
    """
    Find the best visible point on a block to look at.
    Checks which face of the block is most visible and returns a point on that face.
    
    Args:
        player_pos: (x, y, z) tuple of player position
        block_pos: (x, y, z) tuple of block position (integers)
    
    Returns:
        (x, y, z) tuple of the best point to look at on the block
    """
    px, py, pz = player_pos
    bx, by, bz = block_pos
    
    # Calculate player's eye position (1.62 blocks above feet)
    eye_y = py + 1.62
    
    # Calculate direction from player eye to block center
    dx = (bx + 0.5) - px
    dy = (by + 0.5) - eye_y
    dz = (bz + 0.5) - pz
    
    # Offset from center for each face (0.45 = near edge but not quite at it)
    face_offset = 0.45
    
    # Calculate absolute differences to determine dominant direction
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    abs_dz = abs(dz)
    
    # Find the dominant axis (which face is most directly visible)
    if abs_dx > abs_dy and abs_dx > abs_dz:
        # X-axis dominant (west/east face)
        target_x = bx + (0.5 - face_offset if dx < 0 else 0.5 + face_offset)
        target_y = by + 0.5
        target_z = bz + 0.5
    elif abs_dy > abs_dz:
        # Y-axis dominant (bottom/top face)
        target_x = bx + 0.5
        target_y = by + (0.5 - face_offset if dy < 0 else 0.5 + face_offset)
        target_z = bz + 0.5
    else:
        # Z-axis dominant (north/south face)
        target_x = bx + 0.5
        target_y = by + 0.5
        target_z = bz + (0.5 - face_offset if dz < 0 else 0.5 + face_offset)
    
    return (target_x, target_y, target_z)

def calculate_look_angles(player_pos, target_pos):
    """
    Calculate yaw and pitch to look at target position from player position.
    
    Args:
        player_pos: (x, y, z) tuple of player position
        target_pos: (x, y, z) tuple of target position
    
    Returns:
        (yaw, pitch) tuple in degrees
    """
    px, py, pz = player_pos
    tx, ty, tz = target_pos
    
    # Calculate differences (adjust for player eye height at 1.62 blocks)
    dx = tx - px
    dy = ty - (py + 1.62)
    dz = tz - pz
    
    # Calculate distance in horizontal plane
    horizontal_distance = math.sqrt(dx**2 + dz**2)
    
    # Calculate pitch (vertical angle, negative because of Minecraft's coordinate system)
    pitch = -math.degrees(math.atan2(dy, horizontal_distance))
    
    # Calculate yaw (horizontal angle)
    yaw = math.degrees(math.atan2(-dx, dz))
    
    return yaw, pitch

def normalize_angle(angle):
    """Normalize angle to be between -180 and 180."""
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle

def angle_difference(current, target):
    """Calculate the shortest difference between two angles."""
    diff = normalize_angle(target - current)
    return diff

def calculate_angular_distance(yaw1, pitch1, yaw2, pitch2):
    """
    Calculate angular distance between two orientations.
    Returns a value representing how far apart two look directions are.
    """
    # Convert to radians
    yaw1_rad = math.radians(yaw1)
    pitch1_rad = math.radians(pitch1)
    yaw2_rad = math.radians(yaw2)
    pitch2_rad = math.radians(pitch2)
    
    # Convert to 3D unit vectors
    x1 = math.cos(pitch1_rad) * math.sin(yaw1_rad)
    y1 = math.sin(pitch1_rad)
    z1 = math.cos(pitch1_rad) * math.cos(yaw1_rad)
    
    x2 = math.cos(pitch2_rad) * math.sin(yaw2_rad)
    y2 = math.sin(pitch2_rad)
    z2 = math.cos(pitch2_rad) * math.cos(yaw2_rad)
    
    # Dot product gives cosine of angle between vectors
    dot_product = x1*x2 + y1*y2 + z1*z2
    # Clamp to avoid floating point errors
    dot_product = max(-1.0, min(1.0, dot_product))
    
    # Return angle in degrees
    return math.degrees(math.acos(dot_product))

def sort_blocks_by_viewing_order(blocks, player_pos, use_smart_targeting):
    """
    Sort blocks by natural viewing order (cluster-aware).
    Looks at nearest block first, then blocks close to current view direction.
    """
    if not blocks:
        return []
    
    # Start with the nearest block
    sorted_blocks = []
    remaining = blocks.copy()
    
    # Sort remaining by distance initially
    remaining.sort(key=lambda b: b['distance'])
    
    # Pick the nearest as first block
    current_block = remaining.pop(0)
    sorted_blocks.append(current_block)
    
    current_yaw, current_pitch = minescript.player_orientation()
    
    # For each subsequent block, pick the one closest to current view angle
    while remaining:
        current_pos = current_block['position']
        
        # Calculate target point (smart or center)
        if use_smart_targeting:
            target_point = find_visible_block_point(player_pos, current_pos)
        else:
            target_point = (current_pos[0] + 0.5, current_pos[1] + 0.5, current_pos[2] + 0.5)
        
        current_yaw, current_pitch = calculate_look_angles(player_pos, target_point)
        
        # Find block with minimum angular distance from current view
        best_block = None
        best_angular_distance = float('inf')
        
        for block in remaining:
            block_pos = block['position']
            
            # Calculate target point for this block
            if use_smart_targeting:
                block_target = find_visible_block_point(player_pos, block_pos)
            else:
                block_target = (block_pos[0] + 0.5, block_pos[1] + 0.5, block_pos[2] + 0.5)
            
            target_yaw, target_pitch = calculate_look_angles(player_pos, block_target)
            
            angular_dist = calculate_angular_distance(current_yaw, current_pitch,
                                                      target_yaw, target_pitch)
            
            if angular_dist < best_angular_distance:
                best_angular_distance = angular_dist
                best_block = block
        
        remaining.remove(best_block)
        sorted_blocks.append(best_block)
        current_block = best_block
    
    return sorted_blocks

def smooth_look_at(target_pos, block_pos, speed=1.0):
    """
    Smoothly rotate camera to look at target position using rotation.py functions.

    Args:
        target_pos: (x, y, z) tuple of precise target point to look at
        block_pos: (x, y, z) tuple of block position (for breaking)
        speed: Rotation speed parameter (passed directly to rotation.py)
    """
    # Use look_at from rotation.py with configured interpolation function
    look_at(target_pos[0], target_pos[1], target_pos[2], speed=speed, func=CONFIG['interpolation'])

    # Break block if enabled
    if CONFIG['break_blocks']:
        if CONFIG['break_delay'] > 0:
            time.sleep(CONFIG['break_delay'])

        # Press attack and hold until block is broken
        minescript.player_press_attack(True)

        # Keep holding until the block at target position is gone
        block_x, block_y, block_z = block_pos
        original_block = minescript.getblock(block_x, block_y, block_z)

        # Hold attack until block changes (is broken) or timeout
        max_wait = 10.0  # Maximum 10 seconds
        wait_time = 0.0
        check_interval = 0.05

        while wait_time < max_wait:
            time.sleep(check_interval)
            wait_time += check_interval

            current_block = minescript.getblock(block_x, block_y, block_z)
            if current_block != original_block:
                # Block was broken
                break

        minescript.player_press_attack(False)

def main():
    """Main function to find and look at all target blocks sequentially."""
    minescript.echo("=== Smooth Auto Mining Script ===")
    minescript.echo(f"Target: {CONFIG['target_block']}")
    minescript.echo(f"Config: distance={CONFIG['search_distance']}m, " +
                   f"speed={CONFIG['rotation_speed']}s, " +
                   f"cooldown={CONFIG['block_cooldown']}s")
    minescript.echo(f"Features: cluster_mode={CONFIG['use_cluster_mode']}, " +
                   f"break_blocks={CONFIG['break_blocks']}, " +
                   f"smart_targeting={CONFIG['use_smart_targeting']}, " +
                   f"auto_rescan={CONFIG['auto_rescan']}, " +
                   f"ignore_state={CONFIG['ignore_block_state']}")
    
    # Get key name for display
    key_names = {89: 'Y', 82: 'R', 71: 'G', 84: 'T'}
    rescan_key_name = key_names.get(CONFIG['rescan_key'], f"key {CONFIG['rescan_key']}")
    minescript.echo(f"\nPress '{rescan_key_name}' to start mining | Open any GUI to exit")
    
    total_blocks_processed = 0
    session_blocks = 0  # Blocks in current session
    is_active = False  # Whether we're actively processing blocks
    
    # Setup event queue for key and screen events
    event_queue = minescript.EventQueue()
    event_queue.register_key_listener()
    
    try:
        while True:
            # Check for exit condition (GUI opened)
            current_screen = minescript.screen_name()
            if current_screen is not None:
                minescript.echo(f"GUI opened ({current_screen}) - Exiting script...")
                break
            
            # Check for scan key press to start/restart
            try:
                while True:
                    event = event_queue.get(block=False)
                    if event.type == "key":
                        # Key down event (action == 1) and matches rescan key
                        if event.action == 1 and event.key == CONFIG['rescan_key']:
                            if is_active:
                                minescript.echo(f"\n'{rescan_key_name}' pressed - Pausing mining!")
                                minescript.echo(f"Session stats: {session_blocks} blocks mined")
                                is_active = False
                                session_blocks = 0
                            else:
                                minescript.echo(f"\n'{rescan_key_name}' pressed - Starting mining!")
                                is_active = True
            except:
                pass  # No events in queue
            
            # Only process if active
            if not is_active:
                time.sleep(0.1)
                continue
            
            player_pos = minescript.player_position()
            
            # Scan for all target blocks (fresh scan every time)
            blocks = find_all_blocks(
                max_distance=CONFIG['search_distance'],
                block_type=CONFIG['target_block'],
                ignore_state=CONFIG['ignore_block_state']
            )
            
            if not blocks:
                if CONFIG['auto_rescan']:
                    # In auto-rescan mode, keep checking silently
                    time.sleep(0.5)  # Wait a bit before rescanning
                    continue
                else:
                    minescript.echo(f"✓ No blocks found in range!")
                    minescript.echo(f"Total blocks mined this session: {session_blocks}")
                    minescript.echo(f"Press '{rescan_key_name}' to stop/start or open GUI to exit")
                    is_active = False
                    session_blocks = 0
                    time.sleep(0.1)
                    continue
            
            # Sort blocks based on configuration
            if CONFIG['use_cluster_mode']:
                sorted_blocks = sort_blocks_by_viewing_order(
                    blocks, 
                    player_pos,
                    CONFIG['use_smart_targeting']
                )
            else:
                sorted_blocks = sorted(blocks, key=lambda b: b['distance'])
            
            # Process only the first block in the sorted list
            block_info = sorted_blocks[0]
            
            # Check for exit condition before processing
            current_screen = minescript.screen_name()
            if current_screen is not None:
                minescript.echo(f"GUI opened ({current_screen}) - Exiting script...")
                break
            
            x, y, z = block_info['position']
            distance = block_info['distance']
            full_type = block_info.get('full_type', CONFIG['target_block'])
            
            # Calculate target point based on smart targeting setting
            if CONFIG['use_smart_targeting']:
                target_point = find_visible_block_point(player_pos, (x, y, z))
                targeting_mode = "visible face"
            else:
                target_point = (x + 0.5, y + 0.5, z + 0.5)
                targeting_mode = "center"
            
            total_available = len(blocks)
            minescript.echo(f"[{total_available} available] Mining {full_type} at ({x}, {y}, {z}) [{targeting_mode}] - {distance:.1f}m")
            
            # Smooth look with configured speed
            smooth_look_at(
                target_point,
                (x, y, z),
                speed=CONFIG['rotation_speed']
            )
            
            # Increment counters
            total_blocks_processed += 1
            session_blocks += 1
            
            # Pause before next scan/block
            if CONFIG['block_cooldown'] > 0:
                time.sleep(CONFIG['block_cooldown'])
            
            # With auto_rescan enabled, loop continues and rescans immediately
            # This allows continuous mining as the player moves or new blocks appear
    
    finally:
        minescript.echo(f"✓ Script ended. Total blocks mined: {total_blocks_processed}")


# Run the script
if __name__ == "__main__":
    main()
