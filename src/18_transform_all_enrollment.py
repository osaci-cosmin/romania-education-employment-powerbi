import pandas as pd  # Imports pandas for data transformation and validation
from pathlib import Path  # Imports tools for working safely with file paths


# --------------------------------------------------
# 1. Define source configurations
# --------------------------------------------------

year_configs = {
    "2015-2016": {
        "filename": "enrollment_2015_2016_raw.xlsx",
        "header": 0,
        "value_column": "Numarul elevilor existenti"
    },
    "2016-2017": {
        "filename": "enrollment_2016_2017_raw.xlsx",
        "header": 0,
        "value_column": "Numarul elevilor existenti"
    },
    "2017-2018": {
        "filename": "enrollment_2017_2018_raw.xlsx",
        "header": 0,
        "value_column": "Numarul elevilor existenti"
    },
    "2018-2019": {
        "filename": "enrollment_2018_2019_raw.xlsx",
        "header": 0,
        "value_column": "Numarul elevilor existenti"
    },
    "2019-2020": {
        "filename": "enrollment_2019_2020_raw.xlsx",
        "header": 0,
        "value_column": "Numarul elevilor existenti"
    },
    "2020-2021": {
        "filename": "enrollment_2020_2021_raw.xlsx",
        "header": 0,
        "value_column": "Elevi exist anterior-asoc"
    },
    "2021-2022": {
        "filename": "enrollment_2021_2022_raw.xlsx",
        "header": 4,
        "value_column": "Elevi exist anterior-asoc"
    },
    "2022-2023": {
        "filename": "enrollment_2022_2023_raw.xlsx",
        "header": 4,
        "value_column": "Elevi exist anterior-asoc"
    },
    "2023-2024": {
        "filename": "enrollment_2023_2024_raw.xlsx",
        "header": 4,
        "value_column": "Elevi exist anterior-asoc"
    }
}


# --------------------------------------------------
# 2. Define formal education levels
# --------------------------------------------------

formal_education_levels = [
    "Antepreşcolar",
    "Preșcolar",
    "Primar",
    "Gimnazial",
    "Profesional",
    "Liceal",
    "Postliceal"
]  # Keeps only formal pre-university education levels


# --------------------------------------------------
# 3. Define county abbreviation to NUTS 3 mapping
# --------------------------------------------------

county_to_nuts3 = {
    "AB": "RO121",
    "AG": "RO311",
    "AR": "RO421",
    "B": "RO321",
    "BC": "RO211",
    "BH": "RO111",
    "BN": "RO112",
    "BR": "RO221",
    "BT": "RO212",
    "BV": "RO122",
    "BZ": "RO222",
    "CJ": "RO113",
    "CL": "RO312",
    "CS": "RO422",
    "CT": "RO223",
    "CV": "RO123",
    "DB": "RO313",
    "DJ": "RO411",
    "GJ": "RO412",
    "GL": "RO224",
    "GR": "RO314",
    "HD": "RO423",
    "HR": "RO124",
    "IF": "RO322",
    "IL": "RO315",
    "IS": "RO213",
    "MH": "RO413",
    "MM": "RO114",
    "MS": "RO125",
    "NT": "RO214",
    "OT": "RO414",
    "PH": "RO316",
    "SB": "RO126",
    "SJ": "RO116",
    "SM": "RO115",
    "SV": "RO215",
    "TL": "RO225",
    "TM": "RO424",
    "TR": "RO317",
    "VL": "RO415",
    "VN": "RO226",
    "VS": "RO216"
}


# --------------------------------------------------
# 4. Define input and output directories
# --------------------------------------------------

raw_dir = Path("data/raw/enrollment")

processed_dir = Path("data/processed")

processed_dir.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# 5. Transform every school year
# --------------------------------------------------

all_years = []

for school_year, config in year_configs.items():

    print("\n" + "=" * 80)
    print("Processing:", school_year)

    file_path = raw_dir / config["filename"]

    df = pd.read_excel(
        file_path,
        header=config["header"]
    )

    value_column = config["value_column"]


    # --------------------------------------------------
    # Keep only formal education observations
    # --------------------------------------------------

    df = df[
        df["Nivel"].isin(formal_education_levels)
    ].copy()

    # Aggregate/footer rows and non-formal activity categories
    # are excluded because they do not belong to the analytical grain.


    # --------------------------------------------------
    # Convert enrollment values to numeric
    # --------------------------------------------------

    df["enrolled_students"] = pd.to_numeric(
        df[value_column],
        errors="coerce"
    )


    # --------------------------------------------------
    # Validate source observations
    # --------------------------------------------------

    assert df["Judet"].isna().sum() == 0, \
        f"Missing county values detected in {school_year}"

    assert df["Nivel"].isna().sum() == 0, \
        f"Missing education levels detected in {school_year}"

    assert df["enrolled_students"].isna().sum() == 0, \
        f"Missing enrollment values detected in {school_year}"

    assert (df["enrolled_students"] < 0).sum() == 0, \
        f"Negative enrollment values detected in {school_year}"

    assert (
        df["enrolled_students"] % 1 != 0
    ).sum() == 0, \
        f"Non-integer enrollment values detected in {school_year}"


    # --------------------------------------------------
    # Add temporal fields
    # --------------------------------------------------

    df["school_year"] = school_year

    df["analysis_year"] = int(
        school_year.split("-")[0]
    )
    # Uses the starting calendar year of the school year.
    # The original school_year field is preserved for semantic accuracy.


    # --------------------------------------------------
    # Standardize geography
    # --------------------------------------------------

    df["county_code"] = df[
        "Judet"
    ].map(county_to_nuts3)

    assert df["county_code"].isna().sum() == 0, \
        f"Missing NUTS 3 mappings detected in {school_year}"


    # --------------------------------------------------
    # Aggregate to analytical grain
    # --------------------------------------------------

    yearly_clean = (
        df.groupby(
            [
                "county_code",
                "Judet",
                "school_year",
                "analysis_year",
                "Nivel"
            ],
            as_index=False
        )["enrolled_students"]
        .sum()
    )

    yearly_clean = yearly_clean.rename(
        columns={
            "Judet": "county_abbr",
            "Nivel": "education_level"
        }
    )


    # --------------------------------------------------
    # Validate yearly analytical table
    # --------------------------------------------------

    assert yearly_clean["county_code"].nunique() == 42, \
        f"Expected 42 counties in {school_year}"

    assert yearly_clean.duplicated(
        subset=[
            "county_code",
            "school_year",
            "education_level"
        ]
    ).sum() == 0, \
        f"Duplicate analytical keys detected in {school_year}"

    print("Counties:", yearly_clean["county_code"].nunique())
    print("Education levels:", yearly_clean["education_level"].nunique())
    print("Analytical rows:", len(yearly_clean))
    print("Enrollment total:", yearly_clean["enrolled_students"].sum())

    all_years.append(yearly_clean)


# --------------------------------------------------
# 6. Combine all school years
# --------------------------------------------------

enrollment_clean = pd.concat(
    all_years,
    ignore_index=True
)


# --------------------------------------------------
# 7. Convert final enrollment values to integers
# --------------------------------------------------

enrollment_clean["enrolled_students"] = (
    enrollment_clean["enrolled_students"]
    .astype("int64")
)


# --------------------------------------------------
# 8. Final dataset validation
# --------------------------------------------------

print("\n" + "=" * 80)
print("FINAL ENROLLMENT DATASET")

print("\nShape:")
print(enrollment_clean.shape)

print("\nSchool years:")
print(enrollment_clean["school_year"].unique())

print("\nUnique school years:")
print(enrollment_clean["school_year"].nunique())

print("\nAnalysis year range:")
print(
    enrollment_clean["analysis_year"].min(),
    "-",
    enrollment_clean["analysis_year"].max()
)

print("\nUnique counties:")
print(enrollment_clean["county_code"].nunique())

print("\nUnique education levels:")
print(enrollment_clean["education_level"].nunique())

print("\nMissing values:")
print(enrollment_clean.isna().sum())

print("\nDuplicate analytical keys:")
print(
    enrollment_clean.duplicated(
        subset=[
            "county_code",
            "school_year",
            "education_level"
        ]
    ).sum()
)

print("\nEnrollment totals by school year:")
print(
    enrollment_clean.groupby(
        "school_year"
    )["enrolled_students"].sum()
)


# --------------------------------------------------
# 9. Automated final checks
# --------------------------------------------------

assert enrollment_clean["school_year"].nunique() == 9, \
    "Expected 9 school years"

assert enrollment_clean["analysis_year"].min() == 2015, \
    "Unexpected minimum analysis year"

assert enrollment_clean["analysis_year"].max() == 2023, \
    "Unexpected maximum analysis year"

assert enrollment_clean["county_code"].nunique() == 42, \
    "Expected 42 Romanian NUTS 3 regions"

assert enrollment_clean["education_level"].nunique() == 7, \
    "Expected 7 formal education levels"

assert enrollment_clean.isna().sum().sum() == 0, \
    "Missing values detected in final enrollment dataset"

assert enrollment_clean.duplicated(
    subset=[
        "county_code",
        "school_year",
        "education_level"
    ]
).sum() == 0, \
    "Duplicate analytical keys detected in final enrollment dataset"

print("\nAll final enrollment data quality checks passed successfully.")


# --------------------------------------------------
# 10. Reorder final columns
# --------------------------------------------------

enrollment_clean = enrollment_clean[
    [
        "county_code",
        "county_abbr",
        "school_year",
        "analysis_year",
        "education_level",
        "enrolled_students"
    ]
]


# --------------------------------------------------
# 11. Export final processed dataset
# --------------------------------------------------

processed_file = processed_dir / "enrollment_clean.csv"

enrollment_clean.to_csv(
    processed_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nFinal enrollment dataset saved successfully.")
print("Output file:", processed_file)


