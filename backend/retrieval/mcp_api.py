import os
import requests

MARKET_API_URL = os.getenv("MARKET_API_URL", "https://api.example.com/market")
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.example.com/weather")
PEST_API_URL = os.getenv("PEST_API_URL", "https://api.example.com/pest")
SCHEME_API_URL = os.getenv("SCHEME_API_URL", "https://api.example.com/scheme")

MARKET_API_KEY = os.getenv("MARKET_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PEST_API_KEY = os.getenv("PEST_API_KEY")
SCHEME_API_KEY = os.getenv("SCHEME_API_KEY")

def get_market_info(query):
    params = {"query": query, "apikey": MARKET_API_KEY}
    try:
        resp = requests.get(MARKET_API_URL, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {"market_info": "Market info not available."}

def get_weather_info(query):
    params = {"query": query, "apikey": WEATHER_API_KEY}
    try:
        resp = requests.get(WEATHER_API_URL, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {"weather_info": "Weather info not available."}

def get_pest_info(query):
    params = {"query": query, "apikey": PEST_API_KEY}
    try:
        resp = requests.get(PEST_API_URL, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {"pest_info": "Pest info not available."}

def get_scheme_info(query):
    params = {"query": query, "apikey": SCHEME_API_KEY}
    try:
        resp = requests.get(SCHEME_API_URL, params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {"scheme_info": "Scheme info not available."}
# TODO make the it return multiple info for each intent
def get_market_weather_pest_info(intent, query=""):
    if intent == "market_info":
        return get_market_info(query)
    elif intent == "weather_update":
        return get_weather_info(query)
    elif intent == "pest_alert":
        return get_pest_info(query)
    elif intent == "scheme_info":
        return get_scheme_info(query)
    else:
        return {"info": "No external API data for this intent."}