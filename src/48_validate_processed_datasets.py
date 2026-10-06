from pathlib import Path
import sys
import re
import unicodedata

import numpy as np
import pandas as pd


# =====================================================================
# Configuration
# =====================================================================

PROCESSED_DIR = Path("data/processed")

EMPLOYMENT_PATH = (
    PROCESSED_DIR
    / "employment_clean.csv"
)

ENROLLMENT_PATH = (
    PROCESSED_DIR
    / "enrollment_clean.csv"
)

BACCALAUREATE_PATH = (
    PROCESSED_DIR
    / "baccalaureate_clean.csv"
)


EXPECTED_EMPLOYMENT_YEARS = set(
    range(2014, 2024)
)

EXPECTED_ENROLLMENT_YEARS = set(
    range(2015, 2024)
)

EXPECTED_BACCALAUREATE_YEARS = set(
    range(2015, 2024)
)

EXPECTED_COUNTIES = 42


EXPECTED_EDUCATION_LEVELS = {
    "anteprescolar",
    "prescolar",
    "primar",
    "gimnazial",
    "profesional",
    "liceal",
    "postliceal",
}


# =====================================================================
# Result tracking
# =====================================================================

ERRORS = []
WARNINGS = []


def pass_check(message):
    print(f"[PASS] {message}")


def fail_check(message):
    print(f"[FAIL] {message}")
    ERRORS.append(message)


def warn_check(message):
    print(f"[WARN] {message}")
    WARNINGS.append(message)


def section(title):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


# =====================================================================
# Helpers
# =====================================================================

def normalize_text(value):
    """
    Normalize Romanian text for safe comparisons.
    """

    value = str(value).strip().lower()

    value = (
        unicodedata
        .normalize(
            "NFKD",
            value,
        )
    )

    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    value = (
        value
        .replace("ş", "s")
        .replace("ș", "s")
        .replace("ţ", "t")
        .replace("ț", "t")
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


def extract_school_year_start(value):
    """
    Extract start year from formats such as:
    2015-2016
    2015-16
    2015_2016
    2015/2016
    """

    if pd.isna(value):
        return np.nan

    text = str(value)

    match = re.search(
        r"(20\d{2})",
        text,
    )

    if not match:
        return np.nan

    return int(
        match.group(1)
    )


def require_columns(
    df,
    expected_columns,
    dataset_name,
):
    missing = (
        set(expected_columns)
        - set(df.columns)
    )

    if missing:
        fail_check(
            f"{dataset_name}: missing columns: "
            f"{sorted(missing)}"
        )

        return False

    pass_check(
        f"{dataset_name}: all required columns exist"
    )

    return True


def check_missing_values(
    df,
    dataset_name,
):
    missing = (
        df
        .isna()
        .sum()
    )

    total_missing = int(
        missing.sum()
    )

    if total_missing == 0:

        pass_check(
            f"{dataset_name}: no missing values"
        )

    else:

        fail_check(
            f"{dataset_name}: "
            f"{total_missing} missing values found"
        )

        print(
            missing[
                missing > 0
            ]
        )


def check_duplicate_key(
    df,
    key_columns,
    dataset_name,
):
    duplicates = (
        df
        .duplicated(
            subset=key_columns,
            keep=False,
        )
    )

    duplicate_count = int(
        duplicates.sum()
    )

    if duplicate_count == 0:

        pass_check(
            f"{dataset_name}: "
            f"no duplicate analytical keys "
            f"{key_columns}"
        )

    else:

        fail_check(
            f"{dataset_name}: "
            f"{duplicate_count} rows belong "
            f"to duplicate analytical keys"
        )

        print(
            df.loc[
                duplicates,
                key_columns
            ]
            .sort_values(
                key_columns
            )
            .head(20)
        )


def check_nonnegative(
    df,
    columns,
    dataset_name,
):
    for column in columns:

        if column not in df.columns:
            continue

        numeric = pd.to_numeric(
            df[column],
            errors="coerce",
        )

        invalid_numeric = (
            numeric.isna()
            & df[column].notna()
        )

        if invalid_numeric.any():

            fail_check(
                f"{dataset_name}: "
                f"{column} contains "
                f"non-numeric values"
            )

            continue

        negative_count = int(
            (numeric < 0).sum()
        )

        if negative_count == 0:

            pass_check(
                f"{dataset_name}: "
                f"{column} contains "
                f"no negative values"
            )

        else:

            fail_check(
                f"{dataset_name}: "
                f"{column} contains "
                f"{negative_count} negative values"
            )


def check_years(
    df,
    year_column,
    expected_years,
    dataset_name,
):
    actual_years = set(
        pd.to_numeric(
            df[year_column],
            errors="coerce",
        )
        .dropna()
        .astype(int)
        .unique()
    )

    print(
        f"{dataset_name} years: "
        f"{sorted(actual_years)}"
    )

    if actual_years == expected_years:

        pass_check(
            f"{dataset_name}: "
            f"expected year coverage confirmed"
        )

    else:

        missing = (
            expected_years
            - actual_years
        )

        unexpected = (
            actual_years
            - expected_years
        )

        fail_check(
            f"{dataset_name}: "
            f"year coverage mismatch | "
            f"missing={sorted(missing)}, "
            f"unexpected={sorted(unexpected)}"
        )


def check_counties_per_year(
    df,
    year_column,
    county_column,
    expected_count,
    dataset_name,
):
    counts = (
        df
        .groupby(year_column)[county_column]
        .nunique()
        .sort_index()
    )

    print(
        "\nCounties per year:"
    )

    print(counts)

    invalid = counts[
        counts != expected_count
    ]

    if invalid.empty:

        pass_check(
            f"{dataset_name}: "
            f"every year contains "
            f"{expected_count} counties"
        )

    else:

        fail_check(
            f"{dataset_name}: "
            f"some years do not contain "
            f"{expected_count} counties"
        )

        print(invalid)


# =====================================================================
# Load datasets
# =====================================================================

section(
    "FINAL PROCESSED DATA VALIDATION"
)


for path in [
    EMPLOYMENT_PATH,
    ENROLLMENT_PATH,
    BACCALAUREATE_PATH,
]:

    if not path.exists():

        fail_check(
            f"File not found: {path}"
        )


if ERRORS:

    print(
        "\nRequired files are missing. "
        "Validation cannot continue."
    )

    sys.exit(1)


employment = pd.read_csv(
    EMPLOYMENT_PATH
)

enrollment = pd.read_csv(
    ENROLLMENT_PATH
)

baccalaureate = pd.read_csv(
    BACCALAUREATE_PATH
)


print(
    f"\nEmployment shape: "
    f"{employment.shape}"
)

print(
    f"Enrollment shape: "
    f"{enrollment.shape}"
)

print(
    f"Baccalaureate shape: "
    f"{baccalaureate.shape}"
)


# =====================================================================
# EMPLOYMENT
# =====================================================================

section(
    "1. EMPLOYMENT VALIDATION"
)


EMPLOYMENT_COLUMNS = [
    "county_code",
    "county",
    "year",
    "employees_thousands",
    "employees",
]


if require_columns(
    employment,
    EMPLOYMENT_COLUMNS,
    "Employment",
):

    check_missing_values(
        employment,
        "Employment",
    )

    check_duplicate_key(
        employment,
        [
            "county_code",
            "year",
        ],
        "Employment",
    )

    check_years(
        employment,
        "year",
        EXPECTED_EMPLOYMENT_YEARS,
        "Employment",
    )

    county_count = (
        employment[
            "county_code"
        ]
        .nunique()
    )

    print(
        f"\nUnique counties: "
        f"{county_count}"
    )

    if county_count == EXPECTED_COUNTIES:

        pass_check(
            "Employment: 42 unique counties"
        )

    else:

        fail_check(
            f"Employment: expected 42 counties, "
            f"found {county_count}"
        )

    check_counties_per_year(
        employment,
        "year",
        "county_code",
        EXPECTED_COUNTIES,
        "Employment",
    )

    check_nonnegative(
        employment,
        [
            "employees_thousands",
            "employees",
        ],
        "Employment",
    )

    expected_employees = (
        pd.to_numeric(
            employment[
                "employees_thousands"
            ],
            errors="coerce",
        )
        * 1000
    ).round()

    actual_employees = (
        pd.to_numeric(
            employment[
                "employees"
            ],
            errors="coerce",
        )
    )

    employee_mismatch = (
        expected_employees
        != actual_employees
    )

    mismatch_count = int(
        employee_mismatch.sum()
    )

    if mismatch_count == 0:

        pass_check(
            "Employment: employees = "
            "employees_thousands × 1000"
        )

    else:

        fail_check(
            f"Employment: "
            f"{mismatch_count} rows fail "
            f"employees conversion validation"
        )

    county_name_counts = (
        employment
        .groupby(
            "county_code"
        )["county"]
        .nunique()
    )

    inconsistent = (
        county_name_counts[
            county_name_counts != 1
        ]
    )

    if inconsistent.empty:

        pass_check(
            "Employment: each county_code "
            "maps to exactly one county name"
        )

    else:

        fail_check(
            "Employment: inconsistent "
            "county_code -> county mapping"
        )

        print(inconsistent)


# =====================================================================
# ENROLLMENT
# =====================================================================

section(
    "2. ENROLLMENT VALIDATION"
)


ENROLLMENT_COLUMNS = [
    "county_code",
    "county_abbr",
    "school_year",
    "analysis_year",
    "education_level",
    "enrolled_students",
]


if require_columns(
    enrollment,
    ENROLLMENT_COLUMNS,
    "Enrollment",
):

    check_missing_values(
        enrollment,
        "Enrollment",
    )

    check_duplicate_key(
        enrollment,
        [
            "county_code",
            "analysis_year",
            "education_level",
        ],
        "Enrollment",
    )

    check_years(
        enrollment,
        "analysis_year",
        EXPECTED_ENROLLMENT_YEARS,
        "Enrollment",
    )

    county_count = (
        enrollment[
            "county_code"
        ]
        .nunique()
    )

    print(
        f"\nUnique counties: "
        f"{county_count}"
    )

    if county_count == EXPECTED_COUNTIES:

        pass_check(
            "Enrollment: 42 unique counties"
        )

    else:

        fail_check(
            f"Enrollment: expected 42 counties, "
            f"found {county_count}"
        )

    check_counties_per_year(
        enrollment,
        "analysis_year",
        "county_code",
        EXPECTED_COUNTIES,
        "Enrollment",
    )

    check_nonnegative(
        enrollment,
        [
            "enrolled_students",
        ],
        "Enrollment",
    )

    normalized_levels = {
        normalize_text(value)
        for value in enrollment[
            "education_level"
        ].dropna().unique()
    }

    print(
        "\nEducation levels:"
    )

    for value in sorted(
        enrollment[
            "education_level"
        ].dropna().unique()
    ):
        print(
            f"- {value}"
        )

    if normalized_levels == EXPECTED_EDUCATION_LEVELS:

        pass_check(
            "Enrollment: expected "
            "7 education levels confirmed"
        )

    else:

        fail_check(
            "Enrollment: education-level "
            "set differs from expected"
        )

        print(
            "Normalized levels found:"
        )

        print(
            sorted(
                normalized_levels
            )
        )

    school_start = (
        enrollment[
            "school_year"
        ]
        .apply(
            extract_school_year_start
        )
    )

    analysis_year = (
        pd.to_numeric(
            enrollment[
                "analysis_year"
            ],
            errors="coerce",
        )
    )

    invalid_school_year = (
        school_start.isna()
    )

    if invalid_school_year.any():

        fail_check(
            "Enrollment: some school_year "
            "values could not be parsed"
        )

        print(
            enrollment.loc[
                invalid_school_year,
                [
                    "school_year",
                    "analysis_year",
                ],
            ]
            .drop_duplicates()
            .head(20)
        )

    else:

        mismatch = (
            school_start
            != analysis_year
        )

        mismatch_count = int(
            mismatch.sum()
        )

        if mismatch_count == 0:

            pass_check(
                "Enrollment: analysis_year equals "
                "school-year starting year"
            )

        else:

            fail_check(
                f"Enrollment: "
                f"{mismatch_count} rows have "
                f"school_year / analysis_year mismatch"
            )

    abbreviation_counts = (
        enrollment
        .groupby(
            "county_code"
        )["county_abbr"]
        .nunique()
    )

    inconsistent = (
        abbreviation_counts[
            abbreviation_counts != 1
        ]
    )

    if inconsistent.empty:

        pass_check(
            "Enrollment: each county_code maps "
            "to one county abbreviation"
        )

    else:

        fail_check(
            "Enrollment: inconsistent "
            "county_code -> county_abbr mapping"
        )

        print(inconsistent)


# =====================================================================
# BACCALAUREATE
# =====================================================================

section(
    "3. BACCALAUREATE VALIDATION"
)


BACCALAUREATE_COLUMNS = [
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


if require_columns(
    baccalaureate,
    BACCALAUREATE_COLUMNS,
    "Baccalaureate",
):

    check_missing_values(
        baccalaureate,
        "Baccalaureate",
    )

    check_duplicate_key(
        baccalaureate,
        [
            "county_code",
            "year",
        ],
        "Baccalaureate",
    )

    check_years(
        baccalaureate,
        "year",
        EXPECTED_BACCALAUREATE_YEARS,
        "Baccalaureate",
    )

    county_count = (
        baccalaureate[
            "county_code"
        ]
        .nunique()
    )

    print(
        f"\nUnique counties: "
        f"{county_count}"
    )

    if county_count == EXPECTED_COUNTIES:

        pass_check(
            "Baccalaureate: 42 unique counties"
        )

    else:

        fail_check(
            f"Baccalaureate: expected 42 counties, "
            f"found {county_count}"
        )

    check_counties_per_year(
        baccalaureate,
        "year",
        "county_code",
        EXPECTED_COUNTIES,
        "Baccalaureate",
    )

    COUNT_COLUMNS = [
        "candidates",
        "present_candidates",
        "passed_candidates",
        "failed_candidates",
        "absent_candidates",
        "eliminated_candidates",
        "graded_candidates",
        "final_grade_sum",
    ]

    check_nonnegative(
        baccalaureate,
        COUNT_COLUMNS,
        "Baccalaureate",
    )

    calculated_candidates = (
        baccalaureate[
            "passed_candidates"
        ]
        + baccalaureate[
            "failed_candidates"
        ]
        + baccalaureate[
            "absent_candidates"
        ]
        + baccalaureate[
            "eliminated_candidates"
        ]
    )

    candidate_mismatch = (
        baccalaureate[
            "candidates"
        ]
        != calculated_candidates
    )

    if not candidate_mismatch.any():

        pass_check(
            "Baccalaureate: candidate accounting valid"
        )

    else:

        fail_check(
            f"Baccalaureate: "
            f"{candidate_mismatch.sum()} rows fail "
            f"candidate accounting"
        )

    calculated_present = (
        baccalaureate[
            "passed_candidates"
        ]
        + baccalaureate[
            "failed_candidates"
        ]
        + baccalaureate[
            "eliminated_candidates"
        ]
    )

    present_mismatch = (
        baccalaureate[
            "present_candidates"
        ]
        != calculated_present
    )

    if not present_mismatch.any():

        pass_check(
            "Baccalaureate: present-candidate "
            "accounting valid"
        )

    else:

        fail_check(
            f"Baccalaureate: "
            f"{present_mismatch.sum()} rows fail "
            f"present-candidate accounting"
        )

    invalid_graded = (
        baccalaureate[
            "graded_candidates"
        ]
        >
        (
            baccalaureate[
                "passed_candidates"
            ]
            +
            baccalaureate[
                "failed_candidates"
            ]
        )
    )

    if not invalid_graded.any():

        pass_check(
            "Baccalaureate: graded_candidates "
            "does not exceed passed + failed"
        )

    else:

        fail_check(
            f"Baccalaureate: "
            f"{invalid_graded.sum()} rows have "
            f"too many graded candidates"
        )

    calculated_pass_rate = np.where(
        baccalaureate[
            "present_candidates"
        ] > 0,
        (
            baccalaureate[
                "passed_candidates"
            ]
            /
            baccalaureate[
                "present_candidates"
            ]
        ),
        np.nan,
    )

    stored_pass_rate = (
        pd.to_numeric(
            baccalaureate[
                "pass_rate"
            ],
            errors="coerce",
        )
    )

    pass_rate_match = np.isclose(
        calculated_pass_rate,
        stored_pass_rate,
        rtol=0,
        atol=1e-6,
        equal_nan=True,
    )

    if pass_rate_match.all():

        pass_check(
            "Baccalaureate: pass_rate = "
            "passed / present"
        )

    else:

        fail_check(
            f"Baccalaureate: "
            f"{(~pass_rate_match).sum()} rows "
            f"have incorrect pass_rate"
        )

    invalid_pass_rate = (
        (
            stored_pass_rate < 0
        )
        |
        (
            stored_pass_rate > 1
        )
    )

    if not invalid_pass_rate.any():

        pass_check(
            "Baccalaureate: pass_rate "
            "is between 0 and 1"
        )

    else:

        fail_check(
            "Baccalaureate: invalid "
            "pass_rate values detected"
        )

    calculated_average_grade = np.where(
        baccalaureate[
            "graded_candidates"
        ] > 0,
        (
            baccalaureate[
                "final_grade_sum"
            ]
            /
            baccalaureate[
                "graded_candidates"
            ]
        ),
        np.nan,
    )

    stored_average_grade = (
        pd.to_numeric(
            baccalaureate[
                "average_grade"
            ],
            errors="coerce",
        )
    )

    average_difference = (
        calculated_average_grade
        - stored_average_grade
    )

    print(
        "\nMaximum absolute average-grade difference:"
    )

    print(
        np.nanmax(
            np.abs(
                average_difference
            )
        )
    )

    average_match = np.isclose(
        calculated_average_grade,
        stored_average_grade,
        rtol=0,
        atol=0.0051,
        equal_nan=True,
    )

    if average_match.all():

        pass_check(
            "Baccalaureate: average_grade = "
            "final_grade_sum / graded_candidates "
            "(within rounding tolerance)"
        )

    else:

        fail_check(
            f"Baccalaureate: "
            f"{(~average_match).sum()} rows "
            f"have incorrect average_grade"
        )

        mismatch_rows = (
            baccalaureate.loc[
                ~average_match,
                [
                    "county_code",
                    "county",
                    "year",
                    "graded_candidates",
                    "final_grade_sum",
                    "average_grade",
                ],
            ]
            .copy()
        )

        mismatch_rows[
            "calculated_average_grade"
        ] = calculated_average_grade[
            ~average_match
        ]

        mismatch_rows[
            "difference"
        ] = (
            mismatch_rows[
                "calculated_average_grade"
            ]
            - mismatch_rows[
                "average_grade"
            ]
        )

        print(
            "\nLargest average-grade mismatches:"
        )

        print(
            mismatch_rows
            .assign(
                absolute_difference=lambda x: (
                    x["difference"].abs()
                )
            )
            .sort_values(
                "absolute_difference",
                ascending=False,
            )
            .head(20)
            .to_string(
                index=False
            )
        )

    invalid_average = (
        (
            stored_average_grade < 1
        )
        |
        (
            stored_average_grade > 10
        )
    )

    if not invalid_average.any():

        pass_check(
            "Baccalaureate: average_grade "
            "is between 1 and 10"
        )

    else:

        fail_check(
            "Baccalaureate: invalid "
            "average_grade values detected"
        )

    county_name_counts = (
        baccalaureate
        .groupby(
            "county_code"
        )["county"]
        .nunique()
    )

    county_abbr_counts = (
        baccalaureate
        .groupby(
            "county_code"
        )["county_abbr"]
        .nunique()
    )

    if (
        county_name_counts.eq(1).all()
        and
        county_abbr_counts.eq(1).all()
    ):

        pass_check(
            "Baccalaureate: county mappings "
            "are internally consistent"
        )

    else:

        fail_check(
            "Baccalaureate: inconsistent "
            "county mappings detected"
        )


# =====================================================================
# CROSS-DATASET COUNTY VALIDATION
# =====================================================================

section(
    "4. CROSS-DATASET COUNTY VALIDATION"
)


employment_codes = set(
    employment[
        "county_code"
    ].astype(str)
)

enrollment_codes = set(
    enrollment[
        "county_code"
    ].astype(str)
)

baccalaureate_codes = set(
    baccalaureate[
        "county_code"
    ].astype(str)
)


if (
    employment_codes
    ==
    enrollment_codes
    ==
    baccalaureate_codes
):

    pass_check(
        "All three datasets use the same "
        "42 county codes"
    )

else:

    fail_check(
        "County-code sets differ "
        "between datasets"
    )

    print(
        "\nOnly in Employment:"
    )

    print(
        sorted(
            employment_codes
            - enrollment_codes
            - baccalaureate_codes
        )
    )

    print(
        "\nOnly in Enrollment:"
    )

    print(
        sorted(
            enrollment_codes
            - employment_codes
            - baccalaureate_codes
        )
    )

    print(
        "\nOnly in Baccalaureate:"
    )

    print(
        sorted(
            baccalaureate_codes
            - employment_codes
            - enrollment_codes
        )
    )


employment_counties = (
    employment[
        [
            "county_code",
            "county",
        ]
    ]
    .drop_duplicates()
    .sort_values(
        "county_code"
    )
)

bac_counties = (
    baccalaureate[
        [
            "county_code",
            "county",
        ]
    ]
    .drop_duplicates()
    .sort_values(
        "county_code"
    )
)


county_comparison = (
    employment_counties
    .merge(
        bac_counties,
        on="county_code",
        how="outer",
        suffixes=(
            "_employment",
            "_baccalaureate",
        ),
    )
)


county_name_mismatch = (
    county_comparison[
        "county_employment"
    ]
    !=
    county_comparison[
        "county_baccalaureate"
    ]
)


if not county_name_mismatch.any():

    pass_check(
        "Employment and Baccalaureate use "
        "the same county names"
    )

else:

    fail_check(
        "Employment and Baccalaureate "
        "county names differ"
    )

    print(
        county_comparison.loc[
            county_name_mismatch
        ]
    )


enrollment_abbr = (
    enrollment[
        [
            "county_code",
            "county_abbr",
        ]
    ]
    .drop_duplicates()
)

bac_abbr = (
    baccalaureate[
        [
            "county_code",
            "county_abbr",
        ]
    ]
    .drop_duplicates()
)


abbr_comparison = (
    enrollment_abbr
    .merge(
        bac_abbr,
        on="county_code",
        how="outer",
        suffixes=(
            "_enrollment",
            "_baccalaureate",
        ),
    )
)


abbr_mismatch = (
    abbr_comparison[
        "county_abbr_enrollment"
    ]
    !=
    abbr_comparison[
        "county_abbr_baccalaureate"
    ]
)


if not abbr_mismatch.any():

    pass_check(
        "Enrollment and Baccalaureate use "
        "the same county abbreviations"
    )

else:

    fail_check(
        "Enrollment and Baccalaureate "
        "county abbreviations differ"
    )

    print(
        abbr_comparison.loc[
            abbr_mismatch
        ]
    )


# =====================================================================
# NATIONAL TOTALS / SANITY SUMMARY
# =====================================================================

section(
    "5. NATIONAL SANITY SUMMARY"
)


print(
    "\nEMPLOYMENT - national employees by year"
)

print(
    employment
    .groupby(
        "year"
    )["employees"]
    .sum()
)


print(
    "\nENROLLMENT - national enrolled students by analysis year"
)

print(
    enrollment
    .groupby(
        "analysis_year"
    )["enrolled_students"]
    .sum()
)


print(
    "\nBACCALAUREATE - national summary"
)

bac_national = (
    baccalaureate
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


bac_national[
    "pass_rate"
] = (
    bac_national[
        "passed_candidates"
    ]
    /
    bac_national[
        "present_candidates"
    ]
)


bac_national[
    "average_grade"
] = (
    bac_national[
        "final_grade_sum"
    ]
    /
    bac_national[
        "graded_candidates"
    ]
)


print(
    bac_national.to_string(
        index=False
    )
)


# =====================================================================
# FINAL RESULT
# =====================================================================

section(
    "FINAL VALIDATION RESULT"
)


print(
    f"\nErrors: "
    f"{len(ERRORS)}"
)

print(
    f"Warnings: "
    f"{len(WARNINGS)}"
)


if WARNINGS:

    print(
        "\nWarnings:"
    )

    for warning in WARNINGS:

        print(
            f"- {warning}"
        )


if ERRORS:

    print(
        "\nErrors:"
    )

    for error in ERRORS:

        print(
            f"- {error}"
        )

    print(
        "\nFINAL STATUS: FAIL"
    )

    sys.exit(1)


print(
    "\nFINAL STATUS: PASS"
)

print(
    "\nAll three processed datasets passed "
    "the final structural and analytical validation."
)

print(
    "\nThe processed-data layer is ready "
    "for Power BI modeling."
)