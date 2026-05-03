#checks if price is cheap
import json
from datetime import datetime


def under_price_api(flights, price):
    result = [
        flight for flight in flights
        if flight.get("price") <= price
    ]
    if len(result) == 0:
        return None

    return result

def cheapest_flight_api(flights):

    result = sorted(flights, key=lambda flight: flight.get("price"))
    return result[0]


def direct_flights_api(flights):
    result =[
        flight for flight in flights
        if flight.get("stops") == 0
    ]
    if len(result) == 0:
        return None
    return result


def latest_price_drop_of_cheapest_flight(flights, departure, to, flight_date, querystring):
    target_date = datetime.strptime(flight_date, "%Y-%m-%d").date()

    matching = [
        flight for flight in flights
        if departure == flight.get("from")
        and to == flight.get("to")
        and datetime.strptime(
            flight.get("departure_time"), "%Y-%m-%d %H:%M"
        ).date() == target_date
    ]

    if not matching:
        return None

    times = {}

    for flight in matching:
        checked_date = datetime.strptime(
            flight.get("checked_at"), "%Y-%m-%d %H:%M:%S"
        ).date()

        if checked_date not in times:
            times[checked_date] = []

        times[checked_date].append(flight)

    check_dates = sorted(times.keys())

    if len(check_dates) < 2:
        return None

    latest_date = check_dates[-1]
    previous_date = check_dates[-2]

    latest_cheapest = min(times[latest_date], key=lambda flight: flight["price"])
    previous_cheapest = min(times[previous_date], key=lambda flight: flight["price"])

    price_difference = latest_cheapest["price"] - previous_cheapest["price"]

    return {
        "route": f"{departure} → {to}",
        "flight_date": str(target_date),
        "previous_check_date": str(previous_date),
        "latest_check_date": str(latest_date),
        "previous_price": previous_cheapest["price"],
        "latest_price": latest_cheapest["price"],
        "difference": price_difference,
        "price_dropped": price_difference < 0,
        "previous_cheapest_flight": previous_cheapest,
        "latest_cheapest_flight": latest_cheapest,
    }
def latest_price_drop_of_specific_flight():
    pass