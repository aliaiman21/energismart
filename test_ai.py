"""
Quick standalone test for ai_recommendations.py
Uses the realistic test scenario: terrace house, family of 4.
"""

from calculations import calculate_kwh, calculate_tnb_cost, calculate_co2
from ui_components import sorted_appliance_breakdown
from ai_recommendations import get_ai_recommendations

# Sample household: terrace house, 4 occupants
occupants = 4

# appliance name -> (watts, hours/day)
appliance_inputs = {
    "Air Conditioner": (746, 6),      # 1.0 HP
    "Refrigerator": (400, 24),
    "Washing Machine": (500, 1),
    "Water Heater": (1000, 1),
    "Fan": (50, 8),
    "Television": (50, 4),
    "Laptop": (50, 5),
    "Lighting": (32 * 6, 5),          # 6 bulbs, 5 hrs/day
}

breakdown = sorted_appliance_breakdown(appliance_inputs, calculate_kwh)
total_kwh = sum(a["kwh"] for a in breakdown)
cost = calculate_tnb_cost(total_kwh)
co2 = calculate_co2(total_kwh)

print(f"Total kWh: {total_kwh}")
print(f"Total cost: RM {cost['total_cost_rm']}")
print(f"CO2: {co2} kg\n")

recommendations, source = get_ai_recommendations(
    breakdown, total_kwh, cost, co2, occupants, calculate_tnb_cost
)

print(f"Source: {source}\n")
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec['icon']} {rec['title']}")
    print(f"   {rec['body']}\n")
    