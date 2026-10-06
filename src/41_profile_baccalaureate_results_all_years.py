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


OLD_STATUS_COLUMN = "STATUS"
OLD_GRADE_COLUMN = "Medie"

NEW_STATUS_COLUMN = "STATUS_FINAL"
NEW_GRADE_COLUMN = "MEDIA_FINALA"


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


def extract_ods_row_values(row, max_columns=60):

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

        remaining = (
            max_columns
            - len(values)
        )

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

def read_ods_selected_columns(
    path,
    requested_columns
):

    with zipfile.ZipFile(
        path,
        "r"
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
        NS
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
        NS
    ):

        row_repeat = int(
            row.get(
                f"{{{NS['table']}}}number-rows-repeated",
                "1"
            )
        )

        values = extract_ods_row_values(
            row
        )

        # -------------------------------------------------------------
        # Header
        # -------------------------------------------------------------

        if header is None:

            normalized_values = [
                normalize_column_name(value)
                for value in values
            ]

            if (
                OLD_STATUS_COLUMN
                in normalized_values
                and OLD_GRADE_COLUMN
                in normalized_values
            ):

                header = normalized_values

                requested_indices = {
                    column: header.index(column)
                    for column in requested_columns
                }

                continue

        if header is None:
            continue

        # -------------------------------------------------------------
        # Ignore empty repeated worksheet rows
        # -------------------------------------------------------------

        if not values:
            continue

        # Candidate data exists before STATUS / Medie,
        # so an entirely empty beginning means an empty row.
        if not any(
            str(value).strip()
            for value in values[:10]
        ):
            continue

        # -------------------------------------------------------------
        # Extract requested columns
        # -------------------------------------------------------------

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

    return pd.DataFrame(
        output
    )


# ---------------------------------------------------------------------
# Standard file readers
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
            OLD_STATUS_COLUMN,
            OLD_GRADE_COLUMN,
        ]
    ].copy()


def read_old_xlsx(path):

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
            OLD_STATUS_COLUMN,
            OLD_GRADE_COLUMN,
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
            NEW_STATUS_COLUMN,
            NEW_GRADE_COLUMN,
        ]
    ].copy()


# ---------------------------------------------------------------------
# Grade conversion
# ---------------------------------------------------------------------

def convert_grade_to_numeric(series):

    cleaned = (
        series
        .astype("string")
        .str.strip()
        .str.replace(
            ",",
            ".",
            regex=False
        )
    )

    numeric = pd.to_numeric(
        cleaned,
        errors="coerce"
    )

    return cleaned, numeric


# ---------------------------------------------------------------------
# Profile all years
# ---------------------------------------------------------------------

print("=" * 100)
print("BACCALAUREATE STATUS / GRADE PROFILE 2015-2023")
print("=" * 100)


for year in range(2015, 2024):

    print("\n" + "=" * 100)
    print(f"YEAR: {year}")
    print("=" * 100)

    path = FILES[year]

    # -------------------------------------------------------------
    # Load
    # -------------------------------------------------------------

    if year == 2015:

        df = read_2015(path)

        status_column = OLD_STATUS_COLUMN
        grade_column = OLD_GRADE_COLUMN

    elif year in {2016, 2017}:

        df = read_ods_selected_columns(
            path,
            [
                OLD_STATUS_COLUMN,
                OLD_GRADE_COLUMN,
            ]
        )

        status_column = OLD_STATUS_COLUMN
        grade_column = OLD_GRADE_COLUMN

    elif year == 2022:

        df = read_2022(path)

        status_column = NEW_STATUS_COLUMN
        grade_column = NEW_GRADE_COLUMN

    else:

        df = read_old_xlsx(path)

        status_column = OLD_STATUS_COLUMN
        grade_column = OLD_GRADE_COLUMN

    # -------------------------------------------------------------
    # Normalize status
    # -------------------------------------------------------------

    status = (
        df[status_column]
        .astype("string")
        .str.strip()
    )

    grade_raw, grade_numeric = (
        convert_grade_to_numeric(
            df[grade_column]
        )
    )

    profile = pd.DataFrame(
        {
            "status": status,
            "grade_raw": grade_raw,
            "grade_numeric": grade_numeric,
        }
    )

    # -------------------------------------------------------------
    # Basic information
    # -------------------------------------------------------------

    print("\nRows:")
    print(len(profile))

    print("\nMissing STATUS:")
    print(
        profile["status"]
        .isna()
        .sum()
    )

    print("\nSTATUS distribution:")
    print(
        profile["status"]
        .value_counts(
            dropna=False
        )
    )

    # -------------------------------------------------------------
    # Grade conversion
    # -------------------------------------------------------------

    print("\nMissing raw grade:")
    print(
        profile["grade_raw"]
        .isna()
        .sum()
    )

    print("\nMissing grade after numeric conversion:")
    print(
        profile["grade_numeric"]
        .isna()
        .sum()
    )

    non_numeric_mask = (
        profile["grade_raw"].notna()
        & profile["grade_numeric"].isna()
    )

    print("\nNon-numeric grade values:")
    print(
        profile.loc[
            non_numeric_mask,
            "grade_raw"
        ]
        .value_counts()
        .head(20)
    )

    # -------------------------------------------------------------
    # Negative / special values
    # -------------------------------------------------------------

    negative_mask = (
        profile["grade_numeric"] < 0
    )

    print("\nNegative grade values:")
    print(
        profile.loc[
            negative_mask,
            "grade_numeric"
        ]
        .value_counts()
        .sort_index()
    )

    print("\nSTATUS distribution among negative grades:")
    print(
        profile.loc[
            negative_mask,
            "status"
        ]
        .value_counts(
            dropna=False
        )
    )

    if negative_mask.any():

        print("\nCross-tab STATUS × negative grade:")
        print(
            pd.crosstab(
                profile.loc[
                    negative_mask,
                    "status"
                ],
                profile.loc[
                    negative_mask,
                    "grade_numeric"
                ],
                dropna=False,
            )
        )

    # -------------------------------------------------------------
    # Other grade ranges
    # -------------------------------------------------------------

    print("\nGrade = 0:")
    print(
        (
            profile["grade_numeric"] == 0
        ).sum()
    )

    valid_range_mask = (
        profile["grade_numeric"]
        .between(
            1,
            10,
            inclusive="both"
        )
    )

    print("\nGrades between 1 and 10:")
    print(
        valid_range_mask.sum()
    )

    print("\nGrades > 10:")
    print(
        (
            profile["grade_numeric"] > 10
        ).sum()
    )

    print("\nSTATUS distribution for grades between 1 and 10:")
    print(
        profile.loc[
            valid_range_mask,
            "status"
        ]
        .value_counts(
            dropna=False
        )
    )

    # -------------------------------------------------------------
    # Summary by status
    # -------------------------------------------------------------

    print("\nGrade summary by STATUS:")

    summary = (
        profile
        .groupby(
            "status",
            dropna=False
        )["grade_numeric"]
        .agg(
            count="count",
            min="min",
            max="max",
            mean="mean",
            median="median",
        )
    )

    print(summary)

    # -------------------------------------------------------------
    # Sanity checks around promotion threshold
    # -------------------------------------------------------------

    promoted_mask = (
        profile["status"]
        == "Promovat"
    )

    failed_mask = (
        profile["status"]
        == "Nepromovat"
    )

    print("\nPromovat count:")
    print(
        promoted_mask.sum()
    )

    print("\nPromovat with grade < 6:")
    print(
        (
            promoted_mask
            & (
                profile["grade_numeric"]
                < 6
            )
        ).sum()
    )

    print("\nPromovat with grade >= 6:")
    print(
        (
            promoted_mask
            & (
                profile["grade_numeric"]
                >= 6
            )
        ).sum()
    )

    print("\nNepromovat count:")
    print(
        failed_mask.sum()
    )

    print("\nNepromovat with grade >= 6:")
    print(
        (
            failed_mask
            & (
                profile["grade_numeric"]
                >= 6
            )
        ).sum()
    )


print("\n" + "=" * 100)
print("ALL-YEAR STATUS / GRADE PROFILE COMPLETED")
print("=" * 100)