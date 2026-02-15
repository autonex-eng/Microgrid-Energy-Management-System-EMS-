import requests
import time
import random

# --- CONFIGURATION ---
# UPDATE THIS URL if you are using PythonAnywhere
API_URL = "http://127.0.0.1:8000/api/update/"
HOUSES = ["house_1", "house_2", "house_3", "house_4", "house_5"]

def generate_mock_data():
    print(f"🚀 Starting Zero-Export Simulator targeting: {API_URL}")
    
    while True:
        for house in HOUSES:
            # Random wattage: Some low (idle), some high (kettle/AC)
            if random.random() > 0.6:
                 wattage = round(random.uniform(1500.0, 3000.0), 2)
            else:
                 wattage = round(random.uniform(100.0, 500.0), 2)
            
            payload = { "house_id": house, "wattage": wattage }
            
            try:
                response = requests.post(API_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    # Print the logic feedback
                    server_cmd = data.get("solar_cmd", "OK")
                    print(f"[{house}] {wattage}W Sent -> Solar Status: {server_cmd}")
                else:
                    print(f"Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"❌ Connection Error: {e}")

        # Wait a bit so logs are readable
        time.sleep(1.5)

if __name__ == "__main__":
    generate_mock_data()