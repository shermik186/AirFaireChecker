# gets flight data
import requests
from dotenv import load_dotenv
import os
from pathlib import Path

def get_api_key():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
    api_key = os.getenv("API_KEY")
    return api_key

def get_api_host():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
    api_host = os.getenv("API_HOST")
    return api_host

def get_data(querystring):
    url = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"
    api_key = get_api_key()
    api_host = get_api_host()

    if not api_key or not api_host:
        raise ValueError("Missing API_KEY or API_HOST in .env file")

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)

        print(response.status_code)
        return response.json()

    except requests.exceptions.Timeout:
        print("API request timed out")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"API returned an error: {e}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

    except ValueError:
        print("API response was not valid JSON")
        return None


def get_locations():
    url = "https://google-flights2.p.rapidapi.com/api/v1/getLocations"
    api_key = get_api_key()
    api_host = get_api_host()

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host

    }
    response = requests.get(url, headers=headers)

    print(response.status_code)
    return response.json()



