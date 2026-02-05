from tools import places_text_search

result = places_text_search.invoke({
    "place_name": "CN Tower",
    "city": "Toronto"
})

print(result)
