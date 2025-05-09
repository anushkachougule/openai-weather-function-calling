from openai import OpenAI
import os
import json
import random

# seting the key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Mock function to return weather info
def get_current_weather(location, datetime = None):
    sample_weather_data ={
        "New York": {"temperature": "12°C", "conditions": "Cloudy"},
        "Los Angeles": {"temperature": "25°C", "conditions": "Sunny"},
        "Chicago": {"temperature": "8°C", "conditions": "Windy"},
        "Paris": {"temperature": "16°C", "conditions": "Rainy"},
        "Tokyo": {"temperature": "19°C", "conditions": "Clear"},
        "San Francisco": {"temperature": "14°C", "conditions": "Foggy"},
        "London": {"temperature": "10°C", "conditions": "Drizzle"},
    }

    # Fall back values for unknown locations
    if location in sample_weather_data:
        weather = sample_weather_data[location]
    else:
        weather={
            "temperature": random.choice(["18°C", "20°C", "22°C", "24°C"]),
            "conditions" : random.choice(["Sunny", "Cloudy", "Rainy", "Windy", "Partly Cloudy"])
        }

    return {
        "location": location,
        "datetime": datetime or "current time",
        "temperature": weather["temperature"],
        "conditions": weather["conditions"],
    }

# Define the function schema for OpenAI
functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and state, e.g., 'New York, NY'",
                },
                "datetime": {
                    "type": "string",
                    "description": "Date or time reference, e.g., 'tomorrow' or '2025-05-09'",
                },
            },
            "required": ["location"],
        },
    }
]

def ask_weather_bot(user_query):
    # Ask the OpenAI model to analyze the user's question and decide if it should call a function
    response = client.chat.completions.create(
    model="gpt-4-0613",
    messages=[
        {"role": "user", "content": user_query}
    ],
    functions=functions,
    function_call="auto"
    )

    message = response.choices[0].message


    if message.function_call is not None:
        func_name = message.function_call.name
        arguments = json.loads(message.function_call.arguments)
        location = arguments.get("location")
        datetime_value = arguments.get("datetime")

        # Fallback if location is missing
        if not location:
            return "Sorry, I couldn't find a location in your question."

        result = get_current_weather(location, datetime=datetime_value)

        # Step 2: Ask the model to generate a final response
        followup = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {"role": "user", "content": user_query},
                message,
                {"role": "function", "name": func_name, "content": json.dumps(result)},
            ]
        )

        return followup.choices[0].message.content
    else:
        return message.content
            
    

# Test cases
if __name__ == "__main__":
    queries = [
        "What's the weather in Paris tomorrow",
        "Can you tell me the weather in London on Saturday?",
        "Is it sunny in Berlin today?",
        "How's the weather in Tokyo this weekend?",
        "What's the weather tomorrow?",
        "Tell me the weather in Singapore",
        "What should I wear today?",
        "Is it hot next week?"
    ]

    for query in queries:
        print(f"User: {query}")
        print(f"Bot: {ask_weather_bot(query)}\n")
