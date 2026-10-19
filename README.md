# OWASP Robotics Security Testing Guide (RSTG)

[![OWASP Incubator](https://img.shields.io/badge/OWASP-Incubator%20Project-blue)](https://owasp.org/www-project-robotics-security-testing-guide/)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

The **OWASP Robotics Security Testing Guide (RSTG)** is an open-source effort to build a standardized penetration testing methodology for humanoid, industrial, and autonomous robots.

Most existing security guides treat software, APIs, and AI models in digital isolation. In robotics, however, digital flaws directly translate into physical actions and safety hazards. The goal of the RSTG is to define practical ways to test this cyber-physical intersection - where compromised code, middleware, or models can manipulate physical movement, expose spatial/camera data, or bypass hardware safety limits.

## Scope & Focus Areas

* **Core Risk Taxonomy (OWASP Robotics Top 10):** Defining the top ten security and physical safety risks in robotics to structure our testing chapters.
* **Robotic Middleware & Protocols:** Testing methodologies for ROS/ROS2 nodes, DDS, CAN bus, and intra-robot communications.
* **Sensor Integrity:** Evaluating resilience against spoofing, jamming, and blinding attacks on LiDAR, ultrasonic sensors, IMUs, and depth cameras.
* **Embodied AI & VLA Models:** Testing Vision-Language-Action (VLA) models against physical, visual, and kinetic prompt injections.
* **Actuation & Hardware Safety Overrides:** Verifying the boundaries between software commands, joint torque limits, and hardware Emergency Stops (E-Stops).

## Current Status & Roadmap

The project is currently in **Phase 1 (R&D & Taxonomy Definition)**. 

1. **Phase 1 (Current):** Researching robotic attack vectors, defining the guide's table of contents, and drafting the initial Robotics Top 10 risk categories.
2. **Phase 2:** Writing the foundational testing scenarios for ROS/ROS2 architectures and cyber-physical translation.
3. **Phase 3:** Expanding test cases into sensor manipulation, VLA models, and hardware safety overrides through community peer review.

## Getting Involved

We are actively looking for robotics engineers, hardware hackers, AI researchers, and pentesters to help review the initial taxonomy and draft testing scenarios. 

* **Project Leader:** [Meysam Bal-afkan](https://github.com/Galaxy-sc)
* **Project Page:** [OWASP RSTG on owasp.org](https://owasp.org/www-project-robotics-security-testing-guide/)

Contribution guidelines (`CONTRIBUTING.md`) and the initial v0.1 taxonomy draft will be added to the repository soon. Feel free to open an issue or reach out via email if you want to collaborate.

## License

This project is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](LICENSE.md).
