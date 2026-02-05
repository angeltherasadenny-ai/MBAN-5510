from tools import get_weather

# CN Tower coordinates
result = get_weather.invoke({
    "lat": 43.6425662,
    "lon": -79.3870568
})

print(result)
