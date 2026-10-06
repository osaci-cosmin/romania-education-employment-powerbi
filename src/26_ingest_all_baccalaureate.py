import requests  # Imports the library used to download official source files
from pathlib import Path  # Imports tools for working safely with file paths


# --------------------------------------------------
# 1. Define official Session I resources
# --------------------------------------------------

resources = {
    2015: {
        "url": "https://data.gov.ro/dataset/3d6d423b-f54f-43c3-ab4c-54f704a36ee5/resource/e2f3ecdd-e615-45ce-808f-9977dab7a453/download/bacinscriere2015sesiuneai00.csv",
        "extension": "csv"
    },

    2016: {
        "url": "https://data.gov.ro/dataset/a7f55a35-c114-4309-a048-88c4924024eb/resource/2e34e2ad-d082-4ef3-aeea-bc6437c72096/download/2016sesiuneai.csv",
        "extension": "csv"
    },

    2017: {
        "url": "https://data.gov.ro/dataset/cb54fa0b-4d8c-4cef-b0d9-fe80e0c99743/resource/2b8d2567-2633-422a-a98b-4fb6cd9c0b09/download/2017-09-25-date-deschise-2017-i.csv",
        "extension": "csv"
    },

    2018: {
        "url": "https://data.gov.ro/dataset/1007a44d-0b53-477a-bc49-8c59e00db39e/resource/bda23092-c00e-4feb-92bf-9df53e19f366/download/date-deschise-bac-2018-sesiunea-1.xlsx",
        "extension": "xlsx"
    },

    2019: {
        "url": "https://data.gov.ro/dataset/83ab8216-a862-407c-ad74-7dba39d22061/resource/450e7341-ec1e-43f8-b9f8-75145afc894c/download/2019-08-06-date-deschise-bac-2019-i.xlsx",
        "extension": "xlsx"
    },

    2020: {
        "url": "https://data.gov.ro/dataset/e996dc5c-48d1-4cbc-9aaf-2f4c3a2362a5/resource/b0de486e-fa2f-4380-9c6c-71e36d6e35c1/download/date-deschise-bac-2020-sesiunea-1.xlsx",
        "extension": "xlsx"
    },

    2021: {
        "url": "https://data.gov.ro/dataset/6827d28b-76de-41e1-a75a-a9251b04714a/resource/2db91f1c-77a6-44bd-a5d7-e1c384c49275/download/2021.08.10_bac_date-deschise_2021.xlsx",
        "extension": "xlsx"
    },

    2022: {
        "url": "https://data.gov.ro/dataset/0778231d-be65-41c8-9530-6f8dbceaaa08/resource/9e0419b2-342c-4849-ad69-78f6dab8efc4/download/2022.07.06_bac_export-sesiunea-1-2022.xlsx",
        "extension": "xlsx"
    },

    2023: {
        "url": "https://data.gov.ro/dataset/90cd5404-01b7-4002-ac63-6e44917afbf9/resource/9635d473-edcb-4df6-af26-968f8030df54/download/2023.07.19_bac_date-deschise_2023-ses1.xlsx",
        "extension": "xlsx"
    }
}


# --------------------------------------------------
# 2. Create the raw directory
# --------------------------------------------------

raw_dir = Path("data/raw/baccalaureate")

raw_dir.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# 3. Download all official source files
# --------------------------------------------------

for year, resource in resources.items():

    url = resource["url"]
    extension = resource["extension"]

    output_file = (
        raw_dir
        / f"baccalaureate_{year}_session1_raw.{extension}"
    )

    print("\n" + "=" * 80)
    print(f"Downloading Baccalaureate {year} Session I...")

    response = requests.get(
        url,
        timeout=180
    )

    response.raise_for_status()

    with open(output_file, "wb") as file:
        file.write(response.content)

    print("Saved:", output_file)
    print("File size:", len(response.content), "bytes")


print("\nAll Baccalaureate Session I raw files downloaded successfully.")