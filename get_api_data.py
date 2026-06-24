import os
import json
import requests

# Ensure target directory exists
os.makedirs(os.path.join("data", "raw"), exist_ok=True)

# 2024 Round 8 was the Monaco Grand Prix
YEAR = "2024"
ROUND = "8"
BASE_URL = "https://api.jolpi.ca/ergast/f1"

endpoints = {
    "race_results": f"/{YEAR}/{ROUND}/results.json",
    "qualifying": f"/{YEAR}/{ROUND}/qualifying.json",
    "driver_standings": f"/{YEAR}/driverStandings.json",
    "constructor_standings": f"/{YEAR}/constructorStandings.json"
}

def fetch_and_save():
    for name, path in endpoints.items():
        url = f"{BASE_URL}{path}"
        print(f"Fetching {name} from {url}...")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                filename = os.path.join("data", "raw", f"{YEAR}_monaco_{name}.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(response.json(), f, indent=2)
                print(f"✓ Saved to {filename}")
            else:
                print(f"✗ Failed to fetch {name}: Status {response.status_code}")
        except Exception as e:
            print(f"✗ Error fetching {name}: {e}")

if __name__ == "__main__":
    fetch_and_save()