from pathlib import Path
import zipfile

import requests


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

URL = (
    "https://data.gov.ro/dataset/"
    "cb54fa0b-4d8c-4cef-b0d9-fe80e0c99743/"
    "resource/fd31ca32-cbfb-4fb2-ba9f-49e80a966e65/"
    "download/2017-09-25-date-deschise-2017-i.ods"
)

OUTPUT_PATH = Path(
    "data/raw/baccalaureate/"
    "baccalaureate_2017_session1_raw.ods"
)


# ---------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------

print("=" * 100)
print("2017 BACCALAUREATE ODS DOWNLOAD")
print("=" * 100)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

print("\nSource:")
print(URL)

print("\nDestination:")
print(OUTPUT_PATH)


if OUTPUT_PATH.exists():
    print("\nFile already exists.")
    print("Existing size:")
    print(OUTPUT_PATH.stat().st_size)

else:
    print("\nDownloading...")

    with requests.get(
        URL,
        stream=True,
        timeout=(30, 300)
    ) as response:

        response.raise_for_status()

        with open(
            OUTPUT_PATH,
            "wb"
        ) as f:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):
                if chunk:
                    f.write(chunk)

    print("\nDownload completed.")

    print("\nDownloaded size:")
    print(OUTPUT_PATH.stat().st_size)


# ---------------------------------------------------------------------
# Basic ODS validation
# ---------------------------------------------------------------------

print("\nChecking ODS archive...")

if not zipfile.is_zipfile(OUTPUT_PATH):
    raise ValueError(
        "Downloaded file is not a valid ODS/ZIP archive."
    )

with zipfile.ZipFile(
    OUTPUT_PATH,
    "r"
) as archive:

    members = archive.namelist()

    print("\nArchive contains content.xml:")
    print("content.xml" in members)

    if "content.xml" not in members:
        raise ValueError(
            "ODS archive does not contain content.xml."
        )


print("\n2017 ODS ingestion completed successfully.")