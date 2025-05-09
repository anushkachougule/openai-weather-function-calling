import os
import json
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# geocoding using Open-Meteo
def geocode_location(location):
    city = location.split(",")[0].strip()  # Remove ", USA" etc. if present
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    response = requests.get(url)
    data = response.json()

    if "results" in data and data["results"]:
        lat = data["results"][0]["latitude"]
        lon = data["results"][0]["longitude"]
        return lat, lon
    return None, None

# Weather retrieval from Open-Meteo
def get_weather_from_api(location, datetime=None):
    lat, lon = geocode_location(location)
    if not lat or not lon:
        return {"error": f"Could not find coordinates for '{location}'."}

    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto"
    }

    if datetime:
        params["start_date"] = datetime
        params["end_date"] = datetime
        params["daily"] = "temperature_2m_max,temperature_2m_min,weathercode"
    else:
        params["current"] = "temperature_2m,weathercode"

    url = "https://api.open-meteo.com/v1/forecast"
    response = requests.get(url, params=params)
    data = response.json()

    # Forecasted weather
    if datetime:
        if "daily" not in data or not data["daily"]["temperature_2m_max"]:
            return {"error": "The weather forecast for that date is not available. Please try a closer date."}

        return {
            "location": location,
            "datetime": datetime,
            "temperature_high": f"{data['daily']['temperature_2m_max'][0]}°C",
            "temperature_low": f"{data['daily']['temperature_2m_min'][0]}°C",
            "conditions": f"Weather code: {data['daily']['weathercode'][0]}"
        }
    else:
        if "current" not in data or "temperature_2m" not in data["current"]:
            return {"error": "Could not retrieve current weather data."}

        return {
            "location": location,
            "temperature": f"{data['current']['temperature_2m']}°C",
            "conditions": f"Weather code: {data['current']['weathercode']}"
        }

# OpenAI function schema
functions = [
    {
        "name": "get_weather_from_api",
        "description": "Get real-time or forecast weather for a specific location and optional date.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country, e.g., 'Paris, France'",
                },
                "datetime": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (optional)",
                },
            },
            "required": ["location"],
        },
    }
]

# GPT interaction and function calling
def ask_weather_bot(user_query):
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[{"role": "user", "content": user_query}],
        functions=functions,
        function_call="auto"
    )

    message = response.choices[0].message

    if message.function_call:
        args = json.loads(message.function_call.arguments)
        location = args.get("location")
        datetime_value = args.get("datetime")

        if not location:
            return "I'm sorry, I couldn't find a location in your question."

        print(f"Location: {location}")
        if datetime_value:
            print(f"Date requested: {datetime_value}")

        result = get_weather_from_api(location, datetime_value)

        if "error" in result:
            return result["error"]

        followup = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {"role": "user", "content": user_query},
                message,
                {"role": "function", "name": "get_weather_from_api", "content": json.dumps(result)},
            ]
        )

        return followup.choices[0].message.content
    else:
        return message.content

# Test cases
if __name__ == "__main__":
    test_queries = [
        "What's the weather in New York City today?",
        "What's the weather in Tokyo on 2025-05-10?",
        "Will it rain in Singapore tomorrow?",
        "Hi!",
        "Tell me the weather in Boston.",
        "What's the weather on Friday?"  
    ]

    for query in test_queries:
        print(f"\nUser: {query}")
        print(f"Bot: {ask_weather_bot(query)}")
