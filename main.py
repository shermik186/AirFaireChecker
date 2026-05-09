import asyncio
import sqlite3

from config import QUERYSTRINGS
from src.analyzer import cheapest_flight_api, latest_price_drop_of_cheapest_flight
from src.database import create_tables, insert_flights, get_flights_by_route, clean_old_flights
from src.fetcher import get_data
from src.notifier import (telegram_message, cheapest_flight_message,
                          price_drop_message, not_working_api, not_enough_data_for_price_drop,
                          no_flights, storage_error)
from src.storage import convert_to_json


def main():

    for querystring in QUERYSTRINGS:

        create_tables()

        api_data = get_data(querystring)
        print(api_data)
        departure, arrival = querystring.get("departure_id"), querystring.get("arrival_id")


        if api_data is None:
            # sends an error to user about not working api
            message = not_working_api(departure, arrival, querystring.get("outbound_date"))
            asyncio.run(telegram_message(message))
            continue

        api_data = convert_to_json(api_data,querystring)


        if not api_data:
            #data have been converted to a json format of only important data, if empty -> no flights were found
            message = no_flights(departure, arrival, querystring.get("outbound_date"))
            asyncio.run(telegram_message(message))
            continue

        #save_to_specific_file(api_data, departure, arrival), under is new sqlite version
        insert_flights(api_data)

        #getting the cheapest flight
        cheapest = cheapest_flight_api(api_data)
        cheapest_message = cheapest_flight_message(cheapest)
        asyncio.run(telegram_message(cheapest_message))



        #getting the data necessary for price drop function
        try:
            #load_data = load_from_specified_json(departure,arrival)
            load_data = get_flights_by_route(departure, arrival)

        except sqlite3.Error:
            # database/storage error
            message = storage_error(departure, arrival, querystring.get("outbound_date"))
            asyncio.run(telegram_message(message))
            continue

        if not load_data:
            # no historical data yet -> same message as missing file before
            message = not_enough_data_for_price_drop(
                departure,
                arrival,
                querystring.get("outbound_date")
            )
            asyncio.run(telegram_message(message))
            continue

        price_drop_data = latest_price_drop_of_cheapest_flight(load_data,departure, arrival, querystring.get("outbound_date"),querystring)

        if price_drop_data is None:
            #informs about not having enough data for price drop info
            message = not_enough_data_for_price_drop(departure, arrival,querystring.get("outbound_date"))
            asyncio.run(telegram_message(message))
            continue

        price_drop_msg = price_drop_message(price_drop_data)
        asyncio.run(telegram_message(price_drop_msg))

    clean_old_flights()


if __name__ == "__main__":
    main()









