import csv
import math
import random
import time

CSV_FILE = "motor_telemetry.csv"

# Initialize CSV file with headers matching problem statement specs
headers = [
    "timestamp",
    "target_rpm",
    "measured_rpm",
    "current",
    "voltage",
    "temp",
    "fault_type",
]
with open(CSV_FILE, "w", newline="") as f:
  writer = csv.writer(f)
  writer.writerow(headers)

print("=" * 60)
print("Motor Simulator Running! Writing data to", CSV_FILE)
print("Inject faults on the fly:")
print("  Type 'n' -> Normal operation")
print("  Type 'f' -> Friction / Bearing overload")
print("  Type 'h' -> Overheating")
print("  Type 's' -> Sensor disconnect (Tachometer cut)")
print("=" * 60)

# Mode controller
current_mode = "n"
motor_temp = 30.0  # Ambient deg C
t = 0.0

import threading


def user_input_thread():
  global current_mode
  while True:
    try:
      cmd = input().strip().lower()
      if cmd in ["n", "f", "h", "s"]:
        current_mode = cmd
        print(f"\n>>> MODE CHANGED TO: {current_mode.upper()} <<<\n")
    except EOFError:
      break


# Start background input listener
threading.Thread(target=user_input_thread, daemon=True).start()

target_rpm = 1500.0

while True:
  t += 0.1
  voltage = 12.0 + random.uniform(-0.05, 0.05)

  if current_mode == "n":
    # Normal healthy motor
    measured_rpm = target_rpm + random.uniform(-10.0, 10.0)
    current = 0.45 + random.uniform(-0.02, 0.02)
    # Natural steady thermal equilibrium ~35C
    motor_temp += (35.0 - motor_temp) * 0.02 + random.uniform(-0.05, 0.05)
    fault_label = "NORMAL"

  elif current_mode == "f":
    # Bearing friction / mechanical drag: RPM drops, Current spikes
    measured_rpm = target_rpm - 350.0 + random.uniform(-20.0, 20.0)
    current = 1.35 + random.uniform(-0.05, 0.05)
    motor_temp += 0.1
    fault_label = "FRICTION_OVERLOAD"

  elif current_mode == "h":
    # Thermal runaway / cooling loss: rapid heating
    measured_rpm = target_rpm + random.uniform(-15.0, 15.0)
    current = 0.55 + random.uniform(-0.02, 0.02)
    motor_temp += 0.35  # Clamping temp rise
    fault_label = "OVERHEATING"

  elif current_mode == "s":
    # Sensor disconnect / wire cut: RPM reads 0, but current is normal
    measured_rpm = 0.0
    current = 0.45 + random.uniform(-0.02, 0.02)
    fault_label = "SENSOR_FAULT"

  # Append latest snapshot
  with open(CSV_FILE, "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        round(t, 2),
        target_rpm,
        round(measured_rpm, 1),
        round(current, 3),
        round(voltage, 2),
        round(motor_temp, 2),
        fault_label,
    ])

  time.sleep(0.1)  # 10 Hz sampling rate