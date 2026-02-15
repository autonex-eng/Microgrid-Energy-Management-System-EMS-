import requests
import time
import random

# CONFIGURATION
API_URL = "http://127.0.0.1:8000/api/update/"
HOUSES = ["house_1", "house_2", "house_3", "house_4", "house_5"]

def generate_mock_data():
    while True:
        for house in HOUSES:
            # Simulate wattage between 200W and 2500W
            wattage = round(random.uniform(200.0, 2500.0), 2)
            
            payload = {
                "house_id": house,
                "wattage": wattage
            }
            
            try:
                # Send data to your Django Backend
                response = requests.post(API_URL, json=payload)
                print(f"Sent {house}: {wattage}W | Status: {response.status_code}")
                
                # Check if Backend sent a "DISCONNECT" command in the response
                if response.json().get("command") == "DISCONNECT":
                    print(f"!!! ALARM: {house} Disconnected by Main Control !!!")
                    
            except Exception as e:
                print(f"Error connecting to backend: {e}")

        # Wait 2 seconds before next update
        time.sleep(2)

if __name__ == "__main__":
    print("Starting Solar System Simulation...")
    generate_mock_data()