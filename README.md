# The Dark Room - Terminal Access

A 3D hacking exploration game built with the Ursina Engine.

> [!WARNING]
> **Maintenance Notice:** This project is archived and is no longer being maintained. It is provided as-is for educational or historical purposes.

## Overview

In *The Dark Room - Terminal Access*, you play as a hacker in a sprawling low-poly city. Your goal is to navigate the urban landscape, find vulnerable cafe networks, crack their passwords using your portable terminal, and submit them for anonymous payments. Watch out for the authorities, as hacking in public spaces can attract unwanted attention.

## Features

- **3D Exploration:** Explore a procedurally generated city with a working elevator and a rideable bicycle.
- **Hacking Simulation:** Use an in-game terminal with commands like `nscan`, `npass`, and `nsubmit`.
- **Smartphone UI:** Access maps and job listings through an interactive in-game phone.
- **Suspicion System:** Hacking near cafe staff increases your suspicion level. If caught, the police will pursue and arrest you.
- **Economy:** Earn money from successful hacks to potentially buy items (like cars from the local dealership).

## Controls

- **WASD:** Move
- **E:** Interaction / Action (Open doors, ride bike, use laptop/phone)
- **F:** Toggle Smartphone
- **T:** Use Terminal (when holding laptop)
- **ESC:** Exit Terminal / Pause

## Requirements

- Python 3.x
- Ursina Engine (`pip install ursina`)

## Installation

1. Clone the repository.
2. Install the requirements:
   ```bash
   pip install ursina
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
