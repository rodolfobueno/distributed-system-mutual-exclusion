# Token Ring Algorithm (with Failure Recovery)

This project implements a Token Ring algorithm in Python, simulating distributed mutual exclusion with basic failure recovery. Each process communicates over TCP sockets, passing a token to control access to a critical section.

## Features

- Token Ring mutual exclusion
- Randomized critical section entry
- Basic failure recovery: skips failed nodes

## Project Structure

- `basic/`: Basic token ring scripts
- `failure_recovery/`: Enhanced version with failure recovery
- `main.py`: Main script for running a node
- `start_first.sh`, `start_second.sh`: Example scripts to start nodes

## Requirements

- Python 3.x

## Usage

1. **Clone the repository** and navigate to the project directory.

2. **Start nodes** using the provided scripts or manually:

   ```bash
   cd basic
   ./start_first.sh
   ./start_second.sh