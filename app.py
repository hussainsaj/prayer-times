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

HEARTBEAT_INTERVAL = 600  # 10 minutes
LOCATION = {
    'city': 'Stoke-on-Trent',
    'country': 'United Kingdom'
}
API_URL = f"https://api.aladhan.com/v1/timingsByCity?city={LOCATION['city']}&country={LOCATION['country']}&latitudeAdjustmentMethod=2"

def wait_for_network():
    # Function to check network connectivity
    while True:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Network connected.")
            break
        except OSError:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Network not available, waiting...")
            time.sleep(5)

def get_prayer_times():
    # Fetch prayer times from the Aladhan API.
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        #for testing purposes
        #now_plus_two = datetime.now() + timedelta(minutes=2)
        
        return {
            'Fajr': data['data']['timings']['Fajr'],
            'Dhuhr': data['data']['timings']['Dhuhr'],
            'Asr': data['data']['timings']['Asr'],
            'Maghrib': data['data']['timings']['Maghrib'],
            'Isha': data['data']['timings']['Isha']
            #,'Test': now_plus_two.strftime('%H:%M')
        }
    except requests.RequestException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Error fetching prayer times: {e}")
        return None

def play_sound(label):
    # Play sound for a prayer time.
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Playing sound for {label}")

    try:
        source = None

        if label == 'Fajr':
            source = 'audio/f.wav'
        else:
            source = 'audio/a.wav'

        if not os.path.exists(source):
            raise FileNotFoundError(f"Audio file '{source}' does not exist.")

        pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=4096, devicename=None)
        pygame.init()
        
        athan = pygame.mixer.Sound(source)
        athan_length = math.ceil(athan.get_length() * 1000) + 1000

        athan.play()
        pygame.time.wait(athan_length) #wait till the athan is finished before closing the programme
        
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Finished playing athan for {label}")

    except FileNotFoundError as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Error: {e}")
    except pygame.error as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Pygame error: {e}")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: An unexpected error occurred: {e}")
    finally:
        try:
            pygame.display.quit()
            pygame.quit()
        except pygame.error as e:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Error during pygame cleanup: {e}")

def schedule_timings(timings):
    # Schedule tasks to play sounds at specified prayer times.
    for label, timing in timings.items():
        schedule.every().day.at(timing).do(play_sound, label=label)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: All prayer timings scheduled.")

def main():
    timings = None
    timings_retrieved = False
    timings_scheduled = False
    last_heartbeat = time.time()
    
    wait_for_network()

    while True:
        time.sleep(1)

        # Heartbeat logging
        if time.time() - last_heartbeat >= HEARTBEAT_INTERVAL:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Heartbeat - System is running.")
            last_heartbeat = time.time()

        # Fetch and schedule prayer times
        if not timings_retrieved:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Fetching prayer times.")
            timings = get_prayer_times()
            if timings:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Prayer times successfully retrieved: {timings}")
                timings_retrieved = True
            else:
                print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Failed to retrieve prayer times. Retrying in 1 minute.")
                time.sleep(60)  # Retry after a short delay

        elif not timings_scheduled:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Scheduling prayer times.")
            schedule_timings(timings)
            timings_scheduled = True

        # Run scheduled tasks
        schedule.run_pending()

if __name__ == "__main__":
    main()