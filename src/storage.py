# saves to JSON
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent


def convert_to_json(data,querystring):
    flights = data["data"]["itineraries"]["topFlights"]
    flight_arr = []

    for flight in flights:
        segment = flight["flights"]

        first = segment[0] #information about the departure airport
        last = segment[-1] # information about the last flight of the journey


        flight_data ={
            "from": first.get("departure_airport").get("airport_code"),
            "to": last.get("arrival_airport").get("airport_code"),
            "departure_time": first.get("departure_airport").get("time"),
            "arrival_time": last.get("arrival_airport").get("time"),
            "price": flight.get("price"),
            "duration": first.get("duration").get("raw"),
            "stops":len(flight["flights"]) - 1,
            "bags": flight.get("bags"),
            "nmb_of_adults": querystring.get("adults"),

            "segments" : [
            {
                "from": seg.get("departure_airport").get("airport_code"),
                "to": seg.get("arrival_airport").get("airport_code"),
                "airline": seg.get("airline"),
                "duration_min": seg.get("duration").get("raw"),
                "time": seg.get("departure_airport").get("time"),
            }
            for seg in flight["flights"]
        ],
            "layovers": [
                {
                    "airport": layover["airport_code"],
                    "duration_min": layover["duration"]
                }
                for layover in flight.get("layovers") or []
            ],
            "checked_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        flight_arr.append(flight_data)
    return flight_arr

def load_from_specified_json(departue, arrival):
    file_name = f"{departue}-{arrival}.json"
    file_path = BASE_DIR / "data" / file_name

    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_to_specific_file(flight_data, departure, arrival):
    file_name = f"{departure}-{arrival}.json"

    file_path = BASE_DIR/"data"/ file_name

    # create folder if it doesn't exist ->data folder on cloud
    file_path.parent.mkdir(parents=True, exist_ok=True)


    existing_data = load_from_specified_json(departure, arrival)
    existing_data.extend(flight_data)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)

def clean_all_files():
    data_folder = BASE_DIR / "data"
    today = datetime.today().date()

    for file in data_folder.iterdir():
        departure,arrival = file.stem.split("-")
        data = load_from_specified_json(departure, arrival)
        valid_flights = []

        for flight in data:
            flight_date = datetime.strptime(flight["departure_time"], "%Y-%m-%d %H:%M").date()
            if flight_date >= today:
                valid_flights.append(flight)


        with (data_folder / file.name).open("w", encoding="utf-8") as f:
            json.dump(valid_flights, f, ensure_ascii=False, indent=4)



