import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

# Load .env file
load_dotenv(override=True)

GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

@tool
def places_text_search(place_name: str, city: str) -> dict:
    """
    Convert a place name into address and latitude/longitude using Google Places Text Search API.
    Includes debug info if something goes wrong.
    """

    query = f"{place_name}, {city}"

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": GOOGLE_KEY
    }

    response = requests.get(url, params=params, timeout=20)
    data = response.json()

    # DEBUG: if Google returns no results or an error
    if not data.get("results"):
        return {
            "error": "No results found",
            "status": data.get("status"),
            "error_message": data.get("error_message"),
            "query": query
        }

    top = data["results"][0]
    location = top["geometry"]["location"]

    return {
        "name": top.get("name"),
        "address": top.get("formatted_address"),
        "lat": location["lat"],
        "lon": location["lng"]
    }

@tool
def get_weather(lat: float, lon: float, days: int = 2) -> dict:
    """
    Get daily weather forecast using Google Weather API (forecast.days).
    """
    url = "https://weather.googleapis.com/v1/forecast/days:lookup"
    params = {
        "key": GOOGLE_KEY,
        "location.latitude": lat,
        "location.longitude": lon,
        "days": days,
    }

    r = requests.get(url, params=params, timeout=20)
    content_type = r.headers.get("Content-Type", "")

    # If not JSON, return debug info
    if "application/json" not in content_type:
        return {
            "error": "Non-JSON response from Weather API",
            "http_status": r.status_code,
            "content_type": content_type,
            "text_preview": r.text[:300],
            "url": r.url,
        }

    data = r.json()

    # Google-style error payload
    if "error" in data:
        return {
            "error": "Weather API returned error",
            "details": data["error"],
            "url": r.url,
        }

    # Return a small useful subset for your assignment
    forecast_days = data.get("forecastDays", [])
    if not forecast_days:
        return {"error": "No forecastDays in response", "raw": data}

    today = forecast_days[0]
    daytime = today.get("daytimeForecast", {}).get("weatherCondition", {}).get("description", {}).get("text")
    nighttime = today.get("nighttimeForecast", {}).get("weatherCondition", {}).get("description", {}).get("text")

    # Temps may appear in different places depending on response; keep raw if unsure
    return {
        "ok": True,
        "today_day": daytime,
        "today_night": nighttime,
        "raw_preview": str(today)[:800],
    }

import os
import requests
import datetime as dt
from langchain_core.tools import tool

@tool
def get_air_quality(lat: float, lon: float, hours: int = 24) -> dict:
    """
    Get air quality hourly forecast using Google Air Quality API.
    Returns AQI category + whether to wear a mask.
    """
    if hours < 1:
        hours = 1
    if hours > 96:
        hours = 96

    # Align to next full hour
    now = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start_dt = now + dt.timedelta(hours=1)
    end_dt = start_dt + dt.timedelta(hours=hours)

    url = "https://airquality.googleapis.com/v1/forecast:lookup"
    params = {"key": os.getenv("GOOGLE_MAPS_API_KEY")}
    body = {
        "location": {"latitude": lat, "longitude": lon},
        "period": {"startTime": start_dt.isoformat() + "Z", "endTime": end_dt.isoformat() + "Z"},
        "languageCode": "en",
    }

    r = requests.post(url, params=params, json=body, timeout=20)

    if "application/json" not in (r.headers.get("Content-Type") or ""):
        return {
            "error": "Non-JSON response from Air Quality API",
            "http_status": r.status_code,
            "text_preview": r.text[:300],
        }

    data = r.json()

    if "error" in data:
        return {"error": "Air Quality API returned error", "details": data["error"]}

    hourly = data.get("hourlyForecasts", [])
    if not hourly:
        return {"error": "No hourlyForecasts returned", "raw_preview": str(data)[:600]}

    first = hourly[0]
    indexes = first.get("indexes", [])

    aqi = None
    category = None
    for idx in indexes:
        if idx.get("code") in ("uaqi", "us_aqi", "aqi"):
            aqi = idx.get("aqi")
            category = idx.get("category")
            break

    # Mask logic (simple)
    mask_needed = False
    if isinstance(aqi, (int, float)) and aqi >= 100:
        mask_needed = True
    if isinstance(category, str) and "unhealthy" in category.lower():
        mask_needed = True

    return {
        "ok": True,
        "first_hour": first.get("dateTime"),
        "aqi": aqi,
        "category": category,
        "mask_needed": mask_needed,
        "window_hours": hours,
    }
