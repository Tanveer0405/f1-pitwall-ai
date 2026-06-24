import os
import json
import time
import requests

# FORCE target directory explicitly to the D: drive project folder
RAW_DIR = r"D:\f1-chatbot\data\raw"
os.makedirs(RAW_DIR, exist_ok=True)

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def download_everything():
    print("====================================================")
    print("STARTING COMPLETE HISTORICAL DOWNLOAD (2018-2025)")
    print("====================================================")
    
    # 1. Complete Driver Index (Historical Profile Data)
    print("\n[1/3] Fetching global historical driver profiles...")
    try:
        res = requests.get(f"{BASE_URL}/drivers.json?limit=2000", timeout=15)
        if res.status_code == 200:
            with open(os.path.join(RAW_DIR, "all_historical_drivers.json"), "w", encoding="utf-8") as f:
                json.dump(res.json(), f, indent=2)
            print("  ✓ Saved all_historical_drivers.json")
    except Exception as e:
        print(f"  ✗ Failed to download driver profiles: {e}")

    # Modern era window to get comprehensive championship and race data
    start_year = 2018
    end_year = 2025

    # 2. Standings Archive Loop
    print(f"\n[2/3] Fetching Championship Standings ({start_year}-{end_year})...")
    for year in range(start_year, end_year + 1):
        for standings_type in ["driverStandings", "constructorStandings"]:
            url = f"{BASE_URL}/{year}/{standings_type}.json"
            print(f"  -> Requesting: {year} {standings_type}...")
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    filename = os.path.join(RAW_DIR, f"{year}_{standings_type}.json")
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(response.json(), f, indent=2)
                time.sleep(0.3) # Polite delay for API limits
            except Exception as e:
                print(f"  ✗ Error fetching {year} {standings_type}: {e}")

    # 3. Individual Race Results Loop (Who won which Grand Prix)
    print(f"\n[3/3] Fetching Grand Prix Race Results ({start_year}-{end_year})...")
    for year in range(start_year, end_year + 1):
        url = f"{BASE_URL}/{year}/results.json?limit=500"
        print(f"  -> Requesting: {year} Individual Race Results...")
        try:
            response = requests.get(url, timeout=12)
            if response.status_code == 200:
                filename = os.path.join(RAW_DIR, f"{year}_raceResults.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(response.json(), f, indent=2)
                print(f"    ✓ Saved {year}_raceResults.json")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ✗ Error fetching {year} race results: {e}")

    print("\n====================================================")
    print("PHASE 1 COMPLETE: All historical data safely stored on D: Drive!")
    print("====================================================")

if __name__ == "__main__":
    download_everything()