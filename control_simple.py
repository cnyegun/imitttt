#!/usr/bin/env python
"""Bare-bones SO101 follower control script."""

import time
from lerobot.robots.so_follower import SO101Follower, SOFollowerRobotConfig

# Config
config = SOFollowerRobotConfig(port="/dev/ttyACM0")
config.id = "right"

# Connect
robot = SO101Follower(config)
robot.connect()
print("Connected!")

# Read current position
obs = robot.get_observation()
motors = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]
current = [obs[f"{m}.pos"] for m in motors]
print(f"Current: {current}")

# Set target positions (degrees)
target = [0, 0, -90, 0, 0, 0]

# Move slowly
steps = 50
duration = 3.0  # seconds

for i in range(steps + 1):
    alpha = i / steps
    interpolated = [c + (t - c) * alpha for c, t in zip(current, target)]
    action = {f"{m}.pos": v for m, v in zip(motors, interpolated)}
    robot.send_action(action)
    time.sleep(duration / steps)

print("Done!")
time.sleep(10)
robot.disconnect()
