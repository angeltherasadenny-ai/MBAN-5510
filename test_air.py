from tools import get_air_quality

print(get_air_quality.invoke({
    "lat": 43.6425662,
    "lon": -79.3870568,
    "hours": 24
}))
