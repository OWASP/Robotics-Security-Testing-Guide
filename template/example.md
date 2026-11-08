# Test Case Name
*(e.g., ROS 2 Discovery Flooding & Amplification)*

|ID          |
|------------|
|RSTG-NAME-ID|

## Summary

A brief description (1-2 paragraphs) of what this test evaluates, the vulnerability mechanism, and the potential impact on the robotic system.

> [!CAUTION]
> **KINETIC RISK:** (Optional - Include this box ONLY if executing this exploit on physical hardware poses a risk of unintended robot movement, environmental damage, or human injury. Detail the required physical safety measures here.)

> [!NOTE]
> **Important Note:** (Optional - Use this box for general testing limitations, environment requirements, or specific firmware versions).

## Test Objectives

- Objective 1 (e.g., Identify unauthenticated ROS 2 topics).
- Objective 2 (e.g., Inject spoofed telemetry to manipulate actuator control).

## Hardware & Environment Requirements

- **Physical Components:** (Required hardware, e.g., Optical Camera, Actuator/Motor, JTAG interface, or Safety PLC).
- **Testing Tools:** (Software/Hardware tools required by the tester, e.g., ROSploit, Nmap, SDR Hardware, can-utils).
- **Simulation / Software:** (Alternative virtual environments, e.g., Gazebo simulator, digital twins, or specific Docker images).

## How to Test

### Safe Verification (Indicators of Vulnerability):**

Read this BEFORE executing exploits. Explain how the tester can confirm the exploit was successful *without* triggering a dangerous physical response. (e.g., "Start monitoring the `/cmd_vel` ROS topic for state changes, or look for specific error codes in `syslog`, rather than allowing the robot to physically move").

### Black-Box / Passive Analysis:

Methods for information gathering and network/physical environment sniffing without initial access (e.g., intercepting DDS traffic or identifying open ports).

### Gray-Box / Active Exploitation:

Payload injection, terminal commands, and exploit scripts. (Include actual code snippets, commands, and expected terminal outputs).

### White-Box / Source Code Analysis:

Reviewing source code, configuration files (e.g., ROS `launch` files or `permissions.xml`), firmware reverse engineering, and static analysis to identify flaws.
  
## Remediation

- **Vendor / Developer:** Actions required by the manufacturer or software team (e.g., source code fixes, implementing middleware encryption, hardware design changes, or issuing security patches).
- **Operator / Integrator:** Actions required by the end-user, facility owner, or deployment team (e.g., OT/IT network segmentation, firewall configuration, physical access restrictions, or VPN implementation).

## Related Test Cases

- [RSTG-NAME-ID](link_to_file.md) - Name of Related Test Case
- [RSTG-NAME-ID](link_to_file.md) - Name of Related Test Case

## References

- Links to related CVEs or RVD (Robot Vulnerability Database) entries.
- Relevant academic papers and industry standards (e.g., ISO 10218, IEC 62443).
