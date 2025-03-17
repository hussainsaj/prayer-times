# Prayer Times Application

## Overview
The Prayer Times application is designed to fetch and play adhan sounds at specified prayer times based on the user's location. It utilizes the Aladhan API to retrieve prayer timings and schedules sound playback accordingly.

## Project Structure
```
prayer-times
├── config
│   └── config.yaml
├── src
│   ├── app.py
├── README.md
├── launcher.sh
└── requirements.txt
```

## Configuration
The application settings are stored in `config/config.yaml`. This file includes:
- API URL parameters for fetching prayer times including location
- Sound file paths for different adhan types
- Heartbeat intervals for logging
- Polling rates for fetching prayer times

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/hussainsaj/prayer-times
   cd prayer-times
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python src/app.py
```

The application will wait for network connectivity, fetch prayer times, and schedule the playback of adhan sounds at the appropriate times.

To add the application to run on boot on a raspberry pi follow these steps:
1. Add the job in the crontab:
   ```
   sudo crontab -e
   ```

2. Add the job so it runs the application on boot
   ```
   @reboot /home/hussain/Desktop/prayer-times/launcher.sh
   ```

3. Save and give permission to launcher.sh
   ```
   chmod +x launcher.sh
   ```

## Testing
The application can be tested by modifying the configuration file to simulate different locations and prayer times. Ensure that the sound files are available in the specified paths.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.