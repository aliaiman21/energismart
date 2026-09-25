"""
EnergiSmart - Reference Data
All the numbers here come from official Malaysian sources:
- TNB tariff rates (effective 1 July 2025): mytnb.com.my/tariff
- Appliance wattages: TNB Home Energy Calculator, hec.tnb.com.my
- CO2 grid emission factor: Suruhanjaya Tenaga (Energy Commission Malaysia), 2024, Peninsular Malaysia
This file has NO logic in it - just numbers, stored so the rest of the app can use them.
"""

# ---------------------------------------------------------
# 1. TNB DOMESTIC TARIFF RATES (effective 1 July 2025)
# ---------------------------------------------------------

TNB_TARIFF = {
    "energy_charge_low": 0.2703,    # RM per kWh, for usage up to 1,500 kWh/month
    "energy_charge_high": 0.3703,   # RM per kWh, for usage above 1,500 kWh/month
    "energy_charge_threshold_kwh": 1500,

    "capacity_charge": 0.0455,      # RM per kWh
    "network_charge": 0.1285,       # RM per kWh

    "retail_charge": 10.00,         # RM per month (flat)
    "retail_charge_waived_below_kwh": 600,  # no retail charge if usage <= 600 kWh
}

# ---------------------------------------------------------
# 2. ENERGY EFFICIENCY INCENTIVE (REBATE) TABLE
# Each entry: (minimum kWh, maximum kWh, rebate in RM per kWh)
# Above 1000 kWh/month = no rebate
# ---------------------------------------------------------

REBATE_TIERS = [
    (1,    200,  0.250),
    (201,  250,  0.245),
    (251,  300,  0.225),
    (301,  350,  0.210),
    (351,  400,  0.170),
    (401,  450,  0.145),
    (451,  500,  0.120),
    (501,  550,  0.105),
    (551,  600,  0.090),
    (601,  650,  0.075),
    (651,  700,  0.055),
    (701,  750,  0.045),
    (751,  800,  0.040),
    (801,  850,  0.025),
    (851,  900,  0.010),
    (901,  1000, 0.005),
]

# ---------------------------------------------------------
# 3. APPLIANCE WATTAGE REFERENCE (the official 10 appliances)
# Values in Watts (W)
# Air Conditioner is NOT here - it's worked out separately below,
# based on its horsepower (HP), using AC_HP_TO_WATT.
# ---------------------------------------------------------

APPLIANCE_WATTAGE = {
    "Refrigerator": 400,
    "Washing Machine": 500,
    "Dryer": 3400,
    "Water Heater": 1000,
    "Fan": 50,
    "Television": 50,
    "Desktop PC": 300,
    "Laptop": 50,
    "Lighting": 32,   # per bulb
}

# ---------------------------------------------------------
# 4. AIR CONDITIONER: HORSEPOWER (HP) -> WATTAGE
# ---------------------------------------------------------

AC_HP_TO_WATT = {
    0.5: 373,
    1.0: 746,
    1.5: 1119,
    2.0: 1492,
    2.5: 1865,
    3.0: 2238,
}

# ---------------------------------------------------------
# 5. CO2 EMISSIONS FACTOR
# Source: Suruhanjaya Tenaga (Energy Commission Malaysia), 2024
# Grid Emission Factor for Peninsular Malaysia
# ---------------------------------------------------------

CO2_EMISSION_FACTOR_KG_PER_KWH = 0.740  # kg CO2 released per kWh of electricity used