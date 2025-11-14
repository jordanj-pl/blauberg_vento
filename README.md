Blauberg Vento HRVs integration with Home Assistant.
# Features
- Speed control (low, medium, high)
- Mode (supply, ventilate, heat recovery) - please be aware that supply and ventilate may work differently than expected. Dependently on dip switch setting within certain hardware the unit can ventilate or supply air if any of those features is selected.
- Internal Clock synchronisation
- Alarm reset
- Filter cleaning message and reset.
- Humidity sensor.
- Diagnostic
  - Battery voltage
  - Device ID
  - Fan 1 speed
  - Fan 2 speed (if applicable e.g. Blauberg Ventor Duo)
  - IP Address
  - Machine hours

This integration has been tested with Blauberg Vento inHome WiFi.

# Installation
1. Download ZIP and copy folder blauberg_vento into /config/custom_components of your Home Assistant instance.
2. Restart HA.

# Configuration
1. Got to Settings -> Devices & services, click on Add Integration and search for Blauberg Vento.
2. Enter your device name and IP address. Default port is 4000 and default password is 1111. If your devices has custom configuration please change the settings. If you know Device ID you can enter, otherwise it will be retrieved during initial communication.

