import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Directory mappings explicitly focused on your D: drive storage
RAW_DIR = r"D:\f1-chatbot\data\raw"
PROCESSED_DIR = r"D:\f1-chatbot\data\processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def parse_raw_file(file_path):
    """Parses structural JSON indexes or pulls raw scraped text files into clean semantic string data."""
    filename = os.path.basename(file_path)
    
    # 1. Handle Unstructured Scraped Text Narratives (Monaco, Engines, Indian GP)
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # 2. Handle Structured API JSON files
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return ""
        
    narrative_lines = []
    try:
        # A. Parse Modern Individual Race Results (2018-2025)
        if "raceResults" in filename:
            races = data["MRData"]["RaceTable"]["Races"]
            for race in races:
                race_name = race["raceName"]
                season = race["season"]
                round_num = race["round"]
                for res in race["Results"]:
                    pos = res["position"]
                    driver = f"{res['Driver']['givenName']} {res['Driver']['familyName']}"
                    constructor = res["Constructor"]["name"]
                    points = res["points"]
                    grid = res["grid"]
                    status = res["status"]
                    
                    line = f"In the {season} Formula 1 season, Round {round_num} was the {race_name}. Driver {driver} driving for {constructor} finished in position {pos}. Started from grid position {grid}. Status: {status}. Points awarded: {points}."
                    narrative_lines.append(line)
        
        # B. Parse Driver Standings (1950-Present)
        elif "driverStandings" in filename:
            standings_list = data["MRData"]["StandingsTable"]["StandingsLists"][0]
            season = standings_list["season"]
            for ds in standings_list["DriverStandings"]:
                pos = ds["position"]
                points = ds["points"]
                wins = ds["wins"]
                driver_name = f"{ds['Driver']['givenName']} {ds['Driver']['familyName']}"
                constructor = ds["Constructors"][0]["name"] if ds.get("Constructors") else "Unknown Team"
                
                line = f"Championship Standings: In the {season} Formula 1 World Championship, driver {driver_name} driving for {constructor} finished in final rank {pos} with {points} points and {wins} race victories."
                narrative_lines.append(line)
                
        # C. Parse Constructor Standings (1950-Present)
        elif "constructorStandings" in filename:
            standings_list = data["MRData"]["StandingsTable"]["StandingsLists"][0]
            season = standings_list["season"]
            for cs in standings_list["ConstructorStandings"]:
                pos = cs["position"]
                points = cs["points"]
                wins = cs["wins"]
                constructor_name = cs["Constructor"]["name"]
                
                line = f"Championship Standings: In the {season} Formula 1 World Championship, constructor {constructor_name} finished in final standing position {pos} with {points} points and {wins} total race victories."
                narrative_lines.append(line)

        # D. Parse Driver Profile Records
        elif "all_historical_drivers" in filename:
            drivers = data["MRData"]["DriverTable"]["Drivers"]
            for d in drivers:
                name = f"{d['givenName']} {d['familyName']}"
                dob = d.get("dateOfBirth", "unknown date")
                nat = d.get("nationality", "")
                line = f"Formula 1 Driver Profile: {name}, Nationality: {nat}, Date of Birth: {dob}."
                narrative_lines.append(line)

    except (IndexError, KeyError, TypeError):
        # Fail gracefully if an individual API object misses a specific property
        pass
        
    return "\n".join(narrative_lines)

def run_pipeline():
    all_chunks = []
    
    # 800 character chunk sizes (~150-200 words) maintain single-row lookup purity.
    # 100 character overlap preserves context at the cut borders.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        length_function=len
    )
    
    print("\n--- STARTING GLOBAL DATA CHUNKING PROCESS ---")
    all_files = [f for f in os.listdir(RAW_DIR) if f.endswith((".json", ".txt"))]
    print(f"Processing {len(all_files)} total files inside data\\raw...")

    for file_name in all_files:
        file_path = os.path.join(RAW_DIR, file_name)
        file_type = "technical_text" if file_name.endswith(".txt") else "championship_json"
        
        processed_text = parse_raw_file(file_path)
        
        if processed_text:
            chunks = text_splitter.create_documents(
                texts=[processed_text], 
                metadatas=[{"source": file_name, "type": file_type}]
            )
            all_chunks.extend(chunks)

    # Wrap up outputs cleanly into serializable dictionary formats
    output_payload = [{"text": chunk.page_content, "metadata": chunk.metadata} for chunk in all_chunks]
    output_file = os.path.join(PROCESSED_DIR, "master_f1_chunks.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)
        
    print("\n====================================================")
    print(f"SUCCESS! Created {len(all_chunks)} unique searchable knowledge assets.")
    print(f"Master file compiled to: {output_file}")
    print("====================================================")

if __name__ == "__main__":
    run_pipeline()