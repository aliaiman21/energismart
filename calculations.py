"""
EnergiSmart - Calculation Engine
Plain Python functions only - no UI, no AI here.
Turns wattage + hours/day into kWh, RM cost, and CO2.
"""

from data import TNB_TARIFF, REBATE_TIERS, CO2_EMISSION_FACTOR_KG_PER_KWH


def calculate_kwh(wattage_watts, hours_per_day, days=30):
    """
    Turn an appliance's wattage and daily usage hours into monthly kWh.
    Formula: kWh = (Watts / 1000) * hours per day * days in month
    """
    kwh = (wattage_watts / 1000) * hours_per_day * days
    return round(kwh, 2)


def get_rebate_rate(total_kwh):
    """
    Look up the rebate rate (RM per kWh) for a given monthly usage.
    Returns 0 if usage is above 1000 kWh (no rebate).
    """
    for min_kwh, max_kwh, rebate_rm_per_kwh in REBATE_TIERS:
        if min_kwh <= total_kwh <= max_kwh:
            return rebate_rm_per_kwh
    return 0.0  # above 1000 kWh = no rebate


def calculate_tnb_cost(total_kwh):
    """
    Calculate the TNB electricity bill for a given total monthly kWh usage,
    following TNB's real tiered structure: energy charge (tiered) + capacity
    charge + network charge + retail charge - rebate.
    Returns a dictionary with the full cost breakdown.
    """
    threshold = TNB_TARIFF["energy_charge_threshold_kwh"]

    # Energy charge (tiered: different rate above/below 1500 kWh)
    if total_kwh <= threshold:
        energy_charge = total_kwh * TNB_TARIFF["energy_charge_low"]
    else:
        energy_charge = (
            threshold * TNB_TARIFF["energy_charge_low"]
            + (total_kwh - threshold) * TNB_TARIFF["energy_charge_high"]
        )

    # Capacity + network charge (apply to all kWh, no tiering)
    capacity_charge = total_kwh * TNB_TARIFF["capacity_charge"]
    network_charge = total_kwh * TNB_TARIFF["network_charge"]

    # Retail charge (flat fee, waived for low usage)
    if total_kwh <= TNB_TARIFF["retail_charge_waived_below_kwh"]:
        retail_charge = 0.0
    else:
        retail_charge = TNB_TARIFF["retail_charge"]

    # Rebate (subtracted)
    rebate_rate = get_rebate_rate(total_kwh)
    rebate_amount = total_kwh * rebate_rate

    total_cost = energy_charge + capacity_charge + network_charge + retail_charge - rebate_amount

    return {
        "total_kwh": round(total_kwh, 2),
        "energy_charge": round(energy_charge, 2),
        "capacity_charge": round(capacity_charge, 2),
        "network_charge": round(network_charge, 2),
        "retail_charge": round(retail_charge, 2),
        "rebate_amount": round(rebate_amount, 2),
        "total_cost_rm": round(total_cost, 2),
    }


def calculate_co2(total_kwh):
    """Calculate CO2 emissions (in kg) for a given monthly kWh usage."""
    co2_kg = total_kwh * CO2_EMISSION_FACTOR_KG_PER_KWH
    return round(co2_kg, 2)


# ---------------------------------------------------------
# Quick test - run this file directly to see it in action
# ---------------------------------------------------------
if __name__ == "__main__":
    # Example household: 1.0 HP aircon (8 hrs/day) + fridge (24 hrs/day) + TV (5 hrs/day)
    appliances = [
        ("Air Conditioner (1.0 HP)", 746, 8),
        ("Refrigerator", 400, 24),
        ("Television", 50, 5),
    ]

    total_kwh = 0
    print("--- Per-appliance breakdown ---")
    for name, watts, hours in appliances:
        kwh = calculate_kwh(watts, hours)
        total_kwh += kwh
        print(f"{name}: {kwh} kWh/month")

    print(f"\nTotal usage: {round(total_kwh, 2)} kWh/month")

    cost = calculate_tnb_cost(total_kwh)
    print("\n--- TNB Bill Breakdown ---")
    for key, value in cost.items():
        print(f"{key}: {value}")

    co2 = calculate_co2(total_kwh)
    print(f"\nCO2 emissions: {co2} kg/month")