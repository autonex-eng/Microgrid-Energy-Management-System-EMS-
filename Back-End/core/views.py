from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random

# --- CONFIGURATION ---
# Keep this high (e.g. 3000.0) so your supply usually matches demand.
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
            
            # --- 1. CALCULATE DEMAND ---
            total_demand = sum(h['wattage'] for h in HOUSE_DATA.values())
            remaining_demand_to_fill = total_demand

            # --- 2. SEQUENTIAL SOLAR LOGIC ---
            # Try to fill the demand with solar units 1-5
            for i in range(1, 6):
                unit_id = f"solar_{i}"
                max_potential = random.uniform(600, SOLAR_CAPACITY_PER_UNIT)
                
                if remaining_demand_to_fill > 0:
                    if remaining_demand_to_fill >= max_potential:
                        # Unit provides 100% capacity
                        SOLAR_UNITS[unit_id]['generation'] = round(max_potential, 2)
                        SOLAR_UNITS[unit_id]['status'] = "RELAY ON"
                        remaining_demand_to_fill -= max_potential
                    else:
                        # Unit throttles to match exact demand
                        SOLAR_UNITS[unit_id]['generation'] = round(remaining_demand_to_fill, 2)
                        SOLAR_UNITS[unit_id]['status'] = "RELAY ON"
                        remaining_demand_to_fill = 0 
                else:
                    # Not needed
                    SOLAR_UNITS[unit_id]['generation'] = 0.0
                    SOLAR_UNITS[unit_id]['status'] = "OFF"

            # --- REMOVED: BLACKOUT PREVENTION LOGIC ---
            # We deleted the code that sets house wattage to 0.0
            # Now, if demand > solar, houses stay ON, and Solar just stays at MAX.

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)