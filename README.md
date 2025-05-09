# LLM Weather Chatbot
This project demonstrates how to build a weather information assistant using OpenAI's function calling API. The chatbot can respond to user queries about the weather for a given location — with optional date/time — and return either simulated or real-time weather information using the Open-Meteo API.


## Project Structure

| File | Description |
|------|-------------|
| `weather_agent_part1.py` | Part 1 – Basic weather assistant using mock data and location-only queries |
| `weather_agent_part2.py` | Part 2 – Enhanced version with support for date/time (e.g., "tomorrow", "next Monday") |
| `weather_agent_api.py` | Final version using Open-Meteo's real weather API for both current and forecast data |


## Features

- Detects weather-related questions using OpenAI’s function calling
- Parses user-provided location (e.g., “New York City”)
- Supports optional time references like “tomorrow” or “2025-05-09”
- Calls Open-Meteo API for real-time or forecast weather data
- GPT generates natural, conversational responses
- Fallback handling for missing or ambiguous inputs


## Background
This project was developed as part of an assignment for INST750 (University of Maryland). It explores practical applications of tool use with Large Language Models (LLMs), specifically OpenAI’s function calling framework.

Resource used:
OpenAI Function Calling Documentation, Course demo videos and lecture notes


## Setup Instructions

1. **Clone this repository:**
   ```bash
   git clone https://github.com/anushkachougule/openai-weather-function-calling.git
   cd openai-weather-function-calling

