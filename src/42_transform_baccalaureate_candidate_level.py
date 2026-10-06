from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

RAW_DIR = Path("data/raw/baccalaureate")
INTERIM_DIR = Path("data/interim")

OUTPUT_PATH = (
    INTERIM_DIR
    / "baccalaureate_candidate_standardized.csv"
)


FILES = {
    2015: RAW_DIR / "baccalaureate_2015_session1_raw.csv",
    2016: RAW_DIR / "baccalaureate_2016_session1_raw.ods",
    2017: RAW_DIR / "baccalaureate_2017_session1_raw.ods",
    2018: RAW_DIR / "baccalaureate_2018_session1_raw.xlsx",
    2019: RAW_DIR / "baccalaureate_2019_session1_raw.xlsx",
    2020: RAW_DIR / "baccalaureate_2020_session1_raw.xlsx",
    2021: RAW_DIR / "baccalaureate_2021_session1_raw.xlsx",
    2022: RAW_DIR / "baccalaureate_2022_session1_raw.xlsx",
    2023: RAW_DIR / "baccalaureate_2023_session1_raw.xlsx",
}


EXPECTED_ROWS = {
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


ALLOWED_STATUSES = {
    "Promovat",
    "Nepromovat",
    "Absent",
    "Eliminat",
}


OLD_COLUMNS = [
    "Cod unic candidat",
    "Unitate (SIIIR)",
    "STATUS",
    "Medie",
]


NEW_COLUMNS = [
    "Cod",
    "Cod SIIIR",
    "Judet",
    "STATUS_FINAL",
    "MEDIA_FINALA",
]


# ---------------------------------------------------------------------
# ODS namespaces
# ---------------------------------------------------------------------

NS = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
}


# ---------------------------------------------------------------------
# General helpers
# ---------------------------------------------------------------------

def normalize_column_name(value):
    return (
        str(value)
        .replace("\ufeff", "")
        .strip()
    )


def normalize_identifier(series):
    return (
        series
        .astype("string")
        .str.strip()
        .str.replace(
            r"\.0$",
            "",
            regex=True,
        )
    )


def normalize_grade(series):

    cleaned = (
        series
        .astype("string")
        .str.strip()
        .str.replace(
            ",",
            ".",
            regex=False,
        )
    )

    numeric = pd.to_numeric(
        cleaned,
        errors="coerce",
    )

    # Only actual school averages are retained.
    # Administrative values such as -1, -2 and -3 become missing.
    valid_grade = numeric.where(
        numeric.between(
            1,
            10,
            inclusive="both",
        )
    )

    return valid_grade.astype("Float64")


# ---------------------------------------------------------------------
# ODS helpers
# ---------------------------------------------------------------------

def get_cell_text(cell):

    paragraphs = []

    for paragraph in cell.findall(
        ".//text:p",
        NS,
    ):
        value = "".join(
            paragraph.itertext()
        ).strip()

        if value:
            paragraphs.append(value)

    if paragraphs:
        return " ".join(paragraphs)

    numeric_value = cell.get(
        f"{{{NS['office']}}}value"
    )

    if numeric_value is not None:
        return numeric_value

    string_value = cell.get(
        f"{{{NS['office']}}}string-value"
    )

    if string_value is not None:
        return string_value

    return ""


def extract_ods_row_values(
    row,
    max_columns=60,
):

    values = []

    for cell in row:

        if cell.tag not in {
            f"{{{NS['table']}}}table-cell",
            f"{{{NS['table']}}}covered-table-cell",
        }:
            continue

        repeat = int(
            cell.get(
                f"{{{NS['table']}}}number-columns-repeated",
                "1",
            )
        )

        value = get_cell_text(cell)

        remaining = (
            max_columns
            - len(values)
        )

        if remaining <= 0:
            break

        repeat_to_use = min(
            repeat,
            remaining,
        )

        values.extend(
            [value] * repeat_to_use
        )

    return values


# ---------------------------------------------------------------------
# ODS selective reader for 2016 / 2017
# ---------------------------------------------------------------------

def read_ods_selected_columns(
    path,
    requested_columns,
):

    with zipfile.ZipFile(
        path,
        "r",
    ) as archive:

        with archive.open(
            "content.xml"
        ) as xml_file:

            tree = ET.parse(
                xml_file
            )

    root = tree.getroot()

    tables = root.findall(
        ".//table:table",
        NS,
    )

    if not tables:
        raise ValueError(
            f"No worksheets found in {path}"
        )

    selected_table = None

    for table in tables:

        sheet_name = table.get(
            f"{{{NS['table']}}}name"
        )

        if sheet_name == "Export_Worksheet":
            selected_table = table
            break

    if selected_table is None:
        selected_table = tables[0]

    header = None
    requested_indices = None

    output = {
        column: []
        for column in requested_columns
    }

    for row in selected_table.findall(
        "table:table-row",
        NS,
    ):

        row_repeat = int(
            row.get(
                f"{{{NS['table']}}}number-rows-repeated",
                "1",
            )
        )

        values = extract_ods_row_values(
            row
        )

        # -------------------------------------------------------------
        # Find header
        # -------------------------------------------------------------

        if header is None:

            normalized_values = [
                normalize_column_name(value)
                for value in values
            ]

            if (
                "Cod unic candidat"
                in normalized_values
            ):

                header = normalized_values

                requested_indices = {}

                for column in requested_columns:

                    if column not in header:
                        raise KeyError(
                            f"{column!r} not found in {path}"
                        )

                    requested_indices[column] = (
                        header.index(column)
                    )

                continue

        if header is None:
            continue

        # -------------------------------------------------------------
        # Ignore empty worksheet rows
        # -------------------------------------------------------------

        candidate_index = requested_indices[
            "Cod unic candidat"
        ]

        if candidate_index >= len(values):
            continue

        candidate_code = str(
            values[candidate_index]
        ).strip()

        if not candidate_code:
            continue

        # Candidate rows should not be repeated,
        # but preserve the ODS semantics if they are.
        for _ in range(row_repeat):

            for column, index in (
                requested_indices.items()
            ):

                value = ""

                if index < len(values):
                    value = values[index]

                output[column].append(
                    value
                )

    if header is None:
        raise ValueError(
            f"Header not found in {path}"
        )

    return pd.DataFrame(
        output
    )


# ---------------------------------------------------------------------
# Source readers
# ---------------------------------------------------------------------

def read_2015(path):

    df = pd.read_csv(
        path,
        sep="\t",
        encoding="utf-16",
        dtype=str,
        low_memory=False,
    )

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    return df[
        OLD_COLUMNS
    ].copy()


def read_old_xlsx(path):

    df = pd.read_excel(
        path,
        sheet_name=0,
        usecols=OLD_COLUMNS,
        dtype=str,
    )

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    return df[
        OLD_COLUMNS
    ].copy()


def read_2022(path):

    df = pd.read_excel(
        path,
        sheet_name=0,
        usecols=NEW_COLUMNS,
        dtype=str,
    )

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    return df[
        NEW_COLUMNS
    ].copy()


# ---------------------------------------------------------------------
# Build validated SIIIR prefix -> county mapping from 2022
# ---------------------------------------------------------------------

print("=" * 100)
print("BUILDING COUNTY MAPPING FROM 2022")
print("=" * 100)


source_2022 = read_2022(
    FILES[2022]
)


source_2022["Cod SIIIR"] = (
    normalize_identifier(
        source_2022["Cod SIIIR"]
    )
    .str.zfill(10)
)


source_2022["county_prefix"] = (
    source_2022["Cod SIIIR"]
    .str[:2]
)


mapping_df = (
    source_2022[
        [
            "county_prefix",
            "Judet",
        ]
    ]
    .drop_duplicates()
    .sort_values(
        "county_prefix"
    )
)


if len(mapping_df) != 42:
    raise ValueError(
        "Expected exactly 42 county-prefix mappings."
    )


prefix_conflicts = (
    mapping_df
    .groupby(
        "county_prefix"
    )["Judet"]
    .nunique()
)

prefix_conflicts = prefix_conflicts[
    prefix_conflicts > 1
]


county_conflicts = (
    mapping_df
    .groupby(
        "Judet"
    )["county_prefix"]
    .nunique()
)

county_conflicts = county_conflicts[
    county_conflicts > 1
]


if not prefix_conflicts.empty:
    raise ValueError(
        "Ambiguous prefix-to-county mapping."
    )


if not county_conflicts.empty:
    raise ValueError(
        "Ambiguous county-to-prefix mapping."
    )


PREFIX_TO_COUNTY = dict(
    zip(
        mapping_df["county_prefix"],
        mapping_df["Judet"],
    )
)


print("\nValidated mappings:")
print(len(PREFIX_TO_COUNTY))

print("\nMapping:")
for prefix, county in PREFIX_TO_COUNTY.items():
    print(
        f"{prefix} -> {county}"
    )


# ---------------------------------------------------------------------
# Standardization function
# ---------------------------------------------------------------------

def standardize_year(
    year,
    df,
):

    # -------------------------------------------------------------
    # Rename source-specific columns
    # -------------------------------------------------------------

    if year == 2022:

        df = df.rename(
            columns={
                "Cod": "candidate_code",
                "Cod SIIIR": "siiir_code",
                "Judet": "source_county_abbr",
                "STATUS_FINAL": "status",
                "MEDIA_FINALA": "grade_raw",
            }
        )

    else:

        df = df.rename(
            columns={
                "Cod unic candidat": "candidate_code",
                "Unitate (SIIIR)": "siiir_code",
                "STATUS": "status",
                "Medie": "grade_raw",
            }
        )

    # -------------------------------------------------------------
    # Normalize identifiers
    # -------------------------------------------------------------

    df["candidate_code"] = (
        normalize_identifier(
            df["candidate_code"]
        )
    )

    df["siiir_code"] = (
        normalize_identifier(
            df["siiir_code"]
        )
        .str.zfill(10)
    )

    # -------------------------------------------------------------
    # Geography
    # -------------------------------------------------------------

    df["county_prefix"] = (
        df["siiir_code"]
        .str[:2]
    )

    df["county_abbr"] = (
        df["county_prefix"]
        .map(
            PREFIX_TO_COUNTY
        )
    )

    # -------------------------------------------------------------
    # Status
    # -------------------------------------------------------------

    df["status"] = (
        df["status"]
        .astype("string")
        .str.strip()
    )

    # -------------------------------------------------------------
    # Final grade
    # -------------------------------------------------------------

    df["final_grade"] = (
        normalize_grade(
            df["grade_raw"]
        )
    )

    # -------------------------------------------------------------
    # Analytical flags
    # -------------------------------------------------------------

    df["is_present"] = (
        df["status"]
        .ne("Absent")
        .astype("int8")
    )

    df["is_passed"] = (
        df["status"]
        .eq("Promovat")
        .astype("int8")
    )

    df["is_failed"] = (
        df["status"]
        .eq("Nepromovat")
        .astype("int8")
    )

    df["is_absent"] = (
        df["status"]
        .eq("Absent")
        .astype("int8")
    )

    df["is_eliminated"] = (
        df["status"]
        .eq("Eliminat")
        .astype("int8")
    )

    df["has_valid_grade"] = (
        df["final_grade"]
        .notna()
        .astype("int8")
    )

    df.insert(
        0,
        "year",
        year,
    )

    # -------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------

    rows = len(df)

    if rows != EXPECTED_ROWS[year]:
        raise ValueError(
            f"{year}: expected "
            f"{EXPECTED_ROWS[year]} rows, "
            f"found {rows}."
        )

    if df["candidate_code"].isna().any():
        raise ValueError(
            f"{year}: missing candidate codes."
        )

    if (
        df["candidate_code"]
        .nunique()
        != rows
    ):
        raise ValueError(
            f"{year}: candidate codes are not unique."
        )

    if df["siiir_code"].isna().any():
        raise ValueError(
            f"{year}: missing SIIIR codes."
        )

    invalid_siiir = ~(
        df["siiir_code"]
        .str.fullmatch(
            r"\d{10}",
            na=False,
        )
    )

    if invalid_siiir.any():
        raise ValueError(
            f"{year}: invalid 10-digit SIIIR codes."
        )

    if df["county_abbr"].isna().any():
        raise ValueError(
            f"{year}: unmapped county prefixes."
        )

    statuses = set(
        df["status"]
        .dropna()
        .unique()
    )

    unknown_statuses = (
        statuses
        - ALLOWED_STATUSES
    )

    if unknown_statuses:
        raise ValueError(
            f"{year}: unknown statuses "
            f"{sorted(unknown_statuses)}"
        )

    if df["status"].isna().any():
        raise ValueError(
            f"{year}: missing statuses."
        )

    # 2022 provides county directly,
    # so use it as an additional geography check.
    if year == 2022:

        source_county = (
            df["source_county_abbr"]
            .astype("string")
            .str.strip()
        )

        county_mismatch = (
            source_county
            != df["county_abbr"]
        )

        if county_mismatch.any():
            raise ValueError(
                "2022: derived county does not match "
                "the source Judet column."
            )

    # Every promoted candidate should have a valid grade >= 6.
    promoted_invalid = (
        df["status"].eq("Promovat")
        & (
            df["final_grade"].isna()
            | (df["final_grade"] < 6)
        )
    )

    if promoted_invalid.any():
        raise ValueError(
            f"{year}: invalid grade among promoted candidates."
        )

    # No failed candidate should have a valid average >= 6.
    failed_invalid = (
        df["status"].eq("Nepromovat")
        & df["final_grade"].notna()
        & (df["final_grade"] >= 6)
    )

    if failed_invalid.any():
        raise ValueError(
            f"{year}: Nepromovat candidate with grade >= 6."
        )

    # Absent / eliminated candidates should not have a valid grade.
    administrative_with_grade = (
        df["status"].isin(
            [
                "Absent",
                "Eliminat",
            ]
        )
        & df["final_grade"].notna()
    )

    if administrative_with_grade.any():
        raise ValueError(
            f"{year}: Absent/Eliminat candidate "
            "has a valid final grade."
        )

    # -------------------------------------------------------------
    # Output schema
    # -------------------------------------------------------------

    output_columns = [
        "year",
        "candidate_code",
        "siiir_code",
        "county_prefix",
        "county_abbr",
        "status",
        "final_grade",
        "is_present",
        "is_passed",
        "is_failed",
        "is_absent",
        "is_eliminated",
        "has_valid_grade",
    ]

    result = df[
        output_columns
    ].copy()

    return result


# ---------------------------------------------------------------------
# Process all years
# ---------------------------------------------------------------------

print("\n" + "=" * 100)
print("STANDARDIZING BACCALAUREATE 2015-2023")
print("=" * 100)


INTERIM_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# Remove any previous output so the script is reproducible.
if OUTPUT_PATH.exists():
    OUTPUT_PATH.unlink()


first_write = True
total_rows = 0


for year in range(2015, 2024):

    print("\n" + "-" * 100)
    print(f"YEAR: {year}")
    print("-" * 100)

    path = FILES[year]

    # -------------------------------------------------------------
    # Read source
    # -------------------------------------------------------------

    if year == 2015:

        source = read_2015(
            path
        )

    elif year in {
        2016,
        2017,
    }:

        source = read_ods_selected_columns(
            path,
            OLD_COLUMNS,
        )

    elif year == 2022:

        # Reuse already loaded 2022 source.
        source = source_2022.copy()

    else:

        source = read_old_xlsx(
            path
        )

    # -------------------------------------------------------------
    # Standardize
    # -------------------------------------------------------------

    standardized = standardize_year(
        year,
        source,
    )

    # -------------------------------------------------------------
    # Diagnostics
    # -------------------------------------------------------------

    print("\nRows:")
    print(len(standardized))

    print("\nCounty count:")
    print(
        standardized["county_abbr"]
        .nunique()
    )

    print("\nSTATUS distribution:")
    print(
        standardized["status"]
        .value_counts()
    )

    print("\nValid final grades:")
    print(
        standardized["has_valid_grade"]
        .sum()
    )

    print("\nPresent candidates:")
    print(
        standardized["is_present"]
        .sum()
    )

    print("\nPassed candidates:")
    print(
        standardized["is_passed"]
        .sum()
    )

    # -------------------------------------------------------------
    # Write incrementally
    # -------------------------------------------------------------

    standardized.to_csv(
        OUTPUT_PATH,
        mode="w" if first_write else "a",
        header=first_write,
        index=False,
        encoding="utf-8",
    )

    first_write = False

    total_rows += len(
        standardized
    )


# ---------------------------------------------------------------------
# Final validation
# ---------------------------------------------------------------------

expected_total_rows = sum(
    EXPECTED_ROWS.values()
)


print("\n" + "=" * 100)
print("FINAL STANDARDIZATION SUMMARY")
print("=" * 100)

print("\nOutput:")
print(OUTPUT_PATH)

print("\nTotal standardized rows:")
print(total_rows)

print("\nExpected total rows:")
print(expected_total_rows)

print("\nDifference:")
print(
    total_rows
    - expected_total_rows
)


if total_rows != expected_total_rows:
    raise ValueError(
        "Final row count does not match expected total."
    )


print("\nOutput file size:")
print(
    OUTPUT_PATH.stat().st_size
)


print("\nBaccalaureate candidate-level standardization completed successfully.")