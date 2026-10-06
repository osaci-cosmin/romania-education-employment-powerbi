import json  # Imports tools for reading and working with JSON files
import pandas as pd  # Imports pandas for tabular data processing and validation
from pathlib import Path  # Imports tools for working safely with file and folder paths

raw_file = "data/raw/eurostat_employment_2014_2023_raw.json"  # Stores the path to the raw Eurostat file

with open(raw_file, "r", encoding="utf-8") as file:
    data = json.load(file)  # Loads the raw JSON file into a Python dictionary

geo_labels = data["dimension"]["geo"]["category"]["label"]  # Gets geographical codes and names
geo_index = data["dimension"]["geo"]["category"]["index"]  # Gets the numerical position of each geographical code

time_labels = data["dimension"]["time"]["category"]["label"]  # Gets the available years
time_index = data["dimension"]["time"]["category"]["index"]  # Gets the numerical position of each year

number_of_years = len(time_index)  # Stores the number of years in the dataset

records = []  # Creates an empty list that will store the final county-year observations

for geo_code, geo_name in geo_labels.items():  # Loops through all geographical areas
    if geo_code.startswith("RO") and len(geo_code) == 5:  # Keeps only Romanian NUTS 3 regions

        county_position = geo_index[geo_code]  # Gets the numerical position of the county

        for year, year_position in time_index.items():  # Loops through every year

            flat_index = county_position * number_of_years + year_position  # Calculates the flattened JSON-stat position

            value = data["value"].get(str(flat_index))  # Retrieves the employment value or None if it is missing

            record = {
                "county_code": geo_code,          # Stores the NUTS 3 county code
                "county": geo_name,               # Stores the county name
                "year": int(year),                # Converts the year from text to integer
                "employees_thousands": value      # Stores employees in thousand persons
            }

            records.append(record)  # Adds the observation to the records list

print("Number of observations:", len(records))  # Checks the expected number of county-year observations

print(records[:5])  # Displays the first five observations for inspection



df = pd.DataFrame(records)  # Converts the list of dictionaries into a pandas DataFrame

print("\nDataFrame shape:")
print(df.shape)  # Displays the number of rows and columns

print("\nData types:")
print(df.dtypes)  # Displays the data type of each column

print("\nMissing values:")
print(df.isna().sum())  # Counts missing values in each column

print("\nDuplicate county-year combinations:")
print(df.duplicated(subset=["county_code", "year"]).sum())  # Checks whether the same county-year combination appears more than once

print("\nUnique counties:")
print(df["county_code"].nunique())  # Counts unique Romanian NUTS 3 county codes

print("\nUnique years:")
print(df["year"].nunique())  # Counts unique years in the dataset

print("\nYear range:")
print(df["year"].min(), "-", df["year"].max())  # Displays the minimum and maximum year

print("\nFirst rows:")
print(df.head())  # Displays the first five rows of the DataFrame



# Automated data quality checks

assert len(df) == 420, "Expected 420 county-year observations"  # Verifies the expected number of observations

assert df["county_code"].nunique() == 42, "Expected 42 Romanian NUTS 3 regions"  # Verifies the number of counties

assert df["year"].nunique() == 10, "Expected 10 years"  # Verifies the number of years

assert df["year"].min() == 2014, "Unexpected minimum year"  # Verifies the beginning of the analysis period

assert df["year"].max() == 2023, "Unexpected maximum year"  # Verifies the end of the analysis period

assert df.duplicated(subset=["county_code", "year"]).sum() == 0, "Duplicate county-year combinations detected"  # Verifies the dataset grain

assert df["employees_thousands"].isna().sum() == 0, "Missing employment values detected"  # Verifies that employment values are complete

print("\nAll data quality checks passed successfully.")




df["employees"] = (df["employees_thousands"] * 1000).round().astype("int64")  # Converts thousand persons into persons

processed_dir = Path("data/processed")  # Defines the folder where processed datasets will be stored

processed_dir.mkdir(parents=True, exist_ok=True)  # Creates the folder if it does not already exist

processed_file = processed_dir / "employment_clean.csv"  # Builds the output file path

df.to_csv(
    processed_file,
    index=False,
    encoding="utf-8-sig"
)  # Exports the validated DataFrame to CSV without adding the pandas index

print("\nProcessed employment dataset saved successfully.")
print("Output file:", processed_file)