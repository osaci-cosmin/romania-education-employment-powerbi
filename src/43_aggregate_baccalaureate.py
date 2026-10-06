from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

INTERIM_PATH = Path(
    "data/interim/baccalaureate_candidate_standardized.csv"
)

ENROLLMENT_PATH = Path(
    "data/processed/enrollment_clean.csv"
)

EMPLOYMENT_PATH = Path(
    "data/processed/employment_clean.csv"
)

OUTPUT_PATH = Path(
    "data/processed/baccalaureate_clean.csv"
)


EXPECTED_YEARS = set(
    range(2015, 2024)
)

EXPECTED_COUNTIES = 42
EXPECTED_ROWS = 42 * 9


EXPECTED_NATIONAL_CANDIDATES = {
    2015: 168_939,
    2016: 137_338,
    2017: 135_513,
    2018: 136_864,
    2019: 136_091,
    2020: 155_650,
    2021: 133_664,
    2022: 126_453,
    2023: 130_522,
}


# ---------------------------------------------------------------------
# Load standardized candidate-level data
# ---------------------------------------------------------------------

print("=" * 100)
print("BACCALAUREATE COUNTY-YEAR AGGREGATION")
print("=" * 100)


df = pd.read_csv(
    INTERIM_PATH,
    usecols=[
        "year",
        "county_abbr",
        "final_grade",
        "is_present",
        "is_passed",
        "is_failed",
        "is_absent",
        "is_eliminated",
        "has_valid_grade",
    ],
)


print("\nCandidate-level rows loaded:")
print(len(df))


# ---------------------------------------------------------------------
# Create grade contribution
# ---------------------------------------------------------------------

# Missing final grades remain missing for the average,
# but contribute 0 to the grade sum.
df["final_grade_sum_component"] = (
    df["final_grade"]
    .fillna(0)
)


# ---------------------------------------------------------------------
# Aggregate to County × Year
# ---------------------------------------------------------------------

aggregated = (
    df
    .groupby(
        [
            "year",
            "county_abbr",
        ],
        as_index=False,
        observed=True,
    )
    .agg(
        candidates=(
            "county_abbr",
            "size",
        ),
        present_candidates=(
            "is_present",
            "sum",
        ),
        passed_candidates=(
            "is_passed",
            "sum",
        ),
        failed_candidates=(
            "is_failed",
            "sum",
        ),
        absent_candidates=(
            "is_absent",
            "sum",
        ),
        eliminated_candidates=(
            "is_eliminated",
            "sum",
        ),
        graded_candidates=(
            "has_valid_grade",
            "sum",
        ),
        final_grade_sum=(
            "final_grade_sum_component",
            "sum",
        ),
    )
)


# ---------------------------------------------------------------------
# Calculate row-level analytical indicators
# ---------------------------------------------------------------------

aggregated["pass_rate"] = (
    aggregated["passed_candidates"]
    / aggregated["present_candidates"]
)


aggregated["average_grade"] = (
    aggregated["final_grade_sum"]
    / aggregated["graded_candidates"]
)


# Keep useful numerical precision.
aggregated["final_grade_sum"] = (
    aggregated["final_grade_sum"]
    .round(2)
)

aggregated["pass_rate"] = (
    aggregated["pass_rate"]
    .round(6)
)

aggregated["average_grade"] = (
    aggregated["average_grade"]
    .round(4)
)


# ---------------------------------------------------------------------
# Build county_abbr -> county_code mapping from Enrollment
# ---------------------------------------------------------------------

enrollment_mapping = pd.read_csv(
    ENROLLMENT_PATH,
    usecols=[
        "county_code",
        "county_abbr",
    ],
    dtype=str,
)


enrollment_mapping = (
    enrollment_mapping
    .drop_duplicates()
    .sort_values(
        "county_abbr"
    )
)


print("\nEnrollment county mapping rows:")
print(len(enrollment_mapping))


if len(enrollment_mapping) != EXPECTED_COUNTIES:
    raise ValueError(
        "Enrollment mapping does not contain exactly 42 counties."
    )


if (
    enrollment_mapping["county_abbr"]
    .nunique()
    != EXPECTED_COUNTIES
):
    raise ValueError(
        "Enrollment county abbreviations are not unique."
    )


if (
    enrollment_mapping["county_code"]
    .nunique()
    != EXPECTED_COUNTIES
):
    raise ValueError(
        "Enrollment county codes are not unique."
    )


# ---------------------------------------------------------------------
# Build county_code -> county name mapping from Employment
# ---------------------------------------------------------------------

employment_mapping = pd.read_csv(
    EMPLOYMENT_PATH,
    usecols=[
        "county_code",
        "county",
    ],
    dtype=str,
)


employment_mapping = (
    employment_mapping
    .drop_duplicates()
    .sort_values(
        "county_code"
    )
)


print("\nEmployment county mapping rows:")
print(len(employment_mapping))


if len(employment_mapping) != EXPECTED_COUNTIES:
    raise ValueError(
        "Employment mapping does not contain exactly 42 counties."
    )


if (
    employment_mapping["county_code"]
    .nunique()
    != EXPECTED_COUNTIES
):
    raise ValueError(
        "Employment county codes are not unique."
    )


# ---------------------------------------------------------------------
# Combine geography mappings
# ---------------------------------------------------------------------

county_mapping = (
    enrollment_mapping
    .merge(
        employment_mapping,
        on="county_code",
        how="left",
        validate="one_to_one",
    )
)


if county_mapping["county"].isna().any():
    raise ValueError(
        "Some county names could not be mapped."
    )


print("\nCombined county mapping:")
print(
    county_mapping
    .sort_values("county_code")
    .to_string(index=False)
)


# ---------------------------------------------------------------------
# Add geography to Baccalaureate aggregation
# ---------------------------------------------------------------------

final = (
    aggregated
    .merge(
        county_mapping,
        on="county_abbr",
        how="left",
        validate="many_to_one",
    )
)


if final["county_code"].isna().any():
    raise ValueError(
        "Some Baccalaureate county abbreviations "
        "could not be mapped to NUTS3."
    )


if final["county"].isna().any():
    raise ValueError(
        "Some county names are missing."
    )


# ---------------------------------------------------------------------
# Reorder columns
# ---------------------------------------------------------------------

final = final[
    [
        "county_code",
        "county",
        "county_abbr",
        "year",
        "candidates",
        "present_candidates",
        "passed_candidates",
        "failed_candidates",
        "absent_candidates",
        "eliminated_candidates",
        "graded_candidates",
        "final_grade_sum",
        "pass_rate",
        "average_grade",
    ]
]


final = (
    final
    .sort_values(
        [
            "year",
            "county_code",
        ]
    )
    .reset_index(
        drop=True
    )
)


# ---------------------------------------------------------------------
# Structural validation
# ---------------------------------------------------------------------

print("\n" + "=" * 100)
print("STRUCTURAL VALIDATION")
print("=" * 100)


print("\nFinal rows:")
print(len(final))

print("\nExpected rows:")
print(EXPECTED_ROWS)


if len(final) != EXPECTED_ROWS:
    raise ValueError(
        f"Expected {EXPECTED_ROWS} County-Year rows, "
        f"found {len(final)}."
    )


years = set(
    final["year"]
    .unique()
)


print("\nYears:")
print(sorted(years))


if years != EXPECTED_YEARS:
    raise ValueError(
        "Unexpected year coverage."
    )


county_counts = (
    final
    .groupby("year")["county_code"]
    .nunique()
)


print("\nCounty count by year:")
print(county_counts)


if not (
    county_counts
    == EXPECTED_COUNTIES
).all():
    raise ValueError(
        "At least one year does not contain 42 counties."
    )


duplicate_keys = (
    final
    .duplicated(
        subset=[
            "county_code",
            "year",
        ]
    )
    .sum()
)


print("\nDuplicate County-Year keys:")
print(duplicate_keys)


if duplicate_keys != 0:
    raise ValueError(
        "Duplicate County-Year analytical keys detected."
    )


# ---------------------------------------------------------------------
# Accounting identities
# ---------------------------------------------------------------------

candidate_identity = (
    final["candidates"]
    == (
        final["passed_candidates"]
        + final["failed_candidates"]
        + final["absent_candidates"]
        + final["eliminated_candidates"]
    )
)


present_identity = (
    final["present_candidates"]
    == (
        final["passed_candidates"]
        + final["failed_candidates"]
        + final["eliminated_candidates"]
    )
)


print("\nCandidate accounting identity valid:")
print(candidate_identity.all())

print("\nPresent-candidate identity valid:")
print(present_identity.all())


if not candidate_identity.all():
    raise ValueError(
        "Candidate accounting identity failed."
    )


if not present_identity.all():
    raise ValueError(
        "Present-candidate accounting identity failed."
    )


# ---------------------------------------------------------------------
# Indicator validation
# ---------------------------------------------------------------------

if not final["pass_rate"].between(
    0,
    1,
    inclusive="both",
).all():
    raise ValueError(
        "Invalid pass_rate detected."
    )


if not final["average_grade"].between(
    1,
    10,
    inclusive="both",
).all():
    raise ValueError(
        "Invalid average_grade detected."
    )


if (
    final["graded_candidates"]
    > final["candidates"]
).any():
    raise ValueError(
        "graded_candidates exceeds candidates."
    )


# ---------------------------------------------------------------------
# National totals validation
# ---------------------------------------------------------------------

national = (
    final
    .groupby(
        "year",
        as_index=False,
    )
    .agg(
        candidates=(
            "candidates",
            "sum",
        ),
        present_candidates=(
            "present_candidates",
            "sum",
        ),
        passed_candidates=(
            "passed_candidates",
            "sum",
        ),
        failed_candidates=(
            "failed_candidates",
            "sum",
        ),
        absent_candidates=(
            "absent_candidates",
            "sum",
        ),
        eliminated_candidates=(
            "eliminated_candidates",
            "sum",
        ),
        graded_candidates=(
            "graded_candidates",
            "sum",
        ),
        final_grade_sum=(
            "final_grade_sum",
            "sum",
        ),
    )
)


national["pass_rate"] = (
    national["passed_candidates"]
    / national["present_candidates"]
)


national["average_grade"] = (
    national["final_grade_sum"]
    / national["graded_candidates"]
)


print("\n" + "=" * 100)
print("NATIONAL VALIDATION")
print("=" * 100)


print(
    national[
        [
            "year",
            "candidates",
            "present_candidates",
            "passed_candidates",
            "pass_rate",
            "graded_candidates",
            "average_grade",
        ]
    ]
    .to_string(
        index=False
    )
)


for _, row in national.iterrows():

    year = int(
        row["year"]
    )

    candidates = int(
        row["candidates"]
    )

    expected = (
        EXPECTED_NATIONAL_CANDIDATES[
            year
        ]
    )

    if candidates != expected:
        raise ValueError(
            f"{year}: candidate total mismatch. "
            f"Expected {expected}, found {candidates}."
        )


# ---------------------------------------------------------------------
# Missing-value validation
# ---------------------------------------------------------------------

print("\nMissing values:")
print(
    final
    .isna()
    .sum()
)


if final.isna().any().any():
    raise ValueError(
        "Unexpected missing values detected "
        "in final Baccalaureate dataset."
    )


# ---------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


final.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8",
)


print("\n" + "=" * 100)
print("FINAL OUTPUT")
print("=" * 100)


print("\nOutput:")
print(OUTPUT_PATH)

print("\nShape:")
print(final.shape)

print("\nFile size:")
print(
    OUTPUT_PATH.stat().st_size
)


print("\nFirst rows:")
print(
    final
    .head(10)
    .to_string(
        index=False
    )
)


print(
    "\nBaccalaureate County-Year aggregation "
    "completed successfully."
)