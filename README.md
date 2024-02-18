# IoT-Platform

## Platform Deployment

The platform can be easily deployed on any machine using containers. Follow the steps below:

1. Copy the `tools` folder and all its contents to the machine where the platform will run.

2. If the machine is running a Linux distribution without Docker installed, you can run the `install_docker.sh` script located in `tools/docker`.

3. Once Docker is installed, start the service by running the following command in the terminal:

   ```bash
   docker-compose up -d
   ```

The platform's interface will be accessible through port `1250`

## Initialization

If you want to perform an example initialization, you can run the .py scripts included in the entities_initialization folder. These scripts create 5 entities in the Context Broker: 4 thermostats and 1 weather station.
Make sure to have Python 3 installed along with the necessary packages listed in `requirements_01-02.txt`:

   ```bash
   pip install --no-cache-dir -r requirements_01-02.txt
   python3 01create_entities.py
   python3 02time_series_subscription.py
   ```

## Fetch data

In the folder `fetch_data` there is an script, `03airzone-station_to_orion_no_loop.py` to fetch data for the 4 thermostats and the weather station.
Make sure to you have necessary packages listed in `requirements_03.txt`:

   ```bash
   pip install --no-cache-dir -r requirements_03.txt
   python3 03airzone-station_to_orion_no_loop.py
   ```

If you want to fetch data every 5 minutes, there is an script, `cron_fetch_data.sh` located in `tools/fetch_data` that installs the needed libraries and creates a cron job that executes `03airzone-station_to_orion_no_loop.py` every 5 minutes.

## Import data

If you want to import data to the platform, there is an sqlite database, `api_data.db` located in `import_data/data`.
Execute `update_cratedb_thermostats.py` to import historic data for the 4 thermostats, and `update_cratedb_station.py` for the weather station. The historic data ranges from July23 to February24.
Make sure to you have necessary packages listed in `requirements_crate.txt`:

   ```bash
   pip install --no-cache-dir -r requirements_crate.txt
   python3 update_cratedb_thermostats.py
   python3 update_cratedb_station.py
   ```
