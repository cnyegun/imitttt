#!/usr/bin/env python
"""Record SO101 arm angles - interactive version."""

import time
import json
from datetime import datetime
from lerobot.robots.so_follower import SO101Follower, SOFollowerRobotConfig

# Config
config = SOFollowerRobotConfig(port="/dev/ttyACM0")
config.id = "right"

robot = SO101Follower(config)
robot.connect()

motors = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]
frames = []
start_time = time.time()  # Initialize to avoid None
recording = False

print("=" * 60)
print("SO101 Arm Recorder")
print("=" * 60)
print("\nCommands:")
print("  s = Snapshot (record current pose, torque stays ON)")
print("  c = Continuous recording (arm goes LIMP, move by hand!)")
print("  p = Print current angles")
print("  r = Relax (disable torque - move arm by hand!)")
print("  h = Hold (enable torque - stiffen arm)")
print("  d = Done (save and exit)")
print("  q = Quit (discard and exit)")
print()


def get_angles():
    obs = robot.get_observation()
    return [obs[f"{m}.pos"] for m in motors]


def print_angles(angles):
    print(
        f"  Pan: {angles[0]:7.1f}°  Lift: {angles[1]:7.1f}°  Elbow: {angles[2]:7.1f}°  Wrist: {angles[3]:7.1f}°  Roll: {angles[4]:7.1f}°  Grip: {angles[5]:7.1f}°"
    )


def save_recording():
    if not frames:
        print("Nothing to save!")
        return
    filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(
            {
                "robot": "so101_follower",
                "duration": frames[-1]["time"] if frames else 0,
                "frame_count": len(frames),
                "fps": 20,
                "frames": frames,
            },
            f,
            indent=2,
        )
    print(f"Saved {len(frames)} frames to: {filename}")


# Main loop
while True:
    cmd = input("\nCommand: ").strip().lower()

    if cmd == "s":
        # Snapshot
        angles = get_angles()
        if not frames:
            start_time = time.time()
        elapsed = time.time() - start_time
        frames.append({"time": elapsed, "angles": dict(zip(motors, angles))})
        print(f"Recorded frame {len(frames)}:")
        print_angles(angles)

    elif cmd == "c":
        # Toggle continuous recording
        if not recording:
            print("Limp mode - recording starts in 1 second...")
            robot.bus.disable_torque()  # Make arm limp!
            time.sleep(1)  # Give time to grab the arm
            print("RECORDING! Move arm by hand. Press 'c' to stop.")
            recording = True
            if not frames:
                start_time = time.time()
            while recording:
                angles = get_angles()
                elapsed = time.time() - start_time
                frames.append({"time": elapsed, "angles": dict(zip(motors, angles))})
                print(f"Frame {len(frames)}\r", end="")
                time.sleep(0.05)
                # Check for input without blocking
                import select
                import sys

                if select.select([sys.stdin], [], [], 0)[0]:
                    if sys.stdin.readline().strip().lower() == "c":
                        recording = False

            # After loop ends, re-enable torque
            robot.bus.enable_torque()
            print(f"\nStopped. Total frames: {len(frames)}")
            print("Torque ENABLED - arm holding last position")
        else:
            recording = False

    elif cmd == "p":
        angles = get_angles()
        print("Current angles:")
        print_angles(angles)

    elif cmd == "r":
        robot.bus.disable_torque()
        print("Torque DISABLED - you can now move the arm by hand!")

    elif cmd == "h":
        robot.bus.enable_torque()
        print("Torque ENABLED - arm is stiff and holding position")

    elif cmd == "d":
        save_recording()
        break

    elif cmd == "q":
        if frames:
            save = input(f"Discard {len(frames)} frames? (y/n): ").strip().lower()
            if save != "y":
                save_recording()
        break

    else:
        print("Unknown command. Try: s, c, p, r, h, d, q")

robot.disconnect()
print("Disconnected.")
