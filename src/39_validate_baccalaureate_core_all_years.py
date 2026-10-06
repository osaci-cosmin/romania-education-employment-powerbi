from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

RAW_DIR = Path("data/raw/baccalaureate")

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


OLD_CANDIDATE_COLUMN = "Cod unic candidat"
OLD_SIIIR_COLUMN = "Unitate (SIIIR)"

NEW_CANDIDATE_COLUMN = "Cod"
NEW_SIIIR_COLUMN = "Cod SIIIR"
NEW_COUNTY_COLUMN = "Judet"


# ---------------------------------------------------------------------
# ODS namespaces
# ---------------------------------------------------------------------

NS = {
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def normalize_column_name(value):
    return (
        str(value)
        .replace("\ufeff", "")
        .strip()
    )


def get_cell_text(cell):
    paragraphs = []

    for paragraph in cell.findall(".//text:p", NS):
        value = "".join(paragraph.itertext()).strip()

        if value:
            paragraphs.append(value)

    if paragraphs:
        return " ".join(paragraphs)

    value = cell.get(
        f"{{{NS['office']}}}value"
    )

    if value is not None:
        return value

    string_value = cell.get(
        f"{{{NS['office']}}}string-value"
    )

    if string_value is not None:
        return string_value

    return ""


def extract_ods_row_values(row, max_columns):
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
                "1"
            )
        )

        value = get_cell_text(cell)

        remaining = max_columns - len(values)

        if remaining <= 0:
            break

        repeat_to_use = min(
            repeat,
            remaining
        )

        values.extend(
            [value] * repeat_to_use
        )

    return values


# ---------------------------------------------------------------------
# ODS selective reader
# ---------------------------------------------------------------------

def read_ods_selected_columns(path, requested_columns):

    with zipfile.ZipFile(path, "r") as archive:
        with archive.open("content.xml") as xml_file:
            tree = ET.parse(xml_file)

    root = tree.getroot()

    tables = root.findall(
        ".//table:table",
        NS
    )

    if not tables:
        raise ValueError(
            f"No worksheets found in {path}"
        )

    # Prefer Export_Worksheet
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
        NS
    ):

        row_repeat = int(
            row.get(
                f"{{{NS['table']}}}number-rows-repeated",
                "1"
            )
        )

        values = extract_ods_row_values(
            row,
            max_columns=60
        )

        # -------------------------------------------------------------
        # Find header
        # -------------------------------------------------------------

        if header is None:

            normalized_values = [
                normalize_column_name(v)
                for v in values
            ]

            if OLD_CANDIDATE_COLUMN in normalized_values:

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
        # Candidate rows
        # -------------------------------------------------------------

        candidate_index = requested_indices[
            OLD_CANDIDATE_COLUMN
        ]

        if candidate_index >= len(values):
            continue

        candidate_code = str(
            values[candidate_index]
        ).strip()

        # Ignore empty repeated worksheet rows
        if not candidate_code:
            continue

        for _ in range(row_repeat):

            for column, index in requested_indices.items():

                value = ""

                if index < len(values):
                    value = values[index]

                output[column].append(value)

    if header is None:
        raise ValueError(
            f"Header not found in {path}"
        )

    return pd.DataFrame(output)


# ---------------------------------------------------------------------
# CSV / XLSX selective readers
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
        [
            OLD_CANDIDATE_COLUMN,
            OLD_SIIIR_COLUMN,
        ]
    ].copy()


def read_xlsx_old_schema(path):

    df = pd.read_excel(
        path,
        sheet_name=0,
        dtype=str,
    )

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    return df[
        [
            OLD_CANDIDATE_COLUMN,
            OLD_SIIIR_COLUMN,
        ]
    ].copy()


def read_2022(path):

    df = pd.read_excel(
        path,
        sheet_name=0,
        dtype=str,
    )

    df.columns = [
        normalize_column_name(column)
        for column in df.columns
    ]

    return df[
        [
            NEW_CANDIDATE_COLUMN,
            NEW_SIIIR_COLUMN,
            NEW_COUNTY_COLUMN,
        ]
    ].copy()


# ---------------------------------------------------------------------
# Normalize identifiers
# ---------------------------------------------------------------------

def normalize_identifier(series):
    return (
        series
        .astype("string")
        .str.strip()
        .str.replace(
            r"\.0$",
            "",
            regex=True
        )
    )


# ---------------------------------------------------------------------
# Build validated county-prefix mapping from 2022
# ---------------------------------------------------------------------

print("=" * 100)
print("BUILDING COUNTY PREFIX MAPPING FROM 2022")
print("=" * 100)


df_2022 = read_2022(
    FILES[2022]
)

df_2022[NEW_SIIIR_COLUMN] = normalize_identifier(
    df_2022[NEW_SIIIR_COLUMN]
)

df_2022["county_prefix"] = (
    df_2022[NEW_SIIIR_COLUMN]
    .str[:2]
)


mapping_df = (
    df_2022[
        [
            "county_prefix",
            NEW_COUNTY_COLUMN,
        ]
    ]
    .dropna()
    .drop_duplicates()
)


prefix_conflicts = (
    mapping_df
    .groupby("county_prefix")[NEW_COUNTY_COLUMN]
    .nunique()
)

prefix_conflicts = prefix_conflicts[
    prefix_conflicts > 1
]


county_conflicts = (
    mapping_df
    .groupby(NEW_COUNTY_COLUMN)["county_prefix"]
    .nunique()
)

county_conflicts = county_conflicts[
    county_conflicts > 1
]


print("\nMapping rows:")
print(len(mapping_df))

print("\nUnique prefixes:")
print(mapping_df["county_prefix"].nunique())

print("\nUnique counties:")
print(mapping_df[NEW_COUNTY_COLUMN].nunique())

print("\nPrefix conflicts:")
print(prefix_conflicts)

print("\nCounty conflicts:")
print(county_conflicts)


if not prefix_conflicts.empty:
    raise ValueError(
        "2022 prefix-to-county mapping is ambiguous."
    )

if not county_conflicts.empty:
    raise ValueError(
        "2022 county-to-prefix mapping is ambiguous."
    )


VALID_PREFIXES = set(
    mapping_df["county_prefix"]
)


print("\nValidated county prefixes:")
print(sorted(VALID_PREFIXES))


# ---------------------------------------------------------------------
# Validate all years
# ---------------------------------------------------------------------

print("\n" + "=" * 100)
print("VALIDATING ALL BACCALAUREATE YEARS")
print("=" * 100)


for year in range(2015, 2024):

    print("\n" + "-" * 100)
    print(f"YEAR: {year}")
    print("-" * 100)

    path = FILES[year]

    # -------------------------------------------------------------
    # Load
    # -------------------------------------------------------------

    if year == 2015:

        df = read_2015(path)

        candidate_column = OLD_CANDIDATE_COLUMN
        siiir_column = OLD_SIIIR_COLUMN

    elif year in {2016, 2017}:

        df = read_ods_selected_columns(
            path,
            [
                OLD_CANDIDATE_COLUMN,
                OLD_SIIIR_COLUMN,
            ]
        )

        candidate_column = OLD_CANDIDATE_COLUMN
        siiir_column = OLD_SIIIR_COLUMN

    elif year == 2022:

        df = df_2022.copy()

        candidate_column = NEW_CANDIDATE_COLUMN
        siiir_column = NEW_SIIIR_COLUMN

    else:

        df = read_xlsx_old_schema(path)

        candidate_column = OLD_CANDIDATE_COLUMN
        siiir_column = OLD_SIIIR_COLUMN

    # -------------------------------------------------------------
    # Normalize
    # -------------------------------------------------------------

    df[candidate_column] = normalize_identifier(
        df[candidate_column]
    )

    df[siiir_column] = normalize_identifier(
        df[siiir_column]
    )

    # -------------------------------------------------------------
    # Candidate validation
    # -------------------------------------------------------------

    rows = len(df)

    non_null_candidates = (
        df[candidate_column]
        .notna()
        .sum()
    )

    unique_candidates = (
        df[candidate_column]
        .nunique(
            dropna=True
        )
    )

    duplicate_candidate_rows = (
        df[candidate_column]
        .duplicated(
            keep=False
        )
        .sum()
    )

    # -------------------------------------------------------------
    # SIIIR validation
    # -------------------------------------------------------------

    siiir_non_null = (
        df[siiir_column]
        .notna()
        .sum()
    )

    digit_mask = (
        df[siiir_column]
        .str.fullmatch(
            r"\d+",
            na=False
        )
    )

    ten_digit_mask = (
        df[siiir_column]
        .str.fullmatch(
            r"\d{10}",
            na=False
        )
    )

    prefixes = (
        df.loc[
            ten_digit_mask,
            siiir_column
        ]
        .str[:2]
    )

    unique_prefixes = set(
        prefixes.dropna()
    )

    unknown_prefixes = (
        unique_prefixes
        - VALID_PREFIXES
    )

    missing_expected_prefixes = (
        VALID_PREFIXES
        - unique_prefixes
    )

    # -------------------------------------------------------------
    # Output
    # -------------------------------------------------------------

    print("\nRows:")
    print(rows)

    print("\nExpected rows:")
    print(EXPECTED_ROWS[year])

    print("\nRow difference:")
    print(
        rows
        - EXPECTED_ROWS[year]
    )

    print("\nNon-null candidate codes:")
    print(non_null_candidates)

    print("\nUnique candidate codes:")
    print(unique_candidates)

    print("\nDuplicate candidate rows:")
    print(duplicate_candidate_rows)

    print("\nNon-null SIIIR codes:")
    print(siiir_non_null)

    print("\nDigit-only SIIIR codes:")
    print(digit_mask.sum())

    print("\n10-digit SIIIR codes:")
    print(ten_digit_mask.sum())

    print("\nUnique county prefixes:")
    print(len(unique_prefixes))

    print("\nUnknown county prefixes:")
    print(sorted(unknown_prefixes))

    print("\nExpected prefixes missing in this year:")
    print(sorted(missing_expected_prefixes))


print("\n" + "=" * 100)
print("ALL-YEAR CORE VALIDATION COMPLETED")
print("=" * 100)