# Electric Motor Digital Twin & Health Monitoring System

A dual-approach predictive health monitoring and diagnostic framework for electric motor drives, developed for the hackathon demonstration.

---

## 1. Project Overview
This project continuously monitors electric motor telemetry (Speed, Current, Voltage, and Temperature) and evaluates asset health in real time. Rather than relying on simple hard thresholds, the system runs an independent **Physics-based Digital Twin** on the host machine. By comparing real-time telemetry against the twin's baseline predictions, dynamic residual errors are extracted to detect and classify early-stage anomalies before mechanical or electrical failure occurs.

---

## 2. Dual Architecture & Implementation Tracks

### Track A: Software-in-the-Loop (SIL) Simulation (Primary Standalone Demo)
* **Telemetry Generator:** `stimulator.py` emulates continuous 10 Hz motor kinematics, electrical loading, and lumped thermal accumulation.
* **Fault Injection Scenarios:** Verified via live keyboard triggers:
  * `n` — **Nominal Operation:** Normal closed-loop tracking; residuals remain near zero; Health Index at 100%.
  * `f` — **Mechanical Drag / Friction:** Motor current spikes while speed drops; residual surge triggers Critical Drag warning.
  * `h` — **Thermal Deviation / Runaway:** Persistent divergence from thermal equilibrium model; triggers early Overheating alert.
  * `s` — **Sensor Plausibility Fault:** Detects zero speed while current and voltage are active, isolating a broken sensor line from a mechanical motor stall.

### Track B: Hardware-in-the-Loop (HIL) Integration (Bench Rig Track)
* **Controller:** STM32 Nucleo-F446RE executing sensor acquisition (Timers, ADC) and motor PWM control.
* **Telemetry Link:** USB-to-UART Virtual COM Port (115200 baud) streaming structured CSV frames.
* **Sensors:** Hall/Tachometer speed feedback, DC bus current/voltage monitoring, SW-420 vibration, and thermal sensing.
* **Safety Isolation:** Local emergency trips and overcurrent watchdogs remain strictly executed on the STM32 firmware layer.

---

## 3. Repository File Structure
* **`app.py`**: Streamlit interactive web dashboard containing the physics Digital Twin equations, residual extractor, plausibility checks, and live telemetry tracking charts.
* **`stimulator.py`**: Python SIL simulation harness with interactive fault injection for live verification.
* **`motor_telemetry.csv`**: Real-time data stream buffer interfacing the ingestion pipeline with the dashboard.
* **`projectlumen.pdf`**: System reference guide, wiring layouts, and communication protocol documentation.

---

## 4. Setup and Execution Guide

### Prerequisites
Install the required Python dependencies:
```bash
pip install streamlit pandas
