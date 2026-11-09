# Table of Contents

## 1. Introduction
- 1.1 Preface, Authors, and Contributors
- 1.2 Objectives and Target Audience
- 1.3 Scope and Non-Goals
- 1.4 Relationship to Other Standards
- 1.5 How to Use This Guide

## 2. Methodology and Framework
### 2.1 Cyber-Physical Device Model and Architecture
### 2.2 Threat Modeling for Robotic Systems
  - 2.2.1 Attacker Model and Trust Boundaries
  - 2.2.2 Mapping to ATT&CK for ICS and OWASP Robotics Top 10
### 2.3 Rules of Engagement and Kinetic Containment
### 2.4 Testing Methodology and Dual-Scoring
### 2.5 Reproducible Flaw Packaging and Containerized Testbeds

## 3. Robotics Security Testing

### 3.1 Information Gathering (`RSTG-INFO`)
- 3.1.1 OSINT, Vendor Documentation, and Supply Chain
- 3.1.2 Physical Port and Sensor Suite Enumeration
- 3.1.3 Network Service and API Footprinting
- 3.1.4 Middleware Computational Graph Introspection
- 3.1.5 Firmware and Software Artifact Fingerprinting

### 3.2 Configuration and Deployment (`RSTG-CONF`)
- 3.2.1 OS Hardening and Container Isolation
- 3.2.2 SROS2 and Zenoh Security Policy Auditing
- 3.2.3 Certificate Authority Chain-of-Trust Validation
- 3.2.4 Network Segmentation and Safety Conduit Isolation
- 3.2.5 Tamper Logging and Component Integrity Verification

### 3.3 Robotics Middleware and IPC (`RSTG-MIDW`)
- 3.3.1 ROS 1 Framework
- 3.3.2 ROS 2 Framework
- 3.3.3 Data Distribution Service (DDS)
- 3.3.4 Alternative Middleware (Zenoh and Micro-ROS)

### 3.4 Application and User Interfaces (`RSTG-APPL`)
- 3.4.1 Web Dashboards, Fleet APIs, and Companion Apps
- 3.4.2 Rosbridge and WebSocket Gateways
- 3.4.3 Telemetry, Camera, and SLAM Map Exposure
- 3.4.4 Industrial Teach Pendants and Control Boxes

### 3.5 Perception and Sensor Security (`RSTG-SENS`)
- 3.5.1 MEMS IMU Acoustic Resonance Attacks
- 3.5.2 3D LiDAR Point-Cloud Spoofing and Saturation
- 3.5.3 Optical Camera Adversarial Patches and IR Injection
- 3.5.4 GNSS and GPS Spoofing
- 3.5.5 Multi-Sensor Fusion and Virtual Sensor Auditing

### 3.6 Embodied AI and Autonomous Planning (`RSTG-EMAI`)
- 3.6.1 Physical Indirect Prompt Injection
- 3.6.2 Multimodal Jailbreaking and Adversarial Inputs
- 3.6.3 VLA Data Poisoning and Environmental Triggers
- 3.6.4 Temporal Action-Chunk Backdoor Testing
- 3.6.5 LLM-to-Middleware Structured Backdoors and Runtime Guardrail Verification

### 3.7 Functional Safety and Actuation (`RSTG-SAFE`)
- 3.7.1 Safety Controllers and Safety PLCs
- 3.7.2 Actuator and Cobot Kinematic Limits
- 3.7.3 Runtime Invariants and Safety-Security Conflicts

## 4. Planned for v1.1 and Later
- 4.1 Hardware and Firmware Security
- 4.2 Industrial Networks and Fieldbus Protocols
- 4.3 Cloud Telemetry and Digital Twins
