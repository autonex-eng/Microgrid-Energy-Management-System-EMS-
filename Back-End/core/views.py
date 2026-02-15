from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# --- 1. CONFIGURATION ---
# The maximum power your solar system can provide (e.g., 5000 Watts)
MAX_SOLAR_CAPACITY = 5000.0

# --- 2. IN-MEMORY STORAGE ---
# This acts as our "Real-Time Database"
# Structure: { 'house_1': {'wattage': 0, 'status': 'CONNECTED'}, ... }
HOUSE_DATA = {}

# Initialize 5 houses
for i in range(1, 6):
    HOUSE_DATA[f"house_{i}"] = {"wattage": 0.0, "status": "CONNECTED"}


# --- 3. THE DASHBOARD VIEW ---
def dashboard_view(request):
    """Renders the HTML Dashboard"""
    return render(request, 'dashboard.html')


# --- 4. API: GET DATA (For Frontend) ---
def get_live_data(request):
    """Sends the latest data to the frontend JavaScript"""
    # Calculate totals for the dashboard
    total_load = sum(h['wattage'] for h in HOUSE_DATA.values() if h['status'] == 'CONNECTED')
    
    return JsonResponse({
        "houses": HOUSE_DATA,
        "total_load": round(total_load, 2),
        "max_capacity": MAX_SOLAR_CAPACITY,
        "grid_status": "OVERLOAD" if total_load > MAX_SOLAR_CAPACITY else "NORMAL"
    })


# --- 5. API: RECEIVE DATA (From Simulator/ESP32) ---
@csrf_exempt
def update_house_data(request):
    """
    Receives JSON: {"house_id": "house_1", "wattage": 1200.5}
    Returns JSON:  {"command": "CONNECT" or "DISCONNECT"}
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            house_id = data.get('house_id')
            wattage = float(data.get('wattage', 0))

            # A. Update the specific house's reading
            if house_id in HOUSE_DATA:
                HOUSE_DATA[house_id]['wattage'] = wattage
            else:
                # Register new house if unknown
                HOUSE_DATA[house_id] = {'wattage': wattage, 'status': 'CONNECTED'}

            # B. THE MAIN LOGIC (Supply vs Demand)
            # Calculate total load assuming everyone is connected
            current_total_load = sum(h['wattage'] for h in HOUSE_DATA.values() if h['status'] == 'CONNECTED')

            command = "CONNECT"
            
            # Logic: If demand is too high, cut off this house?
            # (Simple version: If total > max, tell the reporting house to disconnect)
            if current_total_load > MAX_SOLAR_CAPACITY:
                # Mark as disconnected in our DB
                HOUSE_DATA[house_id]['status'] = 'DISCONNECTED'
                command = "DISCONNECT"
            else:
                # If we have capacity, allow connection
                HOUSE_DATA[house_id]['status'] = 'CONNECTED'
                command = "CONNECT"

            return JsonResponse({"status": "success", "command": command})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)