import re
import random
from typing import List, Dict, Any
from dotenv import load_dotenv

from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from tools import places_text_search, get_weather, get_air_quality

load_dotenv(override=True)

SYSTEM = """You are a travel-planning assistant.

You will be given a raw itinerary text in this format:
City1: <CityName> <YYYY-MM-DD> <PlaceName>;<time> <PlaceName>;<time> ...
City2: <CityName> <YYYY-MM-DD> ...

Your job:
1) Parse into cities, dates, and time slots.
2) Ensure each place has a real address and coordinates (resolve with Places tool if missing).
3) Summarize weather (day/night condition text is enough).
4) Summarize air quality (AQI + category if available) and decide if a mask is needed.
5) Output a clean itinerary and compute TOTAL masks for the whole trip.

If user asks follow-ups, use memory (thread_id) and modify the existing plan rather than restarting.
Keep output structured and easy to read.
"""


# -------------------------
# 0) Hard-mode: structured output attraction generator
# -------------------------
class AttractionList(BaseModel):
    places: List[str] = Field(
        description="4 to 6 popular tourist attractions (names only)."
    )


@tool
def generate_attractions(city: str) -> dict:
    """
    Generate attraction NAMES for a city using structured output.
    Returns {"places": [...]}.
    """
    generator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured = generator_llm.with_structured_output(AttractionList)

    result: AttractionList = structured.invoke(
        f"Give 4 to 6 popular tourist attractions in {city}. "
        f"Return names only. No addresses. No extra text."
    )
    return {"places": result.places}


# -------------------------
# 1) Parse hard-mode input
# -------------------------
def parse_hard_input(text: str) -> List[Dict[str, Any]]:
    """
    Example:
    City1: Toronto 2026-01-31 CN Tower;8am-9am Royal Ontario Museum;10am-11am
    City2: Chicago 2026-02-01 Millennium Park;9am-10am Art Institute of Chicago;11am-12pm

    Also supports:
    City1: Toronto 2026-01-31
    (then we auto-generate attractions)
    """
    blocks = re.split(r"City\d+\s*:\s*", text.strip())
    blocks = [b.strip() for b in blocks if b.strip()]

    trip: List[Dict[str, Any]] = []

    for b in blocks:
        parts = b.split()
        if len(parts) < 2:
            continue

        city = parts[0]
        date = parts[1]
        rest = " ".join(parts[2:]).strip()

        pattern = r"([^;]+);([0-9:apmAPM\- ]+)"
        matches = re.findall(pattern, rest)

        slots = []
        for name, time_range in matches:
            slots.append({"name": name.strip(), "time": time_range.strip()})

        trip.append({"city": city, "date": date, "slots": slots})

    return trip


# -------------------------
# 2) Build plan (tool calls)
# -------------------------
def build_plan(trip: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    For each place: resolve name -> address, lat, lon
    For each city/day: get weather + air quality using first resolved location
    Compute total masks (1 per day if mask_needed_today)
    """
    output: Dict[str, Any] = {"days": [], "total_masks": 0}

    for day in trip:
        city = day["city"]
        date = day["date"]

        # HARD MODE:
        # If no slots were provided, generate attraction names + random time slots
        if not day.get("slots"):
            gen = generate_attractions.invoke({"city": city})

            possible_times = [
                "9:00 AM – 10:30 AM",
                "10:30 AM – 12:00 PM",
                "1:00 PM – 2:30 PM",
                "3:00 PM – 4:30 PM",
                "5:00 PM – 6:30 PM",
                "7:00 PM – 8:30 PM",
            ]

            # Stable randomness per city (so your demo doesn't change every run)
            random.seed(city)

            used_times = set()
            day["slots"] = []

            for name in gen.get("places", []):
                available = [t for t in possible_times if t not in used_times]
                if not available:
                    available = possible_times

                time_slot = random.choice(available)
                used_times.add(time_slot)

                day["slots"].append({"name": name, "time": time_slot})

        resolved_slots = []
        city_lat = None
        city_lon = None

        for s in day.get("slots", []):
            place = places_text_search.invoke({"place_name": s["name"], "city": city})

            if place.get("error"):
                resolved_slots.append(
                    {"time": s.get("time", ""), "name": s["name"], "error": place.get("error")}
                )
            else:
                resolved_slots.append(
                    {
                        "time": s.get("time", ""),
                        "name": place.get("name") or s["name"],
                        "address": place.get("address"),
                        "lat": place.get("lat"),
                        "lon": place.get("lon"),
                    }
                )
                if city_lat is None and city_lon is None:
                    city_lat = place.get("lat")
                    city_lon = place.get("lon")

        weather = None
        air = None
        mask_today = False

        if city_lat is not None and city_lon is not None:
            weather = get_weather.invoke({"lat": city_lat, "lon": city_lon, "days": 2})
            air = get_air_quality.invoke({"lat": city_lat, "lon": city_lon, "hours": 24})
            mask_today = bool(air.get("mask_needed"))

        if mask_today:
            output["total_masks"] += 1

        output["days"].append(
            {
                "city": city,
                "date": date,
                "weather": weather,
                "air_quality": air,
                "mask_needed_today": mask_today,
                "schedule": resolved_slots,
            }
        )

    return output


# -------------------------
# 3) Agent (memory enabled)
# -------------------------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
checkpointer = MemorySaver()

agent = create_agent(
    model=llm,
    tools=[generate_attractions, places_text_search, get_weather, get_air_quality],
    system_prompt=SYSTEM,
    checkpointer=checkpointer,
)


def run_agent(user_text: str, thread_id: str = "trip-thread-1") -> str:
    trip = parse_hard_input(user_text)
    plan = build_plan(trip)

    prompt = f"""
Format the following PLAN_DATA as a final itinerary.

Requirements:
- Show TOTAL masks needed at the top.
- For each city/date: show weather summary (today_day/today_night if present), air quality (aqi/category if present), and mask_needed_today.
- Then list each time slot with the attraction name + full address.
- Keep it clean and readable.

PLAN_DATA:
{plan}
"""

    result = agent.invoke(
        {
            "messages": [
                ("user", prompt),
            ]
        },
        config={"configurable": {"thread_id": thread_id}},
    )

    return result["messages"][-1].content


if __name__ == "__main__":
    hard_input = input("Paste hard-mode itinerary text:\n")
    print("\n" + run_agent(hard_input))


def main():
    hard_input = input('Paste hard-mode itinerary text:\n')
    print('\n' + run_agent(hard_input))

