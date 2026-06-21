"""
verify_state.py

Confirms state flows correctly through run_agent's planning loop:
  - the dict passed INTO suggest_outfit is the SAME object as session["selected_item"]
  - the string passed INTO create_fit_card is the SAME object as session["outfit_suggestion"]

We wrap the real tools to record exactly what they received, using `is`
(identity) checks — so this proves no re-prompting, copying, or hardcoding
happens between steps.
"""

import agent
from utils.data_loader import get_example_wardrobe

# Records of what each tool actually received at call time.
seen = {}

_real_suggest = agent.suggest_outfit
_real_create = agent.create_fit_card


def spy_suggest_outfit(new_item, wardrobe):
    seen["suggest_outfit_item"] = new_item          # object passed in
    return _real_suggest(new_item, wardrobe)


def spy_create_fit_card(outfit, new_item):
    seen["create_fit_card_outfit"] = outfit          # object passed in
    seen["create_fit_card_item"] = new_item
    return _real_create(outfit, new_item)


# Patch the names that run_agent calls.
agent.suggest_outfit = spy_suggest_outfit
agent.create_fit_card = spy_create_fit_card

QUERY = "looking for a vintage graphic tee under $30"

session = agent.run_agent(query=QUERY, wardrobe=get_example_wardrobe())

print(f"Query: {QUERY!r}\n")

if session["error"]:
    print(f"Agent ended early with error: {session['error']}")
    raise SystemExit(1)

print("=== session['selected_item'] ===")
print(session["selected_item"])
print()

print("=== session['outfit_suggestion'] ===")
print(session["outfit_suggestion"])
print()

# ── Identity checks (the actual verification) ────────────────────────────────
item_match = session["selected_item"] is seen["suggest_outfit_item"]
item_into_card = session["selected_item"] is seen["create_fit_card_item"]
outfit_match = session["outfit_suggestion"] is seen["create_fit_card_outfit"]

print("=== State-flow checks (must all be True) ===")
print(f"selected_item is the dict passed into suggest_outfit:   {item_match}")
print(f"selected_item is the dict passed into create_fit_card:  {item_into_card}")
print(f"outfit_suggestion is the str passed into create_fit_card: {outfit_match}")

if item_match and item_into_card and outfit_match:
    print("\nPASS — state flows through the session with no re-prompting or hardcoding.")
else:
    print("\nFAIL — a tool received something other than the stored session value.")
    raise SystemExit(1)
