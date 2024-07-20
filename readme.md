
# Meta Terminal 3.1

Forked from [Meta Terminal III](https://github.com/Meta-Team/Meta-Terminal-III), Meta Terminal 3.1 is a graphical user interface (GUI) application designed for interacting with various devices via serial, TCP, and Bluetooth connections. The application provides functionalities to send commands, display terminal output, and plot data received from the devices.

## Features

- Connect to devices via Serial, TCP, or Bluetooth.
- Send commands to connected devices.
- Display terminal output in real-time.
- Plot data received from devices in real-time.

## Requirements

- Python 3.6+
- PyQt5
- pyhocon
- matplotlib

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/h4nty/meta-terminal-3.1.git
   cd meta-terminal-3.1
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Use the GUI to connect to a device:
   - Select the connection method (Serial or TCP) from the dropdown.
   - Enter the port or device address.
   - Click "Connect".

3. Send commands to the connected device:
   - Enter the command in the text box at the bottom.
   - Click "Send".

4. Clear the terminal display by clicking the "Clear" button.

5. View the plotted data on the right side of the window.

## File Overview

- `main.py`: The main entry point of the application. Sets up the GUI and handles user interactions.
- `device.py`: Manages device connections and communication for Serial, TCP, and Bluetooth methods.
- `chart_widget.py`: Manages the creation and updating of charts for plotting data received from devices.

## Removed Features

- The parameter modifier functionality has been removed.
- The configuration save and load features have been removed.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any improvements or bug fixes.

