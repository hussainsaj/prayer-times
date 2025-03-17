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

def load_config():
    with open('config/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def wait_for_network():
    while True:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Network connected.")
            break
        except OSError:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Network not available, waiting...")
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
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Error fetching prayer times: {e}")
        return None

def play_sound(label, config):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Playing sound for {label}")

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
        
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Finished playing athan for {label}")

    except FileNotFoundError as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Error: {e}")
    except pygame.error as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Pygame error: {e}")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: An unexpected error occurred: {e}")
    finally:
        pygame.quit()

def schedule_timings(timings, config):
    for label, timing in timings.items():
        schedule.every().day.at(timing).do(play_sound, label=label, config=config)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: All prayer timings scheduled.")

def main():
    config = load_config()
    timings = None
    timings_retrieved = False
    timings_scheduled = False
    heartbeat_interval = config['settings']['heartbeat_interval']
    last_heartbeat = time.time()
    
    wait_for_network()

    while True:
        time.sleep(1)

        if time.time() - last_heartbeat >= heartbeat_interval:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Heartbeat - System is running.")
            last_heartbeat = time.time()

        if not timings_retrieved:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Fetching prayer times.")
            timings = get_prayer_times(config)
            if timings:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Prayer times successfully retrieved: {timings}")
                timings_retrieved = True
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Failed to retrieve prayer times. Retrying in {config['settings']['polling_rate']} seconds.")
                time.sleep(config['settings']['polling_rate'])

        elif not timings_scheduled:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Scheduling prayer times.")
            schedule_timings(timings, config)
            timings_scheduled = True

        schedule.run_pending()

if __name__ == "__main__":
    main()