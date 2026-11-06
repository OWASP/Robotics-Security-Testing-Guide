# Table of Contents

## 1. Introduction
- 1.1 Preface, Authors, and Contributors
- 1.2 Objectives and Target Audience
- 1.3 Scope and Non-Goals
- 1.4 Relationship to Other Standards (IoT, Firmware, AI, IEC 62443, ISO 10218, IEC 61508)
- 1.5 How to Use This Guide (Test Case Template, Environment and Risk Labels)

## 2. Methodology and Framework

### 2.1 Cyber-Physical Device Model & Architecture
### 2.2 Threat Modeling for Robotic Systems
  - 2.2.1 Attacker Model and Trust Boundaries
  - 2.2.2 Mapping to ATT&CK for ICS and OWASP Top 10 for Robotics
### 2.3 Cyber-Physical Rules of Engagement and Kinetic Containment
### 2.4 Testing Methodology and Dual-Scoring (CVSS/RVSS)
### 2.5 Reproducible Flaw Packaging and Containerized Testbeds

## 3. Robotics Security Testing

### 3.1 Information Gathering
  - 3.1.1 OSINT, Vendor Documentation, and Supply Chain
  - 3.1.2 Physical Port and Sensor Suite Enumeration
  - 3.1.3 Network Service and API Footprinting
  - 3.1.4 Middleware Computational Graph Introspection
  - 3.1.5 Firmware and Software Artifact Fingerprinting

### 3.2 Configuration and Deployment
  - 3.2.1 OS Hardening, Multi-Tenant Isolation, and Container Escapes
  - 3.2.2 SROS2 and Zenoh Security Policy and Keystore Auditing
  - 3.2.3 Certificate Authority Chain-of-Trust Validation
  - 3.2.4 Network Segmentation and Safety Conduit Isolation
  - 3.2.5 Tamper Logging and Component Integrity Verification
  - 3.2.6 Wireless Provisioning and Onboarding (BLE, Wi-Fi, Pairing)

### 3.3 Robotics Middleware and IPC
  - 3.3.1 ROS 1 Framework
  - 3.3.2 ROS 2 Framework
  - 3.3.3 Data Distribution Service
  - 3.3.4 Alternative Middleware (Zenoh, Micro-ROS)

### 3.4 Application and User Interfaces
  - 3.4.1 Web Dashboards, Fleet APIs, and Companion Apps
  - 3.4.2 Rosbridge and WebSocket Gateways
  - 3.4.3 Telemetry, Camera, and SLAM Map Exposure
  - 3.4.4 Industrial Teach Pendants and Control Boxes

### 3.5 Multi-Modal Perception and Sensor Transduction
  - 3.5.1 Acoustic Resonance Transduction Attacks on MEMS IMUs
  - 3.5.2 3D LiDAR Point-Cloud Spoofing, Relay, and Saturation
  - 3.5.3 Optical Camera Adversarial Patches and Invisible IR Injection
  - 3.5.4 GNSS/GPS SDR Spoofing and Lateral Trajectory Deviation
  - 3.5.5 Multi-Sensor Fusion and Software Virtual Sensor Recovery Auditing

### 3.6 Embodied AI, VLA Models, and Autonomous Planning
  - 3.6.1 Scene-Conditioned Physical Indirect Prompt Injection
  - 3.6.2 Direct Multimodal Jailbreaking and Adversarial Suffix Optimization
  - 3.6.3 VLA Fine-Tuning Data Poisoning and 3D Environmental Triggers
  - 3.6.4 Temporal Action-Chunk Backdoor Testing
  - 3.6.5 LLM-to-Middleware Structured Backdoors and Runtime Guardrail Verification

### 3.7 Functional Safety and Actuation
  - 3.7.1 Safety Controllers (Safety PLC)
  - 3.7.2 Actuator and Cobot Limits (Speed, Force, Torque)
  - 3.7.3 Runtime Invariants and Safety-Security Conflict Auditing

### 3.8 Command Authority and Arbitration
  - 3.8.1 Command Source Inventory (AI Planner, Teleoperation, Teach Pendant, Fleet API, Scripts)
  - 3.8.2 Teleoperation Channel Security (Session Hijacking, Command Replay, Operator Feed Spoofing)
  - 3.8.3 Authority Arbitration and Conflicting Commands (AI vs. Human, Operator vs. Operator)
  - 3.8.4 Authority Handover and Link-Loss Fail-Safe Behavior
  - 3.8.5 Authority Escalation Across Command Sources

## 4. Planned for v1.1 and Later
  - 4.1 Hardware and Firmware: Internal Buses, Physical Interfaces, Bootloader and Updates
  - 4.2 Industrial Networks and Fieldbus: TSN, PTP, EtherCAT, Modbus/PROFINET/EtherNet-IP
  - 4.3 Cloud Telemetry and Digital Twins
