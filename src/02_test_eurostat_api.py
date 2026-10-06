import requests  # Imports the requests library used to communicate with web APIs

url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10r_3empers"  # Stores the Eurostat employment dataset endpoint

params = {
    "lang": "en",                  # Requests metadata and labels in English
    "freq": "A",                   # Selects annual data
    "unit": "THS",                 # Selects values expressed in thousand persons
    "wstatus": "SAL",              # Selects employees
    "nace_r2": "TOTAL",            # Selects all economic activities combined
    "geoLevel": "nuts3",           # Keeps only NUTS 3 geographical regions
    "sinceTimePeriod": "2014",     # Selects data starting from 2014
    "untilTimePeriod": "2023"      # Selects data up to and including 2023
}

response = requests.get(url, params=params, timeout=30)  # Sends the filtered request to Eurostat

print("Status code:", response.status_code)  # Displays the HTTP response status

data = response.json()  # Converts the JSON response into a Python dictionary

geo_labels = data["dimension"]["geo"]["category"]["label"]  # Extracts geographical codes and names

time_labels = data["dimension"]["time"]["category"]["label"]  # Extracts the years returned by Eurostat

ro_nuts3 = {}  # Creates an empty dictionary for Romanian NUTS 3 regions

for geo_code, geo_name in geo_labels.items():  # Loops through all NUTS 3 regions
    if geo_code.startswith("RO") and len(geo_code) == 5:  # Keeps only Romanian NUTS 3 codes
        ro_nuts3[geo_code] = geo_name  # Stores the Romanian code and county name

print("Romanian NUTS 3 regions:", len(ro_nuts3))  # Validates that Romania has 42 NUTS 3 regions

print("Years:", list(time_labels.values()))  # Displays the years returned by the API

print("Dimensions:", data["id"])  # Displays the order of dimensions in the JSON-stat dataset

print("Dimension sizes:", data["size"])  # Displays the number of categories in each dimension







geo_index = data["dimension"]["geo"]["category"]["index"]  # Gets the position of each geographical code in the dataset

time_index = data["dimension"]["time"]["category"]["index"]  # Gets the position of each year in the dataset

number_of_years = len(time_index)  # Stores the number of years returned by the API

county_code = "RO423"  # Selects Hunedoara using its NUTS 3 code

county_position = geo_index[county_code]  # Gets Hunedoara's numerical position inside the geo dimension

for year, year_position in time_index.items():  # Loops through every year returned by Eurostat
    flat_index = county_position * number_of_years + year_position  # Calculates the position of the observation in the flattened JSON-stat dataset

    value = data["value"].get(str(flat_index))  # Retrieves the statistical value; returns None if the observation is missing

    print(county_code, year, value)  # Displays county code, year and employee value