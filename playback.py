#!/usr/bin/env python
"""Playback recorded motion from JSON file."""

import json
import time
import sys
from lerobot.robots.so_follower import SO101Follower, SOFollowerRobotConfig

record_name = sys.argv[1]

# Load recording
with open(record_name, "r") as f:  # Change filename!
    data = json.load(f)

# Config
config = SOFollowerRobotConfig(port="/dev/ttyACM0")
config.id = "right"

# Connect
robot = SO101Follower(config)
robot.connect()
print(f"Playing back {data['frame_count']} frames...")

motors = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]

# Playback
prev_time = 0
for frame in data["frames"]:
    # Wait for correct timing
    sleep_time = frame["time"] - prev_time
    if sleep_time > 0:
        time.sleep(sleep_time)
    prev_time = frame["time"]

    # Send action
    action = {f"{m}.pos": frame["angles"][m] for m in motors}
    robot.send_action(action)
    print(f"Time: {frame['time']:.2f}s", end="\r")

print("\nDone!")
robot.disconnect()
