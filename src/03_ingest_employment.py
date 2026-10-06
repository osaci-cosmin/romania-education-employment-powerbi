import json  # Imports tools for working with JSON files
import requests  # Imports the library used to communicate with the Eurostat API

url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10r_3empers"  # Stores the Eurostat employment dataset endpoint

params = {
    "lang": "en",                  # Requests metadata and labels in English
    "freq": "A",                   # Selects annual data
    "unit": "THS",                 # Selects values expressed in thousand persons
    "wstatus": "SAL",              # Selects employees
    "nace_r2": "TOTAL",            # Selects all economic activities combined
    "geoLevel": "nuts3",           # Selects NUTS 3 geographical regions
    "sinceTimePeriod": "2014",     # Selects data starting from 2014
    "untilTimePeriod": "2023"      # Selects data up to and including 2023
}

response = requests.get(url, params=params, timeout=30)  # Sends the request to the Eurostat API

response.raise_for_status()  # Stops the script if the server returns an HTTP error

data = response.json()  # Converts the JSON response into a Python dictionary

with open("data/raw/eurostat_employment_2014_2023_raw.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)  # Saves the original API response as a formatted JSON file

print("Raw employment data saved successfully.")