import requests
import time
from datetime import datetime
import schedule

API_URL = 'https://api.aladhan.com/v1/timingsByCity?city=Stoke-on-Trent&country=United%20Kingdom'
HEARTBEAT_INTERVAL = 600  # 10 minutes

def get_prayer_times():
    #Fetch prayer times from the Aladhan API.
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return {
            'Fajr': data['data']['timings']['Fajr'],
            'Dhuhr': data['data']['timings']['Dhuhr'],
            'Asr': data['data']['timings']['Asr'],
            'Maghrib': data['data']['timings']['Maghrib'],
            'Isha': data['data']['timings']['Isha']
        }
    except requests.RequestException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Error fetching prayer times: {e}")
        return None

def play_sound(label):
    #Simulate playing a sound for a prayer time.
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Playing sound for {label}")

def schedule_timings(timings):
    #Schedule tasks to play sounds at specified prayer times.
    for label, timing in timings.items():
        schedule.every().day.at(timing).do(play_sound, label=label)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: All prayer timings scheduled.")

def main():
    timings = None
    timings_retrieved = False
    timings_scheduled = False
    last_heartbeat = time.time()

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