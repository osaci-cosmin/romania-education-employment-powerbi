import requests  # Imports the library used to communicate with the data.gov.ro API


# --------------------------------------------------
# 1. Define the CKAN search endpoint
# --------------------------------------------------

url = "https://data.gov.ro/api/3/action/package_search"
# Stores the official data.gov.ro CKAN dataset search endpoint


# --------------------------------------------------
# 2. Search for Baccalaureate result datasets
# --------------------------------------------------

params = {
    "q": "Rezultate Bacalaureat",
    "rows": 100
}
# Searches broadly for datasets related to Baccalaureate results


response = requests.get(
    url,
    params=params,
    timeout=30
)
# Sends the API request


response.raise_for_status()
# Stops execution if the API returns an HTTP error


data = response.json()
# Converts the JSON response into a Python dictionary


datasets = data["result"]["results"]
# Extracts the returned datasets


# --------------------------------------------------
# 3. Keep only Ministry of Education datasets
# --------------------------------------------------

ministry_datasets = []

for dataset in datasets:

    organization = dataset.get("organization")

    if not organization:
        continue

    organization_title = organization.get(
        "title",
        ""
    )

    if "Ministerul Educației" in organization_title:
        ministry_datasets.append(dataset)


# --------------------------------------------------
# 4. Display datasets and downloadable resources
# --------------------------------------------------

print("Total datasets returned:")
print(len(datasets))

print("\nMinistry of Education datasets:")
print(len(ministry_datasets))


for dataset in ministry_datasets:

    print("\n" + "=" * 100)

    print("Dataset title:", dataset["title"])

    print("Dataset name:", dataset["name"])

    print(
        "Organization:",
        dataset["organization"]["title"]
    )

    print(
        "Resources:",
        len(dataset["resources"])
    )

    for resource in dataset["resources"]:

        print(
            "  Resource name:",
            resource.get("name")
        )

        print(
            "  Format:",
            resource.get("format")
        )

        print(
            "  URL:",
            resource.get("url")
        )