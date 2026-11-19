# Command Authority and Arbitration Overview

Many robots accept motion commands from more than one source, such as a navigation stack, an AI planner, a remote teleoperator, a teach pendant, and a fleet management system. The test cases in this section examine which source is allowed to move the robot at any moment, how control passes between sources, and what the robot does when a source fails or loses its link.

## Glossary

Terms used across the test cases in this section:

- A **command source** is any component that can send motion commands to the robot.
- An **arbitration layer** decides which command source is in control at any moment, such as a command multiplexer or a mode switch.
- A **transition** is any change affecting the source in control: a planned handover from one source to another, or an unplanned event such as losing the link to the source in control, whether or not another source then takes over.
- The **expected behavior** is what the target's specification says should happen at each transition.
- An **enabling control** (also called a deadman control) is a control the operator must hold for motion to be allowed; releasing it should stop motion.
- A **liveness check** detects that a source has stopped communicating, such as a timeout that triggers when no messages arrive.
- A **downstream timeout** is a timeout in a component closer to the actuators than the arbiter, such as a motor controller, that stops the robot when commands stop arriving.
