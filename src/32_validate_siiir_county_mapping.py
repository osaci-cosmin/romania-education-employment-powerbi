import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Define the 2022 source file
# --------------------------------------------------

file_2022 = Path(
    "data/raw/baccalaureate/"
    "baccalaureate_2022_session1_raw.xlsx"
)


# --------------------------------------------------
# 2. Read only the columns needed for geography
# --------------------------------------------------

df = pd.read_excel(
    file_2022,
    sheet_name="Export Worksheet",
    usecols=[
        "Judet",
        "Cod SIIIR",
        "Cod",
        "STATUS_FINAL",
        "MEDIA_FINALA",
    ]
)


# --------------------------------------------------
# 3. Normalize text columns
# --------------------------------------------------

df["Judet"] = (
    df["Judet"]
    .astype("string")
    .str.strip()
)

df["Cod SIIIR"] = (
    df["Cod SIIIR"]
    .astype("string")
    .str.strip()
)


# --------------------------------------------------
# 4. Extract the first two digits of the SIIIR code
# --------------------------------------------------

df["siiir_county_prefix"] = (
    df["Cod SIIIR"]
    .str[:2]
)


# --------------------------------------------------
# 5. Basic candidate validation
# --------------------------------------------------

print("Rows:")
print(len(df))

print("\nNon-null candidate codes:")
print(
    df["Cod"]
    .notna()
    .sum()
)

print("\nUnique candidate codes:")
print(
    df["Cod"]
    .nunique(dropna=True)
)

print("\nUnique counties:")
print(
    df["Judet"]
    .nunique(dropna=True)
)

print("\nCounty values:")
print(
    sorted(
        df["Judet"]
        .dropna()
        .unique()
    )
)


# --------------------------------------------------
# 6. Build prefix-to-county combinations
# --------------------------------------------------

mapping = (
    df[
        [
            "siiir_county_prefix",
            "Judet"
        ]
    ]
    .dropna()
    .drop_duplicates()
    .sort_values(
        [
            "siiir_county_prefix",
            "Judet"
        ]
    )
)


print("\nPrefix-to-county combinations:")
print(
    mapping.to_string(
        index=False
    )
)


# --------------------------------------------------
# 7. Check whether one prefix maps to multiple counties
# --------------------------------------------------

prefix_conflicts = (
    mapping
    .groupby(
        "siiir_county_prefix"
    )["Judet"]
    .nunique()
)


prefix_conflicts = (
    prefix_conflicts[
        prefix_conflicts > 1
    ]
)


print(
    "\nPrefixes mapped to multiple counties:"
)

print(
    prefix_conflicts
)


# --------------------------------------------------
# 8. Check whether one county has multiple prefixes
# --------------------------------------------------

county_prefix_counts = (
    mapping
    .groupby(
        "Judet"
    )["siiir_county_prefix"]
    .nunique()
)


multiple_prefix_counties = (
    county_prefix_counts[
        county_prefix_counts > 1
    ]
)


print(
    "\nCounties with multiple prefixes:"
)

print(
    multiple_prefix_counties
)


# --------------------------------------------------
# 9. Inspect final-result fields
# --------------------------------------------------

print(
    "\nSTATUS_FINAL distribution:"
)

print(
    df["STATUS_FINAL"]
    .value_counts(
        dropna=False
    )
)


print(
    "\nMEDIA_FINALA summary:"
)

print(
    pd.to_numeric(
        df["MEDIA_FINALA"],
        errors="coerce"
    )
    .describe()
)


print(
    "\n2022 geography and candidate validation completed."
)