"""
EnergiSmart - AI-powered recommendation module (Phase 2)

Sends Claude the household's ALREADY-CALCULATED numbers (never raw form
input, and Claude is never asked to invent its own kWh/RM/CO2 figures).
Includes output validation + a retry loop. Falls back to the existing
rule-based generate_recommendations() if the API call fails or returns
something unparseable.
"""

import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

from ui_components import generate_recommendations  # rule-based fallback

load_dotenv()
_client = None


def _get_client():
    """Create the Anthropic client once and reuse it."""
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not found in .env")
        _client = Anthropic(api_key=api_key)
    return _client


def _build_prompt(breakdown, total_kwh, cost, co2, occupants):
    """
    Build the prompt. We only send CALCULATED numbers - Claude must reason
    over these, not invent its own kWh/RM/CO2 figures.
    """
    top3 = breakdown[:3]
    appliance_lines = "\n".join(
        f"- {a['name']}: {a['kwh']} kWh/month ({a['hours']} hrs/day at {a['watts']}W)"
        for a in top3
    )

    prompt = f"""You are an energy-saving advisor for a Malaysian household.

Here is this household's ALREADY-CALCULATED energy data. Do not invent or
recalculate any kWh, RM, or CO2 numbers - only use the ones given below.

Household size: {occupants} occupants
Total monthly usage: {total_kwh} kWh
Total monthly bill: RM {cost['total_cost_rm']}
CO2 emitted: {co2} kg/month

Top energy-consuming appliances:
{appliance_lines}

Based ONLY on this data, generate exactly 3 personalised energy-saving
recommendations, ranked by potential impact.

STRICT RULE 1 (no invented numbers): Do NOT invent, estimate, or calculate
any new numbers of your own - no percentages, no RM savings figures, no
kWh figures, and critically, NO CO2 figures for individual appliances
(only the household's TOTAL CO2 figure above was calculated - no
per-appliance CO2 breakdown exists, so never state or imply one). Only
reference the exact numbers already given above (household total kWh,
RM, CO2, and each appliance's own kWh/watts/hours as listed). Give
practical, specific, qualitative advice instead (what to do and why it
matters), without quantifying the outcome yourself.

STRICT RULE 2 (no spending advice): This app helps Malaysian households
REDUCE their electricity bill. Never recommend buying, replacing, or
upgrading an appliance (e.g. "switch to an inverter model", "replace your
dryer", "buy a new fridge") - that asks the household to spend money to
solve a cost problem, which contradicts the point of this advice.
Recommendations must be FREE or near-free actions the household can do
immediately: changing usage habits (e.g. hours, timing, temperature
settings), basic maintenance (e.g. cleaning coils/filters, checking door
seals), or behavioural changes (e.g. air-drying instead of using a
dryer). If an appliance is the top energy consumer purely because of how
often or how long it is used, focus the advice on usage, not the
appliance itself.

For each recommendation, respond ONLY with a JSON array in this exact
format, with nothing else before or after it (no markdown fences, no
preamble):

[
  {{"title": "short title (max 6 words)", "icon": "one relevant emoji", "body": "2-3 sentence practical, personalised tip referencing the specific appliance and numbers above"}},
  {{"title": "...", "icon": "...", "body": "..."}},
  {{"title": "...", "icon": "...", "body": "..."}}
]
"""
    return prompt


def _validate(parsed):
    """Check the parsed JSON matches the shape our UI expects."""
    if not isinstance(parsed, list) or len(parsed) == 0:
        return False
    for item in parsed:
        if not isinstance(item, dict):
            return False
        if not all(k in item for k in ("title", "icon", "body")):
            return False
        if not all(isinstance(item[k], str) and item[k].strip() for k in ("title", "icon", "body")):
            return False
    return True


def get_ai_recommendations(breakdown, total_kwh, cost, co2, occupants,
                            calculate_tnb_cost, max_retries=2):
    """
    Main entry point. Tries Claude up to `max_retries` times with output
    validation. Falls back to the rule-based recommendations if the API
    call fails or output can't be validated after all retries.

    Returns: (recommendations_list, source) where source is "ai" or "rule_based"
    """
    prompt = _build_prompt(breakdown, total_kwh, cost, co2, occupants)

    for attempt in range(max_retries):
        try:
            client = _get_client()
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = response.content[0].text.strip()

            # Strip markdown fences if Claude adds them despite instructions
            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                if raw_text.lower().startswith("json"):
                    raw_text = raw_text[4:].strip()

            parsed = json.loads(raw_text)

            if _validate(parsed):
                return parsed[:3], "ai"
            # invalid shape -> fall through to retry

        except Exception:
            # API error, timeout, bad JSON, etc. -> retry
            pass

    # All attempts failed or were invalid -> use the existing rule-based logic
    fallback = generate_recommendations(breakdown, total_kwh, calculate_tnb_cost)
    return fallback, "rule_based"
