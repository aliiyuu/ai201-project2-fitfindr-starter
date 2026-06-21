# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tool Inventory

Your README submission must document each tool's name, inputs, and return value. **These must exactly match your actual function signatures in `tools.py`.** Your documented interfaces will be checked against your actual function signatures in `tools.py` — if the parameter count or types contradict what's in the code, you may not receive full credit for that tool.

### `search_listings(description, size=None, max_price=None) -> list[dict]`

Searches the mock listings dataset for items matching the keywords, then optionally filters by size and price ceiling and ranks the matches by keyword overlap.

| Parameter | Type | Description |
|-----------|------|-------------|
| `description` | `str` | Keywords describing what the user wants (e.g. `"vintage graphic tee"`). Used for relevance scoring. |
| `size` | `str \| None` | Size to filter by, matched case-insensitively as a substring (so `"M"` matches `"S/M"`). `None` skips size filtering. |
| `max_price` | `float \| None` | Maximum price, inclusive. `None` skips price filtering. |

**Returns:** A `list[dict]` of matching listings sorted by relevance (best match first). Each dict contains `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`. Returns `[]` when nothing matches — never raises.

### `suggest_outfit(new_item, wardrobe) -> str`

Asks the LLM to suggest 1–2 complete outfits for a thrifted item, pairing it with the user's wardrobe.

| Parameter | Type | Description |
|-----------|------|-------------|
| `new_item` | `dict` | A listing dict (typically the top result from `search_listings`). |
| `wardrobe` | `dict` | A wardrobe dict with an `items` key holding a list of wardrobe items. May be empty. |

**Returns:** A non-empty `str` with the outfit suggestion(s). When the wardrobe is empty, it returns general styling advice instead of referencing owned pieces.

### `create_fit_card(outfit, new_item) -> str`

Generates a short, casual, shareable caption (like a real OOTD post) for the thrifted find.

| Parameter | Type | Description |
|-----------|------|-------------|
| `outfit` | `str` | The outfit suggestion string returned by `suggest_outfit`. |
| `new_item` | `dict` | The listing dict for the thrifted item, used for the name, price, and platform. |

**Returns:** A 2–4 sentence `str` usable as an Instagram/TikTok caption. Uses a higher LLM temperature so different inputs produce different captions. If `outfit` is empty or whitespace-only, it returns a descriptive error string instead of calling the LLM.

---

## Interaction Walkthrough

## Demo Video

A full demo of FitFindr is here: [Watch the demo](https://drive.google.com/file/d/1Y9WJt0kFv4otB6Z2tFcF1eYnxGAjrk-l/view?usp=sharing)

<!-- Walk through a complete interaction step by step: natural language query → each tool call (and why) → final fit card.
     Walk through this carefully — it's how graders follow your agent's reasoning without a live demo.
     Use a specific example — do not leave this as a template. -->

**User query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1: Tool called:**
- Tool: `search_listings`
- Input: `search_listings("vintage graphic tee", size=None, max_price=30.0)`
- Why this tool: The user wants to find an item, so the agent first searches the listings dataset using the keywords and price ceiling parsed from the query.
- Output: A ranked `list[dict]` of matching listings. The top result is selected as `selected_item` — e.g. `"Y2K Baby Tee — Butterfly Print"` ($18, depop, size S/M).

**Step 2: Tool called:**
- Tool: `suggest_outfit`
- Input: `suggest_outfit(new_item=<Y2K Baby Tee>, wardrobe=<example wardrobe>)`
- Why this tool: Now that an item is selected, the agent asks the LLM how to style it with the user's wardrobe.
- Output: A styling string referencing specific owned pieces — e.g. pairing the tee with baggy straight-leg jeans and chunky white sneakers for a casual look, plus a second earthy-toned option.

**Step 3: Tool called:**
- Tool: `create_fit_card`
- Input: `create_fit_card(outfit=<suggestion>, new_item=<Y2K Baby Tee>)`
- Why this tool: With a styled outfit ready, the agent generates a shareable caption that names the item, price, and platform.
- Output: A 2–4 sentence OOTD caption, e.g. "thrifted this Y2K butterfly baby tee off depop for $18 and it's everything 🦋 styled with my baggy jeans + chunky sneakers, full look in stories".

**Final output to user:** FitFindr shows the picked listing, the styling suggestion, and the ready-to-post fit card caption together, so the user can decide whether to buy and how to wear it.

---

## Error Handling and Fail Points

<!-- For each tool, describe the specific failure mode and what your agent does in response.
     This maps to the error handling section of the rubric (F5-C1). -->

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | No results match the query (`[]` returned) | **Stop (hard stop).** Don't call `suggest_outfit` or `create_fit_card`. Set an error message in the session telling the user what to adjust (raise budget, loosen size, simplify keywords) and return early. |
| `suggest_outfit` | Wardrobe is empty (`wardrobe['items'] == []`) | **Adapt (continue).** Don't stop or error. Fall back to general styling advice for the item instead of named owned pieces, return a non-empty string, and proceed to `create_fit_card`. |
| `create_fit_card` | Outfit input is missing or incomplete (empty/whitespace `outfit`) | **Stop (hard stop).** Don't call the LLM. Return a descriptive error string instead of a blank caption so the loop surfaces a clear message. |

---

## Spec Reflection

<!-- Answer both questions with at least 2–3 sentences each. -->

**One way planning.md helped during implementation:**
Writing out the per-tool failure modes in advance made the planning loop much simpler to implement. Because I had already decided that `search_listings` returning `[]` is a hard stop while an empty wardrobe is an "adapt and continue" case, I knew exactly where to branch in `run_agent` and never accidentally called `suggest_outfit` with empty input. 

**One divergence from spec and why:**
The original plan didn't specify how the natural-language query gets turned into `description`, `size`, and `max_price`. During implementation I added a regex-based `_parse_query` helper in `agent.py` using Claude to extract those fields (e.g. pulling `30.0` from "under $30" and `M` from "size M"). I chose regex over an extra LLM call because it's deterministic and instance, which keeps the loop predictable and easier to test.

---

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
