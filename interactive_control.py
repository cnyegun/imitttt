#!/usr/bin/env python
"""Interactive SO101 arm controller with named poses."""

import time
from lerobot.robots.so_follower import SO101Follower, SOFollowerRobotConfig

# Named poses (shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper)
poses = {
    "rest": [0, -90, 90, 0, 0, 0],  # Arm up, relaxed
    "reach": [0, 0, 0, 0, 0, 50],  # Straight out, open gripper
    "pickup": [0, 45, 90, -45, 0, 50],  # Down and ready
    "wave": [0, -45, 90, 0, 0, 0],  # Mid position
}

# Config
config = SOFollowerRobotConfig(port="/dev/ttyACM0")
config.id = "right"

robot = SO101Follower(config)
robot.connect()
print("Connected!")
print("\nCommands:")
print("  1 = rest pose")
print("  2 = reach pose")
print("  3 = pickup pose")
print("  4 = wave pose")
print("  q = quit")
print()

motors = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]


def move_to(target, duration=2.0):
    """Move smoothly to target pose."""
    obs = robot.get_observation()
    current = [obs[f"{m}.pos"] for m in motors]

    steps = 40
    for i in range(steps + 1):
        alpha = i / steps
        interpolated = [c + (t - c) * alpha for c, t in zip(current, target)]
        action = {f"{m}.pos": v for m, v in zip(motors, interpolated)}
        robot.send_action(action)
        time.sleep(duration / steps)


# Main loop
while True:
    cmd = input("Command: ").strip().lower()

    if cmd == "1":
        move_to(poses["rest"])
        print("→ Rest pose")
    elif cmd == "2":
        move_to(poses["reach"])
        print("→ Reach pose")
    elif cmd == "3":
        move_to(poses["pickup"])
        print("→ Pickup pose")
    elif cmd == "4":
        move_to(poses["wave"])
        print("→ Wave pose")
    elif cmd == "q":
        break
    else:
        print("Unknown command")

robot.disconnect()
print("Goodbye!")
