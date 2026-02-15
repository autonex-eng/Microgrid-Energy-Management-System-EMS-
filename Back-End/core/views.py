from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random

# --- CONFIGURATION ---
# Max potential of one solar string/unit
SOLAR_CAPACITY_PER_UNIT = 3000.0

# --- STORAGE ---
HOUSE_DATA = {}
for i in range(1, 6):
    HOUSE_DATA[f"house_{i}"] = {"wattage": 0.0}

# Initialize 5 Solar Units
SOLAR_UNITS = {}
for i in range(1, 6):
    SOLAR_UNITS[f"solar_{i}"] = {
        "generation": 0.0,
        "status": "OFF"
    }

def dashboard_view(request):
    return render(request, 'dashboard.html')

def get_live_data(request):
    total_demand = sum(h['wattage'] for h in HOUSE_DATA.values())
    total_solar_gen = sum(s['generation'] for s in SOLAR_UNITS.values())
    
    return JsonResponse({
        "houses": HOUSE_DATA,
        "solar_units": SOLAR_UNITS,
        "total_demand": round(total_demand, 2),
        "total_solar": round(total_solar_gen, 2)
    })

@csrf_exempt
def update_house_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            house_id = data.get('house_id')
            wattage = float(data.get('wattage', 0))

            if house_id in HOUSE_DATA:
                HOUSE_DATA[house_id]['wattage'] = wattage




            
            # 1. Calculate Total Demand & Potential Solar
            total_demand = sum(h['wattage'] for h in HOUSE_DATA.values())
            
            # Calculate what solar COULD produce based on weather (e.g., 5000W max)
            total_potential_solar = 0
            unit_potentials = {}
            for i in range(1, 6):
                pot = random.uniform(600, SOLAR_CAPACITY_PER_UNIT) # e.g., 1000W limit
                unit_potentials[f"solar_{i}"] = pot
                total_potential_solar += pot

            # 2. CHECK: Do we have enough Solar?
            if total_potential_solar >= total_demand:
                # CASE: ENOUGH POWER (Happy Path)
                # We limit solar to match demand exactly
                scale = total_demand / total_potential_solar
                for unit, pot in unit_potentials.items():
                    SOLAR_UNITS[unit]['generation'] = round(pot * scale, 1)
                    SOLAR_UNITS[unit]['status'] = "RELAY ON"
                    
                # All houses stay ON
                for h in HOUSE_DATA:
                    HOUSE_DATA[h]['status'] = "CONNECTED" # You might need to add this status field back to houses

            else:
                # CASE: NOT ENOUGH POWER (Blackout Prevention)
                # Solar runs at Max
                for unit, pot in unit_potentials.items():
                    SOLAR_UNITS[unit]['generation'] = round(pot, 1)
                    SOLAR_UNITS[unit]['status'] = "MAX POWER"
                    
                # We must CUT OFF houses until Demand < Supply
                available_power = total_potential_solar
                current_load = 0
                
                # Sort houses by wattage (Smallest first? Or Random?)
                # Let's just loop and cut power if we run out
                for house_id, data in HOUSE_DATA.items():
                    if (current_load + data['wattage']) <= available_power:
                        # Safe to keep ON
                        current_load += data['wattage']
                        # (You would send a "CONNECT" command here)
                    else:
                        # Not enough power! CUT IT OFF.
                        data['wattage'] = 0.0 # Force wattage to 0 because it's off





            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)