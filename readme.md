# OBS Monitor
A simple program that monitors your OBS sources in real time, providing speech and/or tone feedback as you hide or show them.

Note: This program uses the OBS WebSocket server to monitor the status of your sources.

## Getting Started

Step 1: In the OBS Window, press the alt key, right arrow until you find tools, use your arrow keys until you find WebSocket server settings, and press enter.

Step 2: Press tab until you find the enable WebSocket server checkbox. Press space to check this checkbox.

You can optionally add a password and change the port, the program will ask you for your connection settings at first launch.

Step 3: Press tab until you find the okay button, and press space to save your changes.

Note: If you receive any popups from Windows firewall asking you to allow the OBS WebSocket server, allow it.

## Usage

Whether running from source or as a compiled executable, run monitor.py or monitor.exe and enter your connection details.

If you choose to use default connection settings, the program will assume you want to use localhost port 4455 with no password.

Once done, the program will play a tone and/or use your screen reader to indicate a successful connection to your OBS WebSocket server.

The program also plays tones and/or uses your screen reader when it launches or exits, if a connection is lost or refused, or if an error occurs. All errors are written to an errors.log file.

Note: The program will only ask for your connection details at first launch, as all configuration settings are saved to a configuration file.

If you want to change any configuration settings, just edit the config.json file.

Since the program has an invisible interface, you can press Windows Shift F4 to exit.

##Building

To build the program from source, simply run the build script.

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Make your changes and commit them with clear and descriptive messages.
3. Push your changes to your forked repository.
4. Create a pull request.