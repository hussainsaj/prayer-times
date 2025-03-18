import requests
import time
import datetime
from datetime import datetime
from datetime import timedelta
import schedule
import pygame
import math
import os
import socket
import yaml
import logging

def load_config():
    with open('config/config.yaml', 'r') as file:
        return yaml.safe_load(file), os.path.getmtime('config/config.yaml')

# check if the config file has been modified since last checked
def update_config(config, config_last_modified):
    if (os.path.getmtime('config/config.yaml') > config_last_modified):
        logging.info("Configuration file has been modified. Reloading configuration.")
        return load_config()
    else:
        return config, config_last_modified

def wait_for_network():
    while True:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            logging.info("Network connected.")
            break
        except OSError:
            logging.error("Network not available, waiting...")
            time.sleep(5)

def get_prayer_times(config):
    parameters = config['api']['parameters']
    api_url = f"https://api.aladhan.com/v1/timingsByCity"

    first = True
    for key, value in parameters.items():
        if first:
            api_url += f"?{key}={value}"
            first = False
        else:
            api_url += f"&{key}={value}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        schedule = {
            'Fajr': data['data']['timings']['Fajr'],
            'Dhuhr': data['data']['timings']['Dhuhr'],
            'Asr': data['data']['timings']['Asr'],
            'Maghrib': data['data']['timings']['Maghrib'],
            'Isha': data['data']['timings']['Isha']
        }

        #play athan for testing after 1 minute
        if config['settings']['testing']:
            now_plus_one = datetime.now() + timedelta(minutes=1)
            schedule['Test'] = now_plus_one.strftime('%H:%M')
        
        return schedule
    except requests.RequestException as e:
        logging.exception(f"Error fetching prayer times")
        return None

def play_sound(label, config):
    logging.info(f"Playing sound for {label}")

    try:
        source = config['adhan']['sound_files'][label]

        if not os.path.exists(source):
            raise FileNotFoundError(f"Audio file '{source}' does not exist.")

        pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=4096)
        pygame.init()
        
        athan = pygame.mixer.Sound(source)
        athan_length = math.ceil(athan.get_length() * 1000) + 1000

        athan.play()
        pygame.time.wait(athan_length)
        
        logging.info(f"Finished playing athan for {label}")

    except FileNotFoundError as e:
        logging.exception(f"Error")
    except pygame.error as e:
        logging.exception(f"Pygame error")
    except Exception as e:
        logging.exception(f"An unexpected error occurred")
    finally:
        pygame.quit()

def schedule_timings(timings, config):
    for label, timing in timings.items():
        schedule.every().day.at(timing).do(play_sound, label=label, config=config)
    logging.info("All prayer timings scheduled.")

def main():
    logging.basicConfig(
        level=logging.INFO,
        filename=f"logs/{datetime.now().strftime('%Y-%m-%d')}.log",
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filemode='w'
    )

    config, config_last_modified = load_config()
    timings = None
    timings_retrieved = False
    timings_scheduled = False
    heartbeat_interval = config['settings']['heartbeat_interval']
    last_heartbeat = time.time()
    
    wait_for_network()

    while True:
        config, config_last_modified = update_config(config, config_last_modified)

        if time.time() - last_heartbeat >= heartbeat_interval:
            logging.info("Heartbeat - System is running.")
            last_heartbeat = time.time()

        if not timings_retrieved:
            logging.info("Fetching prayer times.")
            timings = get_prayer_times(config)
            if timings:
                logging.info(f"Prayer times successfully retrieved: {timings}")
                timings_retrieved = True
            else:
                logging.error(f"Failed to retrieve prayer times. Retrying in {config['settings']['polling_rate']} seconds.")
                time.sleep(config['settings']['polling_rate'])

        elif not timings_scheduled:
            logging.info("Scheduling prayer times.")
            schedule_timings(timings, config)
            timings_scheduled = True

        schedule.run_pending()

        time.sleep(1)

if __name__ == "__main__":
    main()