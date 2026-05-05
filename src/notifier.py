from telegram import Bot
from datetime import datetime
from dotenv import load_dotenv
import os
from pathlib import Path

def get_chat_id():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
    chat_id = os.getenv("CHAT_ID")
    return chat_id

def get_token():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path)
    token = os.getenv("TELEGRAM_TOKEN")
    return token

async def telegram_message(text):
    token = get_token()
    bot = Bot(token)
    chat_id = get_chat_id()
    await bot.send_message(chat_id=chat_id, text=text)

def cheapest_flight_message(flight):
    # segments info
    segment_info = ""
    for i, segment in enumerate(flight["segments"], 1):
        segment_info += (
            f"\n{i}. {segment['from']} → {segment['to']}"
            f"\n   Airline: {segment['airline']}"
            f"\n   Departure: {segment['time']}"
            f"\n   Duration: {segment['duration_min']} min\n"
        )

    #calculatng the time of the flight
    departure = datetime.strptime(flight["departure_time"], "%Y-%m-%d %H:%M")
    arrival = datetime.strptime(flight["arrival_time"], "%Y-%m-%d %H:%M")

    overall_duration = arrival - departure
    overall_minutes = int(overall_duration.total_seconds() / 60)


    time = f"{overall_minutes // 60}h {overall_minutes % 60}min"  # 12h 0mi


    # stops text
    stops_text = "Direct flight" if flight["stops"] == 0 else f"{flight['stops']} stop(s)"

    message = f"""
    ✈️ Cheap Flight Found!
    
    📍 Route: {flight["from"]} → {flight["to"]}
    📅 Departure: {flight["departure_time"]}
    🕒 Arrival: {flight["arrival_time"]}
    ⏱ Duration: {time}
    🔁 Stops: {stops_text}
    👤 Passengers: {flight["nmb_of_adults"]} adults
    💰 Price: {flight["price"]} CZK

    👜 Carry-on bag: {"Yes" if flight["bags"]["carry_on"] else "No"}
    🧳 Checked bag: {flight["bags"]["checked"] if flight["bags"]["checked"] else "Not included"}

    ✈️ Flight Segments:
    {segment_info}

    Checked at: {flight["checked_at"]}
    """
    return message.strip()

def price_drop_message(flight):
    latest = flight["latest_cheapest_flight"]
    previous = flight["previous_cheapest_flight"]

    # segments info (same style as your function)
    segment_info = ""
    for i, segment in enumerate(latest["segments"], 1):
        segment_info += (
            f"\n{i}. {segment['from']} → {segment['to']}"
            f"\n   Airline: {segment['airline']}"
            f"\n   Departure: {segment['time']}"
            f"\n   Duration: {segment['duration_min']} min\n"
        )

    # total duration
    departure = datetime.strptime(latest["departure_time"], "%Y-%m-%d %H:%M")
    arrival = datetime.strptime(latest["arrival_time"], "%Y-%m-%d %H:%M")

    overall_minutes = int((arrival - departure).total_seconds() / 60)
    time = f"{overall_minutes // 60}h {overall_minutes % 60}min"

    # stops text
    stops_text = "Direct flight" if latest["stops"] == 0 else f"{latest['stops']} stop(s)"

    # price logic
    difference = flight["difference"]
    abs_diff = abs(difference)

    if flight["price_dropped"]:
        header = "📉 Price Drop Alert!"
        change_text = f"The price dropped by {abs_diff} CZK"
    elif difference > 0:
        header = "📈 Price Increase Alert!"
        change_text = f"The price increased by {abs_diff} CZK"
    else:
        header = "➖ Price Update"
        change_text = "No price change"

    message = f"""
    {header}

    📍 Route: {flight["route"]}
    📅 Flight date: {flight["flight_date"]}

    💰 Previous price: {flight["previous_price"]} CZK
    💰 Current price: {flight["latest_price"]} CZK
    🔄 Change: {difference} CZK

    {change_text}

    ✈️ Current Cheapest Flight:
    📅 Departure: {latest["departure_time"]}
    🕒 Arrival: {latest["arrival_time"]}
    ⏱ Duration: {time}
    🔁 Stops: {stops_text}
    👤 Passengers: {latest["nmb_of_adults"]} adults
    💰 Price: {latest["price"]} CZK

    👜 Carry-on bag: {"Yes" if latest["bags"]["carry_on"] else "No"}
    🧳 Checked bag: {latest["bags"]["checked"] if latest["bags"]["checked"] else "Not included"}

    ✈️ Flight Segments:
    {segment_info}

    🕓 Compared checks:
    Previous: {flight["previous_check_date"]}
    Latest: {flight["latest_check_date"]}
    """

    return message.strip()

def not_working_api(departure,arrival,date):
    message = f"""
    API ERROR ⚠️ 
    📍 Route: {departure} → {arrival}
    📅 Date: {date}
    Unfortunately, our API wasn't able to get information about your route.
    We hope that this will not happen again in the future.
    AIR FAIR CHECKER developer
    """

    return message.strip()

def not_enough_data_for_price_drop(departure,arrival,date):
    message = f"""
        NOT ENOUGH DATA ⛔ 
        📍 Route: {departure} → {arrival}
        📅 Date: {date}
        Unfortunately, we don´t have enough data yet to provide you with price drop/increase.
        Tomorrow we will able to do so.
        Thank you for your understanding.
        AIR FAIR CHECKER developer
        """

    return message.strip()

def no_flights(departure,arrival,date):
    message = f"""
    ✈️No Cheap Flight Found!
    📍 Route: {departure} → {arrival}
    📅 Date: {date}
    Unfortunately, no cheap flight have been found on your route.
    We wish you more luck next time.
    AIR FAIR CHECKER developer
    """

    return message.strip()

def storage_error(departure,arrival,date):
    message = f""" 
    STORAGE ERROR ⛔
    📍 Route: {departure} → {arrival}
    📅 Date: {date}
    Problem with storage
    """
    return message.strip()