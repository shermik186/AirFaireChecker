from graphlib import TopologicalSorter
from xml.etree.ElementTree import indent
import json
import asyncio
from src.fetcher import get_data
from src.storage import  convert_to_json, save_to_specific_file,load_from_specified_json,clean_all_files
from src.analyzer import under_price_api, cheapest_flight_api,direct_flights_api,latest_price_drop_of_cheapest_flight
from config import QUERYSTRINGS
from src.notifier import telegram_message,cheapest_flight_message,price_drop_message



def main():
    for querystring in QUERYSTRINGS:

        api_data = get_data(querystring)

        if api_data is None:
            #todo : api failed message
            continue


        api_data = convert_to_json(api_data,querystring)

        if not api_data:
            #todo : no good flight from api message
            continue
        departure, arrival = querystring.get("departure_id"), querystring.get("arrival_id")
        save_to_specific_file(api_data,departure,arrival)

        #getting the cheapest flight
        cheapest = cheapest_flight_api(api_data)
        cheapest_message = cheapest_flight_message(cheapest)
        asyncio.run(telegram_message(cheapest_message))



        #getting the data necessary for price drop function
        try:
            load_data = load_from_specified_json(departure,arrival)

        except FileNotFoundError:
            print(f"File not found: {departure}-{arrival}")
            continue
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {departure}-{arrival}")
            continue

        price_drop_data = latest_price_drop_of_cheapest_flight(load_data,departure, arrival, querystring.get("outbound_date"),querystring)

        if price_drop_data is None:
            #todo: add message about not enough data for price drop change
            continue

        price_drop_msg = price_drop_message(price_drop_data)
        asyncio.run(telegram_message(price_drop_msg))

         #TODO : later add a under price option

    #cleaning old data in files
    clean_all_files()


if __name__ == "__main__":
    main()









