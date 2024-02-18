#!/bin/bash

# Instalar los requisitos
sudo pip install --no-cache-dir -r requirements_03.txt

# Crear la tarea en crontab
(crontab -l ; echo "*/5 * * * * /usr/bin/python3 /home/iot-platform/tools/fetch_data/03airzone-station_to_orion_no_loop.py") | crontab -
