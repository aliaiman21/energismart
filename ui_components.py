"""
EnergiSmart - UI helper logic
Appliance metadata, rule-based recommendations, the (clearly-labelled,
transparent) efficiency score, and CSV report export.

IMPORTANT: none of this touches calculate_kwh / calculate_tnb_cost /
calculate_co2 - it only consumes their outputs.
"""

import io
import pandas as pd

# ---------------------------------------------------------------
# Appliance display metadata (icon + short description for cards)
# ---------------------------------------------------------------

APPLIANCE_META = {
    "Air Conditioner":  {"icon": "❄️", "desc": "Cooling & climate control"},
    "Refrigerator":     {"icon": "🧊", "desc": "Always-on food preservation"},
    "Washing Machine":  {"icon": "🧺", "desc": "Laundry cleaning"},
    "Dryer":            {"icon": "🌀", "desc": "Laundry drying"},
    "Water Heater":     {"icon": "🚿", "desc": "Hot water supply"},
    "Fan":               {"icon": "🌬️", "desc": "Air circulation"},
    "Television":       {"icon": "📺", "desc": "Home entertainment"},
    "Desktop PC":        {"icon": "🖥️", "desc": "Work & computing"},
    "Laptop":            {"icon": "💻", "desc": "Portable computing"},
    "Lighting":          {"icon": "💡", "desc": "Home illumination"},
}

APPLIANCE_ORDER = [
    "Air Conditioner", "Refrigerator", "Washing Machine", "Dryer", "Water Heater",
    "Fan", "Television", "Desktop PC", "Laptop", "Lighting",
]

# ---------------------------------------------------------------
# Rule-based recommendation copy per appliance (used when that
# appliance is the household's #1 or #2 consumer). Purely rule-based -
# NOT AI-generated. No Claude API call is involved here.
# ---------------------------------------------------------------

TIPS = {
    "Air Conditioner": {
        "title": "Optimise Air Conditioning",
        "icon": "❄️",
        "body": "Your air conditioner is currently your largest energy consumer. "
                "Raising the set temperature by 1-2°C or reducing operating hours "
                "when the room is unoccupied can meaningfully lower consumption "
                "without a large comfort trade-off.",
    },
    "Water Heater": {
        "title": "Shorten Water Heater Usage",
        "icon": "🚿",
        "body": "Water heaters draw very high wattage even for short periods. "
                "Reducing shower time by a few minutes per person, or lowering "
                "the thermostat setting, can noticeably cut this appliance's contribution.",
    },
    "Dryer": {
        "title": "Reduce Dryer Reliance",
        "icon": "🌀",
        "body": "Dryers are one of the highest-wattage appliances in a typical home. "
                "Line-drying laundry on dry days, even partially, can significantly "
                "reduce this appliance's monthly consumption.",
    },
    "Refrigerator": {
        "title": "Maintain Refrigerator Efficiency",
        "icon": "🧊",
        "body": "Your refrigerator runs continuously, so small efficiency losses add "
                "up. Keep coils clean, avoid overpacking, and check the door seal - "
                "a poor seal can raise consumption without any visible sign.",
    },
    "Washing Machine": {
        "title": "Run Full Loads Only",
        "icon": "🧺",
        "body": "Washing machines use similar energy per cycle regardless of load "
                "size. Consolidating laundry into full loads reduces the number of "
                "cycles needed per month.",
    },
    "Lighting": {
        "title": "Optimise Lighting",
        "icon": "💡",
        "body": "Consider switching frequently-used bulbs to energy-efficient LED "
                "lighting where you haven't already. LEDs typically use 70-85% less "
                "energy than incandescent bulbs for the same brightness.",
    },
    "Desktop PC": {
        "title": "Manage Desktop PC Usage",
        "icon": "🖥️",
        "body": "Enable sleep mode during idle periods and shut down fully when not "
                "in use overnight, rather than leaving the desktop running continuously.",
    },
    "Television": {
        "title": "Manage Television Standby Time",
        "icon": "📺",
        "body": "Switch off at the wall rather than leaving the television on standby "
                "for long periods - standby draw adds up over a full month.",
    },
    "Fan": {
        "title": "Use Fans Strategically",
        "icon": "🌬️",
        "body": "Pairing a fan with a slightly higher air-conditioner temperature "
                "setting can maintain comfort while reducing your overall cooling load.",
    },
    "Laptop": {
        "title": "Manage Laptop Charging Habits",
        "icon": "💻",
        "body": "Laptops are relatively low-consumption, but enabling battery-saver "
                "or sleep settings during idle periods still adds up over a month.",
    },
}


def sorted_appliance_breakdown(appliance_inputs, calculate_kwh):
    """
    Returns a list of dicts: [{name, watts, hours, kwh}, ...] sorted by kWh
    descending. Uses the existing calculate_kwh() - no numbers invented here.
    """
    rows = []
    for name, (watts, hours) in appliance_inputs.items():
        kwh = calculate_kwh(watts, hours)
        rows.append({"name": name, "watts": watts, "hours": hours, "kwh": kwh})
    rows.sort(key=lambda r: r["kwh"], reverse=True)
    return rows


def top_driver_impact(breakdown, total_kwh, calculate_tnb_cost, reduce_hours=2):
    """
    For the #1 appliance by kWh, calculate the ACTUAL RM impact of reducing
    its daily usage by `reduce_hours` hours/day, using the real
    calculate_tnb_cost() function (never a fabricated figure).
    Returns None if there isn't a meaningful reduction to show.
    """
    if not breakdown:
        return None
    top = breakdown[0]
    if top["hours"] <= 0:
        return None

    new_hours = max(0, top["hours"] - reduce_hours)
    actual_reduction_hours = top["hours"] - new_hours
    if actual_reduction_hours <= 0:
        return None

    reduced_kwh_for_appliance = (top["watts"] / 1000) * new_hours * 30
    kwh_saved = round(top["kwh"] - reduced_kwh_for_appliance, 2)
    new_total_kwh = max(0, total_kwh - kwh_saved)

    cost_before = calculate_tnb_cost(total_kwh)
    cost_after = calculate_tnb_cost(new_total_kwh)
    rm_saved = round(cost_before["total_cost_rm"] - cost_after["total_cost_rm"], 2)

    return {
        "appliance": top["name"],
        "reduce_hours": actual_reduction_hours,
        "kwh_saved": kwh_saved,
        "rm_saved": rm_saved,
    }


def generate_recommendations(breakdown, total_kwh, calculate_tnb_cost):
    """
    Build up to 3 rule-based recommendation cards from the household's
    ACTUAL calculated data. Not AI-generated - no Claude API call here.
    """
    recs = []
    if not breakdown:
        return recs

    # 1) Tip for the top consumer
    top = breakdown[0]
    tip = TIPS.get(top["name"])
    if tip:
        recs.append(tip)

    # 2) Tip for the #2 consumer, if meaningfully different from #1
    if len(breakdown) > 1:
        second = breakdown[1]
        tip2 = TIPS.get(second["name"])
        if tip2 and tip2["title"] != tip["title"]:
            recs.append(tip2)

    # 3) General carbon-footprint tip referencing the top driver
    if total_kwh > 0:
        share = round((top["kwh"] / total_kwh) * 100, 1)
        recs.append({
            "title": "Reduce Your Carbon Footprint",
            "icon": "🌍",
            "body": f"Small changes to your highest-consumption appliance "
                    f"({top['name']}, {share}% of your monthly usage) will reduce "
                    f"your carbon footprint more than the same effort applied to a "
                    f"low-consumption device.",
        })

    return recs[:3]


def efficiency_score(total_kwh, occupants, benchmark_kwh_per_person=200):
    """
    A SIMPLE, TRANSPARENT, clearly-estimated efficiency score - not a
    scientific or official rating. Formula (disclosed in the UI):

        usage_per_person = total_kwh / occupants
        ratio            = usage_per_person / benchmark_kwh_per_person
        score             = 100 - (ratio - 1) * 100, clamped to [0, 100]

    i.e. usage exactly at the benchmark -> 100; double the benchmark -> 0.
    """
    if occupants <= 0:
        occupants = 1
    usage_per_person = total_kwh / occupants
    ratio = usage_per_person / benchmark_kwh_per_person
    raw_score = 100 - (ratio - 1) * 100
    score = max(0, min(100, round(raw_score)))

    if score >= 80:
        band = "Excellent"
        message = "Your household's usage is efficient relative to our reference benchmark."
    elif score >= 60:
        band = "Good"
        message = "Good — there is still room to reduce your energy consumption."
    elif score >= 40:
        band = "Fair"
        message = "Fair — a few targeted changes could meaningfully lower your usage."
    else:
        band = "Needs Improvement"
        message = "Your usage is well above the reference benchmark — see the recommendations below."

    return {
        "score": score,
        "band": band,
        "message": message,
        "usage_per_person": round(usage_per_person, 1),
        "benchmark": benchmark_kwh_per_person,
    }


def build_csv_report(household, breakdown, cost, co2, score):
    """
    Build a simple, structured CSV report the user can download.
    Returns bytes ready for st.download_button.
    """
    buf = io.StringIO()

    buf.write("EnergiSmart Energy Report\n")
    buf.write("\nHousehold\n")
    pd.DataFrame([household]).to_csv(buf, index=False)

    buf.write("\nPer-Appliance Breakdown\n")
    pd.DataFrame(breakdown)[["name", "watts", "hours", "kwh"]].rename(
        columns={"name": "Appliance", "watts": "Watts", "hours": "Hours/day", "kwh": "kWh/month"}
    ).to_csv(buf, index=False)

    buf.write("\nTNB Bill Breakdown (RM)\n")
    pd.DataFrame([cost]).to_csv(buf, index=False)

    buf.write("\nSummary\n")
    pd.DataFrame([{
        "Total kWh/month": cost["total_kwh"],
        "Total Bill (RM)": cost["total_cost_rm"],
        "CO2 (kg/month)": co2,
        "Efficiency Score": score["score"],
        "Efficiency Band": score["band"],
    }]).to_csv(buf, index=False)

    buf.write("\nDisclaimer: Estimated based on the tariff assumptions used by this "
               "application (TNB Domestic Tariff, effective 1 July 2025). Actual TNB "
               "bills may vary. This report is not an official TNB document.\n")

    return buf.getvalue().encode("utf-8")
