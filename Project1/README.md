# Travel Planner Agent (LangChain + LangGraph) - Project1
## Author: **Angel Denny**


This project is a travel-planning assistant built using **LangChain** and **LangGraph**.  
It takes a raw “hard-mode” itinerary input, resolves real attraction addresses using **Google Places**, retrieves **Weather** and **Air Quality** data using Google APIs, and outputs a clean final itinerary.

It also calculates the **TOTAL masks needed** for the trip based on air quality.

---

## Features

- Parses a hard-mode itinerary input format (City + Date + Place + Time)
- Uses Google Places API to resolve:
  - Attraction name
  - Full address
  - Latitude/Longitude
- Uses Google Weather API to get daily forecast summaries
- Uses Google Air Quality API to retrieve AQI and category
- Automatically decides whether a mask is needed (simple logic)
- Outputs a clean itinerary summary
- Supports a “hard mode” where attractions can be auto-generated if no slots are given
- Includes test scripts for each tool

---

## Tech Stack

- Python
- LangChain (v1.2+)
- LangGraph (memory checkpointing)
- OpenAI Chat Model (`gpt-4o-mini`)
- Google Places Text Search API
- Google Weather API
- Google Air Quality API
- uv (package + environment management)

---

## Project Structure


Got you — the one above is *good*, but it’s still missing a few things that make a README feel truly “complete” (like prerequisites, API setup steps, exact commands, troubleshooting, and how to get Google keys).

Below is a **fully instructed README.md** that someone can follow even if they’ve never seen your project before.

---

## ✅ FULL README.md (Copy-Paste)

```md
# Project 1 — Travel Planner Agent (LangChain + LangGraph)

A travel-planning assistant built with **LangChain** + **LangGraph** that:
- Parses a raw itinerary input (hard-mode format)
- Resolves real attraction addresses + coordinates using **Google Places**
- Fetches **Weather** using Google Weather API
- Fetches **Air Quality (AQI)** using Google Air Quality API
- Decides if a **mask is needed**
- Outputs a clean itinerary + total masks required for the full trip

---

## Demo Output (What the program generates)

The final output includes:

- **TOTAL masks needed** for the entire trip  
- For each city/date:
  - Weather summary (day + night)
  - Air quality summary (AQI + category)
  - Mask needed today (True/False)
  - Schedule with attraction name + full address

---

## Project Files

```

.
├── agent_app_fixed.py      # Main agent (parsing, tool calls, formatting)
├── tools.py                # Google Places, Weather, Air Quality tools
├── main.py                 # Loads .env and confirms API key exists
├── test_tool.py            # Tests Google Places tool
├── test_weather.py         # Tests Weather tool
├── test_air.py             # Tests Air Quality tool
├── pyproject.toml          # uv dependency file
├── .env                    # Your personal API keys (NOT uploaded)
├── .env.example            # Template for others (uploaded)
└── README.md

````

---

## Requirements

You must have:

- Python 3.10+ (recommended)
- uv installed
- A Google Cloud API key with these APIs enabled:
  - Places API (Text Search)
  - Weather API
  - Air Quality API
- An OpenAI API key

---

## Step 1 — Install uv

### Windows (PowerShell)
```powershell
pip install uv
````

### macOS/Linux

```bash
pip install uv
```

Check it works:

```bash
uv --version
```

---

## Step 2 — Clone the Repository

```bash
git clone <your-repo-link>
cd <your-repo-folder>
```

---

## Step 3 — Environment Variables (.env)

This project requires API keys.
Use the file titled "env.template" to insert your keys

---
### Create your `.env` file (your real keys)

Create:

```
.env
```

Paste:

```env
GOOGLE_MAPS_API_KEY=your_real_google_key_here
OPENAI_API_KEY=your_real_openai_key_here
```

---

## Step 4 — Install Dependencies

This project uses `uv` and installs dependencies using `pyproject.toml`.

```bash
uv sync
```

---

## Step 5 — Confirm Your API Keys Load

Run:

```bash
uv run python main.py
```

Expected output example:

```
Looking for .env at: .../.env
Google key loaded: True
Google key starts with: AIzaSy
```

If it says `False`, your `.env` is missing or not in the correct folder.

---

## Step 6 — Run the Agent

Run:

```bash
uv run python agent_app_fixed.py
```

You will see:

```
Paste hard-mode itinerary text:
```

---

## Hard-Mode Input Format

### Example (with attractions + times)

```
City1: Toronto 2026-01-31 CN Tower;8am-9am Royal Ontario Museum;10am-11am
City2: Chicago 2026-02-01 Millennium Park;9am-10am Art Institute of Chicago;11am-12pm
```

---

### Example (NO attractions provided — auto generation)

```
City1: Toronto 2026-01-31
City2: Chicago 2026-02-01
```

If no attractions are provided, the program automatically:

* generates 4–6 attractions per city using structured output
* assigns time slots automatically

---

## How the Agent Works

### 1) Parse input

Extracts:

* City
* Date
* (Optional) place + time slots

### 2) Resolve attraction details

Uses Google Places Text Search API to get:

* formatted address
* coordinates

### 3) Get weather + air quality

Uses:

* Google Weather API
* Google Air Quality API

### 4) Mask decision

Mask needed if:

* AQI >= 100 OR
* category includes "unhealthy"

### 5) Output formatting

Outputs a clean readable itinerary and total masks.

---

## Tool Tests (Recommended)

### Test Places Search

```bash
uv run python test_tool.py
```

### Test Weather

```bash
uv run python test_weather.py
```

### Test Air Quality

```bash
uv run python test_air.py
```

---

## Troubleshooting

### ❌ Problem: `Google key loaded: False`

Fix:

* Make sure `.env` is in the same folder as your python files
* Make sure your `.env` is named exactly `.env`
* Make sure you saved the file properly

---

### ❌ Problem: “No results found” from Places API

Fix:

* Try a more specific attraction name
* Example: use `"CN Tower"` instead of `"Tower"`

---

### ❌ Problem: Weather API returns Non-JSON response

This usually means:

* Weather API not enabled in Google Cloud
* Key does not have access
* Billing not enabled

---

### ❌ Problem: Air Quality API returns error

This usually means:

* Air Quality API not enabled
* Incorrect API permissions
* Billing not enabled

---

## Google API Setup (How to Get Your Key)
1. Go to Google Cloud Console
2. Create a project
3. Enable billing (required for most Google APIs)
4. Enable these APIs:

   * Places API
   * Weather API
   * Air Quality API
5. Create an API key under:
   APIs & Services → Credentials
6. Copy the key into your `.env`
---




