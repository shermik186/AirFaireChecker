import json
import asyncio

from src.fetcher import get_data
from src.storage import  convert_to_json, save_to_specific_file,load_from_specified_json,clean_all_files
from src.analyzer import under_price_api, cheapest_flight_api,direct_flights_api,latest_price_drop_of_cheapest_flight
from config import QUERYSTRINGS
from src.notifier import (telegram_message,cheapest_flight_message,
price_drop_message, not_working_api, not_enough_data_for_price_drop,
no_flights,storage_error)



def main():
    for querystring in QUERYSTRINGS:

        api_data = get_data(querystring)
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

        save_to_specific_file(api_data,departure,arrival)

        #getting the cheapest flight
        cheapest = cheapest_flight_api(api_data)
        cheapest_message = cheapest_flight_message(cheapest)
        asyncio.run(telegram_message(cheapest_message))



        #getting the data necessary for price drop function
        try:
            load_data = load_from_specified_json(departure,arrival)

        except FileNotFoundError:
            #no file -> not ebough data
            message = not_enough_data_for_price_drop(departure,arrival,querystring.get("outbound_date"))
            asyncio.run(telegram_message(message))
            continue
        except json.JSONDecodeError:
            #error with files
            message = storage_error(departure,arrival,querystring.get("outbound_date"))
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



    #cleaning old data in files
    clean_all_files()


if __name__ == "__main__":
    main()









