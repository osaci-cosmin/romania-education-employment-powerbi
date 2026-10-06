import requests  # Imports the library used to download files from the web
from pathlib import Path  # Imports tools for working safely with file and folder paths


# --------------------------------------------------
# 1. Define official enrollment resources
# --------------------------------------------------

enrollment_resources = {
    "2015-2016": "https://data.gov.ro/dataset/ae31768d-1a07-4787-96a5-42e5d2a2b891/resource/8f63c20a-50a6-4800-a2e3-2192f4bbb651/download/2015_2016.xlsx",
    "2016-2017": "https://data.gov.ro/dataset/cd6dbbe0-bcd3-4ebd-a7e1-aedab1ebee3a/resource/913d4ee2-b5f8-4d88-ad8b-520a52aa7334/download/2016_2017.xlsx",
    "2017-2018": "https://data.gov.ro/dataset/218b69d6-102b-4f96-9777-e2af7140e3c8/resource/30b706d9-8abf-4412-ba0c-fb866ad33cbf/download/2017_2018.xlsx",
    "2018-2019": "https://data.gov.ro/dataset/a60c5b1f-a500-4e04-a2bf-d990dcd3b49c/resource/414d8e9c-0309-4fd5-a594-e7381c5ce19f/download/2018_2019.xlsx",
    "2019-2020": "https://data.gov.ro/dataset/929eb57b-23ab-44b7-bda5-5982cd935e44/resource/3725387f-6be8-496a-9d9c-696d910db6c2/download/2019_2020.xlsx",
    "2020-2021": "https://data.gov.ro/dataset/305274da-7396-4fe6-a95c-9228a54532ff/resource/45c20ed0-1013-4596-ad85-5f843909eb0b/download/elevi-2020-2021.xlsx",
    "2021-2022": "https://data.gov.ro/dataset/f212e8e8-0cc5-462f-81f9-efa8871e4810/resource/721bf5ea-8710-44aa-8826-ddc12e00a2b7/download/2021_2022.xlsx",
    "2022-2023": "https://data.gov.ro/dataset/0f2e8cd2-1ddd-4a06-b347-cf664a579371/resource/b5c9a794-dc12-496a-9889-ae1cf88a036b/download/2022_2023_elevi.xlsx",
    "2023-2024": "https://data.gov.ro/dataset/140c6c3a-6e10-412e-a9b2-3cda478a2725/resource/2442487a-e52b-43b7-90f0-0d0e4d9fdbdb/download/2023_2024_elevi.xlsx"
}


# --------------------------------------------------
# 2. Create the raw enrollment directory
# --------------------------------------------------

raw_dir = Path("data/raw/enrollment")  # Defines the folder used for raw enrollment files

raw_dir.mkdir(
    parents=True,
    exist_ok=True
)  # Creates the directory if it does not already exist


# --------------------------------------------------
# 3. Download every school year
# --------------------------------------------------

for school_year, url in enrollment_resources.items():

    output_file = raw_dir / f"enrollment_{school_year.replace('-', '_')}_raw.xlsx"
    # Creates a consistent local filename for each school year

    print(f"\nDownloading {school_year}...")

    response = requests.get(
        url,
        timeout=120
    )  # Downloads the original Excel resource

    response.raise_for_status()
    # Stops execution if the server returns an HTTP error

    with open(output_file, "wb") as file:
        file.write(response.content)
    # Saves the original binary file without modifying its contents

    print("Saved:", output_file)
    print("File size:", len(response.content), "bytes")


print("\nAll enrollment raw files downloaded successfully.")

