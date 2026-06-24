import os
import requests

# Path configuration focused explicitly on your D: drive storage
RAW_DIR = r"D:\f1-chatbot\data\raw"
os.makedirs(RAW_DIR, exist_ok=True)

# Maximum-scale unified catalog mapping mechanics, components, aerodynamics, and tracking channels
F1_TOPICS = {
    # 1. THE PHYSICS OF FLUID DYNAMICS & SPEED
    "f1_aerodynamics_ground": "Ground_effect_(cars)",       # Venturi tunnels, floor sealing, porpoising
    "f1_aerodynamics_drs": "Drag_reduction_system",         # Active wing aerodynamics and stall mechanics
    "f1_car_anatomy": "Formula_One_car",                    # Component layouts, monocoque, weight distributions
    "f1_open_wheel": "Open-wheel_car",                      # Dynamics of exposed rotating tyre wakes
    "f1_tyres_pneumatic": "Tyre",                           # General compound mechanical slip angles and friction
    "f1_tyres_racing": "Formula_One_tyres",                 # Thermal blankets, marbles, track temperature impact
    "f1_circuits_design": "Formula_One_circuits",           # Track safety barriers and curb physics
    
    # 2. POWERTRAIN, TRANSMISSION & DETAILED COMPONENTS
    "f1_engines_hybrid": "Formula_One_engines",             # V6 ICE, Turbo, MGU-K, MGU-H architectures
    "f1_internal_combustion": "Internal_combustion_engine", # Piston architecture, thermal cycles, and fuel maps
    "f1_transmissions": "Semi-automatic_transmission",      # Seamless shift gearboxes and paddles
    "f1_clutches": "Clutch",                                # Electro-hydraulic carbon multi-plate layouts
    "f1_suspension_geometry": "Suspension_(vehicle)",        # Wishbones, pushrods, pullrods, anti-squat settings
    "f1_braking_systems": "Disc_brake",                     # Carbon-carbon brake discs and thermal cooling ducts
    
    # 3. ELECTRONICS, DATA SYSTEMS & PROCESSING
    "telemetry_processing": "Telemetry",                    # Real-time data logging, RF links, sensor streams
    "f1_sensors_inertial": "Inertial_measurement_unit",     # G-force acceleration mapping and gyroscopes
    "f1_ecu_control": "Electronic_control_unit",            # Standardized FIA engine controllers
    
    # 4. REGULATORY FRAMEWORKS & EVOLUTION
    "f1_regulations_current": "Formula_One_regulations",
    "f1_regulations_history": "History_of_Formula_One_regulations",
    "f1_safety_evolution": "Safety_in_Formula_One",         # Survival cells, fire suppression, and the Halo
    
    # 5. CONSTRUCTOR FACTORY OPERATIONS
    "scuderia_ferrari": "Scuderia_Ferrari",
    "mclaren_racing": "McLaren_Racing",
    "mercedes_amg_f1": "Mercedes-Benz_in_Formula_One",
    "red_bull_racing": "Red_Bull_Racing",
    "williams_racing": "Williams_Grand_Prix_Engineering",
    "alpine_f1": "Alpine_F1_Team",
    "aston_martin_f1": "Aston_Martin_in_Formula_One",
    "haas_f1": "Haas_F1_Team",
    "sauber_motorsport": "Sauber_Motorsport",
    "audi_f1_team": "Audi_in_Formula_One",
    "cadillac_f1_team": "Cadillac_in_Formula_One",
    
    # 6. HISTORIC WORLD CHAMPIONSHIP SEASONS
    "f1_2022_championship": "2022_Formula_One_World_Championship",
    "f1_2023_championship": "2023_Formula_One_World_Championship",
    "f1_2024_championship": "2024_Formula_One_World_Championship",
    "f1_2025_championship": "2025_Formula_One_World_Championship",
    "f1_2026_championship": "2026_Formula_One_World_Championship",
    
    # 7. DRIVERS & CIRCUITS
    "michael_schumacher": "Michael_Schumacher",
    "lewis_hamilton": "Lewis_Hamilton",
    "ayrton_senna": "Ayrton_Senna",
    "max_verstappen": "Max_Verstappen",
    "sebastian_vettel": "Sebastian_Vettel",
    "kimi_antonelli": "Kimi_Antonelli",
    "silverstone_circuit": "Silverstone_Circuit",
    "monza_circuit": "Autodromo_Nazionale_di_Monza",
    "spa_francorchamps": "Circuit_de_Spa-Francorchamps",
    "suzuka_circuit": "Suzuka_International_Racing_Course",
    "monaco_circuit": "Monaco_Circuit"
}

def download_wikipedia_md():
    print("====================================================")
    print("🏎️ STARTING MAXIMUM HYPER-SCALE F1 DATA HARVEST 🏎️")
    print(f"Target destination matrix: {RAW_DIR}")
    print("====================================================\n")
    
    api_url = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "F1ChatbotProject/4.0 (contact: engineering-student@example.com)"}

    success_count = 0

    for filename, topic in F1_TOPICS.items():
        output_path = os.path.join(RAW_DIR, f"{filename}.txt")
        print(f"Polling Wikipedia API for data payload: '{topic}'...")
        
        params = {
            "action": "query",
            "format": "json",
            "titles": topic,
            "prop": "extracts",
            "explaintext": True,  # Clean structural plain text, dropping messy HTML strings
            "redirects": 1        # Automatically trace dynamic page redirects
        }
        
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                
                page_id = next(iter(pages))
                page_data = pages[page_id]
                
                if "extract" in page_data and page_data["extract"].strip():
                    text_content = page_data["extract"]
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(text_content)
                    print(f"  ✓ Extracted successfully -> {filename}.txt ({len(text_content):,} chars)")
                    success_count += 1
                else:
                    print(f"  ✗ Text element footprint empty or omitted for title: {topic}")
            else:
                print(f"  ✗ Connection rejected for {topic} (Code: {response.status_code})")
        except Exception as e:
            print(f"  ✗ Pipeline loop execution crash on asset '{topic}': {e}")
            
    print("\n====================================================")
    print(f"✓ COMPLETED! Harvested {success_count}/{len(F1_TOPICS)} comprehensive engineering files.")
    print("====================================================")

if __name__ == "__main__":
    download_wikipedia_md()