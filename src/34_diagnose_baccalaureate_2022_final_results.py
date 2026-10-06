from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

FILE_PATH = Path(
    "data/raw/baccalaureate/baccalaureate_2022_session1_raw.xlsx"
)

STATUS_COLUMN = "STATUS_FINAL"
GRADE_COLUMN = "MEDIA_FINALA"


# ---------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------

df = pd.read_excel(
    FILE_PATH,
    sheet_name=0,
    dtype={
        "Cod SIIIR": str,
        "Cod": str,
    }
)

print("=" * 100)
print("2022 BACCALAUREATE FINAL RESULT DIAGNOSIS")
print("=" * 100)


# ---------------------------------------------------------------------
# Basic checks
# ---------------------------------------------------------------------

print("\nRows:")
print(len(df))

print("\nSTATUS_FINAL distribution:")
print(
    df[STATUS_COLUMN]
    .value_counts(dropna=False)
)


# ---------------------------------------------------------------------
# Convert final grade safely to numeric
# ---------------------------------------------------------------------

df["media_finala_numeric"] = pd.to_numeric(
    df[GRADE_COLUMN],
    errors="coerce"
)

print("\nMEDIA_FINALA missing after numeric conversion:")
print(df["media_finala_numeric"].isna().sum())


# ---------------------------------------------------------------------
# Exact negative values
# ---------------------------------------------------------------------

negative_values = (
    df.loc[
        df["media_finala_numeric"] < 0,
        "media_finala_numeric"
    ]
    .value_counts()
    .sort_index()
)

print("\nNegative MEDIA_FINALA values:")
print(negative_values)


# ---------------------------------------------------------------------
# Cross-tab: status versus negative/special grades
# ---------------------------------------------------------------------

special_rows = df[
    df["media_finala_numeric"] < 0
].copy()

print("\nSTATUS_FINAL distribution among negative MEDIA_FINALA rows:")
print(
    special_rows[STATUS_COLUMN]
    .value_counts(dropna=False)
)


print("\nCross-tab STATUS_FINAL × negative MEDIA_FINALA:")
print(
    pd.crosstab(
        special_rows[STATUS_COLUMN],
        special_rows["media_finala_numeric"],
        dropna=False
    )
)


# ---------------------------------------------------------------------
# Grade summary by final status
# ---------------------------------------------------------------------

print("\nMEDIA_FINALA summary by STATUS_FINAL:")
print(
    df.groupby(STATUS_COLUMN)["media_finala_numeric"]
    .agg(
        count="count",
        min="min",
        max="max",
        mean="mean",
        median="median"
    )
    .sort_index()
)


# ---------------------------------------------------------------------
# Valid school-grade range
# ---------------------------------------------------------------------

valid_grade_mask = df["media_finala_numeric"].between(
    1,
    10,
    inclusive="both"
)

print("\nRows with MEDIA_FINALA between 1 and 10:")
print(valid_grade_mask.sum())

print("\nSTATUS_FINAL distribution for grades between 1 and 10:")
print(
    df.loc[
        valid_grade_mask,
        STATUS_COLUMN
    ].value_counts(dropna=False)
)


# ---------------------------------------------------------------------
# Check promoted candidates
# ---------------------------------------------------------------------

promoted = df[
    df[STATUS_COLUMN] == "Promovat"
]

print("\nPromoted candidates:")
print(len(promoted))

print("\nPromoted candidates with MEDIA_FINALA < 6:")
print(
    (
        promoted["media_finala_numeric"] < 6
    ).sum()
)

print("\nPromoted candidates with MEDIA_FINALA >= 6:")
print(
    (
        promoted["media_finala_numeric"] >= 6
    ).sum()
)


# ---------------------------------------------------------------------
# Check non-promoted candidates
# ---------------------------------------------------------------------

failed = df[
    df[STATUS_COLUMN] == "Nepromovat"
]

print("\nNepromovat candidates:")
print(len(failed))

print("\nNepromovat candidates with MEDIA_FINALA >= 6:")
print(
    (
        failed["media_finala_numeric"] >= 6
    ).sum()
)

print("\nNepromovat candidates with MEDIA_FINALA between 1 and 10:")
print(
    failed["media_finala_numeric"]
    .between(1, 10, inclusive="both")
    .sum()
)


# ---------------------------------------------------------------------
# Candidate categories useful for future aggregation
# ---------------------------------------------------------------------

print("\nPotential KPI counts:")

print("All candidate rows:")
print(len(df))

print("Promovat:")
print((df[STATUS_COLUMN] == "Promovat").sum())

print("Nepromovat:")
print((df[STATUS_COLUMN] == "Nepromovat").sum())

print("Absent:")
print((df[STATUS_COLUMN] == "Absent").sum())

print("Eliminat:")
print((df[STATUS_COLUMN] == "Eliminat").sum())

print("Promovat + Nepromovat:")
print(
    df[STATUS_COLUMN]
    .isin(["Promovat", "Nepromovat"])
    .sum()
)


print("\nDiagnosis completed.")