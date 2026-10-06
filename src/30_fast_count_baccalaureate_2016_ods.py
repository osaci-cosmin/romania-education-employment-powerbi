import zipfile  # Imports tools for reading the internal structure of ODS files
import xml.etree.ElementTree as ET  # Imports streaming XML parsing tools
from pathlib import Path  # Imports tools for working safely with file paths


# --------------------------------------------------
# 1. Define the existing ODS source file
# --------------------------------------------------

ods_file = Path(
    "data/raw/baccalaureate/"
    "baccalaureate_2016_session1_raw.ods"
)


# --------------------------------------------------
# 2. Define ODF XML namespaces
# --------------------------------------------------

TABLE_NS = (
    "urn:oasis:names:tc:opendocument:"
    "xmlns:table:1.0"
)

OFFICE_NS = (
    "urn:oasis:names:tc:opendocument:"
    "xmlns:office:1.0"
)


TABLE_TAG = f"{{{TABLE_NS}}}table"
ROW_TAG = f"{{{TABLE_NS}}}table-row"
CELL_TAG = f"{{{TABLE_NS}}}table-cell"
COVERED_CELL_TAG = f"{{{TABLE_NS}}}covered-table-cell"

TABLE_NAME_ATTR = f"{{{TABLE_NS}}}name"
ROW_REPEAT_ATTR = f"{{{TABLE_NS}}}number-rows-repeated"

OFFICE_VALUE_ATTR = f"{{{OFFICE_NS}}}value"
OFFICE_STRING_VALUE_ATTR = f"{{{OFFICE_NS}}}string-value"


# --------------------------------------------------
# 3. Helper function for extracting cell content
# --------------------------------------------------

def get_cell_value(cell):
    """
    Extracts a readable value from an ODS table cell.
    """

    string_value = cell.get(
        OFFICE_STRING_VALUE_ATTR
    )

    if string_value is not None:
        return string_value.strip()

    numeric_value = cell.get(
        OFFICE_VALUE_ATTR
    )

    if numeric_value is not None:
        return numeric_value.strip()

    text_content = "".join(
        cell.itertext()
    ).strip()

    return text_content


# --------------------------------------------------
# 4. Stream content.xml directly from the ODS archive
# --------------------------------------------------

print("Reading ODS directly from internal XML...")
print("File:", ods_file)
print(
    "File size:",
    f"{ods_file.stat().st_size:,}",
    "bytes"
)


target_sheet = "Export_Worksheet"

inside_target_sheet = False

physical_rows = 0
expanded_rows = 0

candidate_rows = 0
unique_candidate_codes = set()

header_found = False


with zipfile.ZipFile(
    ods_file,
    "r"
) as ods_archive:

    with ods_archive.open(
        "content.xml"
    ) as xml_file:

        context = ET.iterparse(
            xml_file,
            events=("start", "end")
        )

        for event, element in context:

            # --------------------------------------------------
            # Detect the target worksheet
            # --------------------------------------------------

            if (
                event == "start"
                and element.tag == TABLE_TAG
            ):

                sheet_name = element.get(
                    TABLE_NAME_ATTR
                )

                inside_target_sheet = (
                    sheet_name == target_sheet
                )

                if inside_target_sheet:
                    print(
                        "\nTarget sheet found:",
                        sheet_name
                    )

            # --------------------------------------------------
            # Process rows from the target worksheet
            # --------------------------------------------------

            elif (
                event == "end"
                and element.tag == ROW_TAG
                and inside_target_sheet
            ):

                physical_rows += 1

                row_repeat = int(
                    element.get(
                        ROW_REPEAT_ATTR,
                        "1"
                    )
                )

                expanded_rows += row_repeat

                cells = [
                    child
                    for child in element
                    if child.tag in (
                        CELL_TAG,
                        COVERED_CELL_TAG
                    )
                ]

                if cells:

                    first_cell = cells[0]

                    first_value = get_cell_value(
                        first_cell
                    )

                    # --------------------------------------------------
                    # Detect the header
                    # --------------------------------------------------

                    if (
                        first_value.strip()
                        == "Cod unic candidat"
                    ):

                        header_found = True

                        print(
                            "Header detected successfully."
                        )

                    # --------------------------------------------------
                    # Count candidate rows
                    # --------------------------------------------------

                    elif (
                        header_found
                        and first_value != ""
                    ):

                        candidate_rows += row_repeat

                        unique_candidate_codes.add(
                            first_value
                        )

                element.clear()

            # --------------------------------------------------
            # Detect the end of the target worksheet
            # --------------------------------------------------

            elif (
                event == "end"
                and element.tag == TABLE_TAG
                and inside_target_sheet
            ):

                break


# --------------------------------------------------
# 5. Display results
# --------------------------------------------------

print("\n" + "=" * 80)

print("2016 ODS FAST VALIDATION")

print("\nPhysical XML rows:")
print(physical_rows)

print("\nExpanded worksheet rows:")
print(expanded_rows)

print("\nCandidate rows:")
print(candidate_rows)

print("\nUnique candidate codes:")
print(
    len(unique_candidate_codes)
)

print("\nHeader found:")
print(header_found)


# --------------------------------------------------
# 6. Basic validation
# --------------------------------------------------

if not header_found:
    raise ValueError(
        "Expected Baccalaureate header was not found."
    )

if candidate_rows == 0:
    raise ValueError(
        "No candidate rows were detected."
    )


print(
    "\n2016 ODS fast validation completed successfully."
)