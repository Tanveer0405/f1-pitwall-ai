import os
import json
import requests
import time

RAW_DIR = r"D:\f1-chatbot\data\raw"
os.makedirs(RAW_DIR, exist_ok=True)

BASE_URL = "https://api.jolpi.ca/ergast/f1"

print("Starting historical download...")

# Driver archive
url = f"{BASE_URL}/drivers.json?limit=2000"

r = requests.get(url)

print("Driver archive status:", r.status_code)

with open(os.path.join(RAW_DIR, "all_drivers.json"), "w", encoding="utf-8") as f:
    json.dump(r.json(), f, indent=2)

print("Saved driver archive")

# Seasons
for year in range(1950, 2026):

    print(f"Downloading {year}")

    try:

        url = f"{BASE_URL}/{year}/driverStandings.json"

        r = requests.get(url, timeout=20)

        if r.status_code == 200:

            filename = os.path.join(
                RAW_DIR,
                f"{year}_driverStandings.json"
            )

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(r.json(), f, indent=2)

            print("Saved", filename)

        else:

            print(year, "status =", r.status_code)

    except Exception as e:

        print(year, e)

    time.sleep(0.5)

print("DONE")