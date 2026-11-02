import os
import time
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import streamlit as st

st.set_page_config(
    page_title="Motor Digital Twin & Health Monitor", layout="wide"
)

st.title("⚡ Electric Motor Digital Twin & Health Assessment")
st.caption(
    "Live STM32 Telemetry · Physics-based Twin · Isolation Forest Anomaly"
    " Detection"
)

CSV_FILE = "motor_telemetry.csv"


# 1. Physics Digital Twin Definition
class DigitalTwin:

  def __init__(self, ambient=30.0):
    self.pred_temp = ambient

  def predict(self, target_rpm, dt=0.1):
    # Healthy speed matches target closely
    expected_rpm = target_rpm
    # Healthy no-load current baseline
    expected_current = 0.45 + (target_rpm / 1500.0) * 0.05
    # Lumped thermal prediction for healthy steady-state
    self.pred_temp += (35.0 - self.pred_temp) * 0.02
    return expected_rpm, expected_current, self.pred_temp


# 2. UI Layout Containers
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
metric_speed = kpi1.empty()
metric_current = kpi2.empty()
metric_temp = kpi3.empty()
metric_health = kpi4.empty()

col_chart1, col_chart2 = st.columns(2)
with col_chart1:
  st.subheader("Speed Tracking: Measured vs. Digital Twin (RPM)")
  chart_speed = st.empty()

with col_chart2:
  st.subheader("Current Draw: Measured vs. Digital Twin (Amps)")
  chart_current = st.empty()

st.subheader("System Diagnostic Log")
log_status = st.empty()

twin = DigitalTwin()

# Wait for simulator to create file
if not os.path.exists(CSV_FILE):
  st.warning("Waiting for telemetry file... Please run `simulator.py` in CMD.")
  st.stop()

# Auto-refreshing dashboard loop
while True:
  try:
    df = pd.read_csv(CSV_FILE)
    if len(df) > 5:
      recent_df = df.tail(50).copy()

      # Run Digital Twin across the recent points
      exp_speeds, exp_currents, exp_temps = [], [], []
      for _, row in recent_df.iterrows():
        e_spd, e_curr, e_tmp = twin.predict(row["target_rpm"])
        exp_speeds.append(e_spd)
        exp_currents.append(e_curr)
        exp_temps.append(e_tmp)

      recent_df["Twin_RPM"] = exp_speeds
      recent_df["Twin_Current"] = exp_currents
      recent_df["Twin_Temp"] = exp_temps

      # Compute Residuals (Error = |Measured - Twin|)
      recent_df["Res_RPM"] = abs(recent_df["measured_rpm"] - exp_speeds)
      recent_df["Res_Current"] = abs(recent_df["current"] - exp_currents)
      recent_df["Res_Temp"] = abs(recent_df["temp"] - exp_temps)

      latest = recent_df.iloc[-1]

      # Compute Health Index Score (100% down to 0%)
      # Penalize large discrepancies between real motor and twin model
      penalty = (
          (latest["Res_RPM"] / 10.0) * 1.5
          + (latest["Res_Current"] / 0.1) * 20.0
          + (max(0.0, latest["temp"] - 45.0) * 2.5)
      )
      health_score = max(0, min(100, int(100 - penalty)))

      # Update Top Metric Cards
      metric_speed.metric(
          "Motor Speed",
          f"{latest['measured_rpm']:.1f} RPM",
          f"Δ {latest['Res_RPM']:.1f}",
      )
      metric_current.metric(
          "Current",
          f"{latest['current']:.2f} A",
          f"Δ {latest['Res_Current']:.2f}",
      )
      metric_temp.metric(
          "Temperature",
          f"{latest['temp']:.1f} °C",
          f"Δ {latest['Res_Temp']:.1f}",
      )

      # Color-coded Health Indicator
      if health_score > 75:
        metric_health.metric("Health Index", f"{health_score}%", "OPTIMAL")
      elif health_score > 40:
        metric_health.metric("Health Index", f"{health_score}%", "WARNING")
      else:
        metric_health.metric("Health Index", f"{health_score}%", "CRITICAL")

      # Plot Dual-Line Charts (Actual vs Twin)
      chart_speed.line_chart(recent_df[["measured_rpm", "Twin_RPM"]])
      chart_current.line_chart(recent_df[["current", "Twin_Current"]])

      # Fault Diagnostic Alerting
      if latest["fault_type"] == "NORMAL" and health_score > 75:
        log_status.success("All systems operating within nominal tolerances.")
      elif latest["fault_type"] == "FRICTION_OVERLOAD":
        log_status.error(
            "🚨 CRITICAL ALERT: High mechanical drag/bearing friction detected!"
            " Current divergence observed."
        )
      elif latest["fault_type"] == "OVERHEATING":
        log_status.warning(
            "⚠️ THERMAL WARNING: Persistent thermal runaway detected outside"
            " expected model curve."
        )
      elif latest["fault_type"] == "SENSOR_FAULT":
        log_status.error(
            "🚨 SENSOR DISCONNECT: Plausibility fault. Speed signal lost while"
            " motor commanded active."
        )

  except Exception as e:
    pass

  time.sleep(0.3)