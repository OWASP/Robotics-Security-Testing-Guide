# OWASP Robotics Security Testing Guide (RSTG)

[![OWASP Incubator](https://img.shields.io/badge/OWASP-Incubator%20Project-blue)](https://owasp.org/www-project-robotics-security-testing-guide/)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

The **OWASP Robotics Security Testing Guide (RSTG)** is an open-source effort to build a standardized, hands-on penetration testing methodology for humanoid, industrial, and autonomous robots.

Most existing security guides treat software, APIs, and AI models in digital isolation. In robotics, however, digital flaws directly translate into physical actions and safety hazards. The goal of the RSTG is to define practical ways to test this cyber-physical intersection - where compromised code, middleware, or models can manipulate physical movement, expose spatial/camera data, or bypass hardware safety limits.

## Scope & Focus Areas

- **Robotic Middleware & Protocols:** Testing methodologies for ROS/ROS 2 nodes, DDS, Zenoh, Micro-ROS, and intra-robot communications.
- **Command Authority & Arbitration:** Evaluating handover logic, teleoperation link-loss fail-safes, and single-point-of-control enforcement.
- **Perception & Sensor Integrity:** Evaluating resilience against spoofing, jamming, and blinding attacks on LiDAR, IMUs, GNSS, and optical cameras.
- **Embodied AI & VLA Models:** Testing Vision-Language-Action (VLA) models and autonomous planners against physical, visual, and kinetic prompt injections.
- **Functional Safety & Actuation:** Verifying the boundaries between software commands, kinematic/torque limits, and hardware safety controllers.

## Getting Involved

We are actively looking for robotics engineers, hardware hackers, AI researchers, and pentesters to help author and peer-review test cases.

- **Project Leader:** [Meysam Bal-afkan](https://github.com/Galaxy-sc)
- **Contributor Recognition:** All contributors to this project are officially recognized and rewarded through the [OWASP Community Recognition Tool (OWASP-CRT)](https://crt.owasp.org).

Check the Table of Contents and open Issues to pick a test case, or open a new Issue if you want to propose an addition or improvement.

## License

This project is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](LICENSE.md).
