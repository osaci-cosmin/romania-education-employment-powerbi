# Development Log

This document records the main development steps, technical decisions, validation procedures, methodological choices, and data pipeline architecture of the project in both English and Romanian.

Acest document înregistrează principalele etape de dezvoltare, deciziile tehnice, procedurile de validare, alegerile metodologice și arhitectura pipeline-ului de date al proiectului, atât în limba engleză, cât și în limba română.

---

# Employment Pipeline

## Step 1 — Create the project source code structure

### English

A dedicated `src/` directory was created to store the Python scripts used for data ingestion, transformation, cleaning, profiling, and validation.

Keeping source code separate from raw data, processed data, documentation, and Power BI files makes the project easier to maintain, understand, reproduce, and extend.

The project initially followed this structure:

```text
romania_education_employment/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── development_log.md
├── powerbi/
└── src/
    ├── 01_test_tempo_api.py
    ├── 02_test_eurostat_api.py
    ├── 03_ingest_employment.py
    └── 04_transform_employment.py
```

### Română

A fost creat un folder separat `src/` pentru scripturile Python utilizate pentru ingestia, transformarea, curățarea, profilarea și validarea datelor.

Separarea codului de datele raw, datele procesate, documentație și fișierele Power BI face proiectul mai ușor de întreținut, înțeles, reprodus și extins.

Structura inițială a proiectului a fost:

```text
romania_education_employment/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── development_log.md
├── powerbi/
└── src/
    ├── 01_test_tempo_api.py
    ├── 02_test_eurostat_api.py
    ├── 03_ingest_employment.py
    └── 04_transform_employment.py
```

---

## Step 2 — Test INS TEMPO programmatic access

### English

The initial plan was to retrieve employment data from the Romanian National Institute of Statistics through INS TEMPO.

A Python script named:

```text
01_test_tempo_api.py
```

was created to test whether the TEMPO data source could be accessed programmatically.

The `requests` library was used to send an HTTP GET request.

```python
import requests

url = "http://statistici.insse.ro:8077/tempo-ins/context/"

try:
    response = requests.get(url, timeout=30)

    print("Status code:", response.status_code)
    print(response.text[:1000])

except requests.exceptions.RequestException as error:
    print("Connection error:", error)
```

The `try` / `except` structure was introduced to handle network-related failures without terminating the script unexpectedly.

During development, the TEMPO endpoint repeatedly closed the connection and returned a `ConnectionResetError`.

Because the endpoint could not be accessed reliably from the development environment, the project moved to Eurostat as an alternative official public statistical source for the employment component.

The INS TEMPO test script was preserved to document the original source investigation and error-handling process.

### Română

Planul inițial a fost extragerea datelor despre salariați din baza Institutului Național de Statistică prin INS TEMPO.

A fost creat un script Python numit:

```text
01_test_tempo_api.py
```

pentru a verifica dacă sursa TEMPO poate fi accesată programatic.

Biblioteca `requests` a fost utilizată pentru trimiterea unei cereri HTTP de tip GET.

```python
import requests

url = "http://statistici.insse.ro:8077/tempo-ins/context/"

try:
    response = requests.get(url, timeout=30)

    print("Status code:", response.status_code)
    print(response.text[:1000])

except requests.exceptions.RequestException as error:
    print("Connection error:", error)
```

Structura `try` / `except` a fost introdusă pentru gestionarea controlată a erorilor de rețea.

În timpul dezvoltării, endpoint-ul TEMPO a închis în mod repetat conexiunea și a returnat o eroare de tip `ConnectionResetError`.

Deoarece endpoint-ul nu a putut fi accesat stabil din mediul de dezvoltare, pentru componenta Employment proiectul a trecut la Eurostat ca sursă statistică oficială alternativă.

Scriptul INS TEMPO a fost păstrat pentru documentarea investigației inițiale și a modului de gestionare a erorilor.

---

## Step 3 — Test the Eurostat API connection

### English

A second test script was created:

```text
02_test_eurostat_api.py
```

The Eurostat dataset selected for the employment component was:

```text
nama_10r_3empers
```

The dataset represents employment in thousand persons at regional level.

The first API request was intentionally small in order to verify connectivity and understand the returned JSON structure.

The request selected:

```text
Frequency: Annual
Unit: Thousand persons
Employment status: Employees
Economic activity: Total
Country: Romania
Year: 2023
```

The API returned:

```text
Status code: 200
```

confirming that the connection was successful.

The JSON response was converted into a Python dictionary using:

```python
data = response.json()
```

### Română

A fost creat un al doilea script de test:

```text
02_test_eurostat_api.py
```

Datasetul Eurostat selectat pentru componenta Employment a fost:

```text
nama_10r_3empers
```

Datasetul reprezintă employment în mii de persoane la nivel regional.

Prima cerere API a fost intenționat restrânsă pentru a verifica funcționarea conexiunii și pentru a înțelege structura JSON returnată.

Cererea a selectat:

```text
Frecvență: Anual
Unitate: Mii de persoane
Statut: Employees
Activitate economică: Total
Țară: România
An: 2023
```

API-ul a returnat:

```text
Status code: 200
```

confirmând că legătura funcționează.

Răspunsul JSON a fost convertit într-un dictionary Python folosind:

```python
data = response.json()
```

---

## Step 4 — Identify Romanian NUTS 3 regions

### English

The geographical metadata returned by Eurostat contains multiple territorial levels.

The Romanian NUTS 3 units required for the project were isolated programmatically using:

```python
geo_code.startswith("RO") and len(geo_code) == 5
```

The validation returned:

```text
Number of Romanian NUTS 3 regions: 42
```

These geographical units correspond to:

```text
41 counties + Bucharest
```

Examples include:

```text
RO111 - Bihor
RO113 - Cluj
RO321 - Bucureşti
RO423 - Hunedoara
RO424 - Timiş
```

This filtering prevents national, macro-regional, and NUTS 2 aggregates from being mixed with county-level observations.

### Română

Metadata geografică returnată de Eurostat conține mai multe niveluri teritoriale.

Unitățile NUTS 3 din România necesare proiectului au fost izolate programatic folosind:

```python
geo_code.startswith("RO") and len(geo_code) == 5
```

Validarea a returnat:

```text
Number of Romanian NUTS 3 regions: 42
```

Aceste unități geografice corespund structurii:

```text
41 județe + București
```

Exemple:

```text
RO111 - Bihor
RO113 - Cluj
RO321 - Bucureşti
RO423 - Hunedoara
RO424 - Timiş
```

Această filtrare previne amestecarea observațiilor județene cu totalul național, macroregiunile sau regiunile NUTS 2.

---

## Step 5 — Define the employment extraction period

### English

The target period for the Employment dataset was defined as:

```text
2014–2023
```

The Eurostat API request used:

```python
"sinceTimePeriod": "2014",
"untilTimePeriod": "2023"
```

The returned data confirmed:

```text
Romanian NUTS 3 regions: 42
Years: 2014–2023
Unique years: 10
```

The JSON-stat dimensions were:

```text
['freq', 'unit', 'wstatus', 'nace_r2', 'geo', 'time']
```

with dimension sizes:

```text
[1, 1, 1, 1, 1220, 10]
```

Only the 42 Romanian NUTS 3 units were retained during transformation.

### Română

Perioada țintă pentru datasetul Employment a fost definită astfel:

```text
2014–2023
```

Cererea Eurostat API a utilizat:

```python
"sinceTimePeriod": "2014",
"untilTimePeriod": "2023"
```

Datele returnate au confirmat:

```text
Romanian NUTS 3 regions: 42
Years: 2014–2023
Unique years: 10
```

Dimensiunile JSON-stat au fost:

```text
['freq', 'unit', 'wstatus', 'nace_r2', 'geo', 'time']
```

cu dimensiunile:

```text
[1, 1, 1, 1, 1220, 10]
```

În etapa de transformare au fost păstrate doar cele 42 de unități NUTS 3 din România.

---

## Step 6 — Validate JSON-stat indexing

### English

Before transforming the complete dataset, the JSON-stat indexing logic was tested using:

```text
RO423 - Hunedoara
```

The API stores observations in a flattened JSON-stat structure.

The observation position was calculated using:

```python
flat_index = county_position * number_of_years + year_position
```

The test returned one observation for each year between 2014 and 2023:

```text
RO423 2014 134.65
RO423 2015 140.73
RO423 2016 137.88
RO423 2017 134.12
RO423 2018 134.42
RO423 2019 132.68
RO423 2020 132.21
RO423 2021 127.92
RO423 2022 126.42
RO423 2023 117.04
```

This confirmed that geographical and temporal positions were being interpreted correctly.

### Română

Înainte de transformarea întregului dataset, logica de indexare JSON-stat a fost testată folosind:

```text
RO423 - Hunedoara
```

API-ul stochează observațiile într-o structură JSON-stat aplatizată.

Poziția unei observații a fost calculată folosind:

```python
flat_index = county_position * number_of_years + year_position
```

Testul a returnat câte o observație pentru fiecare an din perioada 2014–2023:

```text
RO423 2014 134.65
RO423 2015 140.73
RO423 2016 137.88
RO423 2017 134.12
RO423 2018 134.42
RO423 2019 132.68
RO423 2020 132.21
RO423 2021 127.92
RO423 2022 126.42
RO423 2023 117.04
```

Testul a confirmat că pozițiile geografice și temporale sunt interpretate corect.

---

## Step 7 — Ingest and preserve the raw Eurostat response

### English

A dedicated ingestion script was created:

```text
03_ingest_employment.py
```

Its responsibility is to retrieve the selected Eurostat dataset and preserve the original API response before any transformation.

The raw response was saved as:

```text
data/raw/eurostat_employment_2014_2023_raw.json
```

The raw dataset is preserved unchanged.

The pipeline therefore separates:

```text
Source API
    ↓
Raw data
    ↓
Transformation
```

The script also uses:

```python
response.raise_for_status()
```

to stop execution when the server returns an HTTP error.

### Română

A fost creat un script separat pentru ingestie:

```text
03_ingest_employment.py
```

Responsabilitatea acestuia este să preia datasetul Eurostat și să păstreze răspunsul original înainte de aplicarea transformărilor.

Răspunsul raw a fost salvat în:

```text
data/raw/eurostat_employment_2014_2023_raw.json
```

Datasetul raw este păstrat nemodificat.

Pipeline-ul separă astfel:

```text
API sursă
    ↓
Date raw
    ↓
Transformare
```

Scriptul utilizează și:

```python
response.raise_for_status()
```

pentru oprirea execuției atunci când serverul returnează o eroare HTTP.

---

## Step 8 — Transform JSON-stat into tabular data

### English

A dedicated transformation script was created:

```text
04_transform_employment.py
```

The script reads the previously saved raw JSON instead of requesting the API again.

The analytical grain was defined as:

```text
County × Year
```

The transformation loops through:

```text
42 counties × 10 years
```

creating:

```text
420 observations
```

Each observation initially contains:

```text
county_code
county
year
employees_thousands
```

Example:

```text
RO111, Bihor, 2014, 215.78
```

The records were converted into a pandas DataFrame using:

```python
df = pd.DataFrame(records)
```

### Română

A fost creat un script separat pentru transformare:

```text
04_transform_employment.py
```

Scriptul citește JSON-ul raw salvat anterior, fără să interogheze din nou API-ul.

Granularitatea analitică a fost definită astfel:

```text
Județ × An
```

Transformarea parcurge:

```text
42 județe × 10 ani
```

și creează:

```text
420 observații
```

Fiecare observație conține inițial:

```text
county_code
county
year
employees_thousands
```

Exemplu:

```text
RO111, Bihor, 2014, 215.78
```

Observațiile au fost transformate într-un pandas DataFrame folosind:

```python
df = pd.DataFrame(records)
```

---

## Step 9 — Validate employment data quality

### English

The transformed DataFrame was validated before export.

Results:

```text
Shape: 420 × 4
Missing values: 0
Duplicate County × Year combinations: 0
Unique counties: 42
Unique years: 10
Year range: 2014–2023
```

The expected grain was confirmed:

```text
1 row = 1 county × 1 year
```

Automated validation rules were added using Python `assert` statements.

Examples:

```python
assert len(df) == 420

assert df["county_code"].nunique() == 42

assert df["year"].nunique() == 10

assert df.duplicated(
    subset=["county_code", "year"]
).sum() == 0

assert df["employees_thousands"].isna().sum() == 0
```

The validation finished with:

```text
All data quality checks passed successfully.
```

### Română

DataFrame-ul rezultat a fost validat înainte de export.

Rezultatele:

```text
Shape: 420 × 4
Valori lipsă: 0
Duplicate Județ × An: 0
Județe unice: 42
Ani unici: 10
Perioadă: 2014–2023
```

Granularitatea așteptată a fost confirmată:

```text
1 rând = 1 județ × 1 an
```

Au fost introduse reguli automate de validare prin Python `assert`.

Exemple:

```python
assert len(df) == 420

assert df["county_code"].nunique() == 42

assert df["year"].nunique() == 10

assert df.duplicated(
    subset=["county_code", "year"]
).sum() == 0

assert df["employees_thousands"].isna().sum() == 0
```

Validarea s-a încheiat cu:

```text
All data quality checks passed successfully.
```

---

## Step 10 — Create the processed employment dataset

### English

Eurostat returns the indicator in:

```text
THS = thousand persons
```

The original value was preserved as:

```text
employees_thousands
```

A second field was created for easier interpretation:

```text
employees
```

using:

```python
df["employees"] = (
    df["employees_thousands"] * 1000
).round().astype("int64")
```

Example:

```text
215.78 thousand persons
→
215,780 persons
```

The validated dataset was exported to:

```text
data/processed/employment_clean.csv
```

The final columns are:

```text
county_code
county
year
employees_thousands
employees
```

### Română

Eurostat returnează indicatorul în:

```text
THS = mii de persoane
```

Valoarea originală a fost păstrată în:

```text
employees_thousands
```

A fost creat și un câmp mai ușor de interpretat:

```text
employees
```

folosind:

```python
df["employees"] = (
    df["employees_thousands"] * 1000
).round().astype("int64")
```

Exemplu:

```text
215.78 mii persoane
→
215.780 persoane
```

Datasetul validat a fost exportat în:

```text
data/processed/employment_clean.csv
```

Coloanele finale sunt:

```text
county_code
county
year
employees_thousands
employees
```

---

# Employment Pipeline Status

## English

The Employment pipeline is operational.

```text
Eurostat API
      ↓
Raw JSON
      ↓
Python transformation
      ↓
JSON-stat parsing
      ↓
Geographical filtering
      ↓
Data quality validation
      ↓
Processed CSV
      ↓
Power BI
```

Current output:

```text
Source dataset: nama_10r_3empers
Geographical level: Romanian NUTS 3
Period: 2014–2023
Geographical units: 42
Years: 10
Observations: 420
Missing values: 0
Duplicate County × Year keys: 0
Processed file: data/processed/employment_clean.csv
```

## Română

Pipeline-ul Employment este funcțional.

```text
Eurostat API
      ↓
JSON raw
      ↓
Transformare Python
      ↓
Parsare JSON-stat
      ↓
Filtrare geografică
      ↓
Validarea calității
      ↓
CSV procesat
      ↓
Power BI
```

Situația actuală:

```text
Dataset sursă: nama_10r_3empers
Nivel geografic: NUTS 3 România
Perioadă: 2014–2023
Unități geografice: 42
Ani: 10
Observații: 420
Valori lipsă: 0
Duplicate Județ × An: 0
Fișier procesat: data/processed/employment_clean.csv
```

---

# Enrollment Pipeline

## Step 11 — Identify the official enrollment data source

### English

The next component focused on student enrollment.

The Romanian national open-data portal was selected as the source:

```text
data.gov.ro
```

The portal uses CKAN and provides an API that can be queried programmatically.

A script was created:

```text
05_test_datagov_enrollment.py
```

The CKAN endpoint used for dataset discovery was:

```text
https://data.gov.ro/api/3/action/package_search
```

The search query was:

```text
Elevi înmatriculați
```

The API returned:

```text
Status code: 200
API success: True
Datasets found: 11
```

Datasets were identified for school years from:

```text
2015-2016
to
2025-2026
```

A specific search for:

```text
2014-2015
```

did not identify an exact dataset belonging to the same enrollment series.

The analytical pipeline therefore begins with:

```text
2015-2016
```

### Română

Următoarea componentă a proiectului a fost reprezentată de elevii înmatriculați.

Portalul național de date deschise a fost selectat ca sursă:

```text
data.gov.ro
```

Portalul utilizează CKAN și pune la dispoziție un API care poate fi interogat programatic.

A fost creat scriptul:

```text
05_test_datagov_enrollment.py
```

Endpoint-ul CKAN utilizat pentru identificarea dataseturilor a fost:

```text
https://data.gov.ro/api/3/action/package_search
```

Căutarea a utilizat:

```text
Elevi înmatriculați
```

API-ul a returnat:

```text
Status code: 200
API success: True
Datasets found: 11
```

Au fost identificate dataseturi pentru anii școlari:

```text
2015-2016
până la
2025-2026
```

O căutare separată pentru:

```text
2014-2015
```

nu a identificat un dataset exact din aceeași serie.

Pipeline-ul analitic începe astfel cu:

```text
2015-2016
```

---

## Step 12 — Inspect enrollment dataset resources

### English

The 2015-2016 dataset was inspected through CKAN metadata before download.

The dataset contained one resource:

```text
Dataset title:
Elevi înmatriculați anul școlar 2015-2016

Dataset name:
elevi-2015-2016

Resources:
1
```

The resource metadata reported:

```text
Format: XLS
```

while the downloadable file itself used:

```text
.xlsx
```

The original resource was preserved without manual modification.

### Română

Datasetul 2015-2016 a fost inspectat prin metadata CKAN înainte de descărcare.

Datasetul conținea o singură resursă:

```text
Dataset title:
Elevi înmatriculați anul școlar 2015-2016

Dataset name:
elevi-2015-2016

Resources:
1
```

Metadata indica:

```text
Format: XLS
```

în timp ce fișierul descărcabil utiliza:

```text
.xlsx
```

Resursa originală a fost păstrată fără modificări manuale.

---

## Step 13 — Ingest the first raw enrollment file

### English

A dedicated ingestion script was created:

```text
06_ingest_enrollment.py
```

The source file was downloaded and stored as:

```text
data/raw/enrollment/enrollment_2015_2016_raw.xlsx
```

The file was written in binary mode:

```python
with open(output_file, "wb") as file:
    file.write(response.content)
```

This preserves the downloaded Excel file exactly as received.

The file size was approximately:

```text
15.7 MB
```

### Română

A fost creat un script separat pentru ingestie:

```text
06_ingest_enrollment.py
```

Fișierul sursă a fost descărcat și salvat în:

```text
data/raw/enrollment/enrollment_2015_2016_raw.xlsx
```

Fișierul a fost scris în mod binar:

```python
with open(output_file, "wb") as file:
    file.write(response.content)
```

Astfel este păstrat exact fișierul Excel primit de la sursă.

Dimensiunea fișierului a fost de aproximativ:

```text
15.7 MB
```

---

## Step 14 — Inspect the raw enrollment workbook

### English

A workbook-inspection script was created:

```text
07_inspect_enrollment.py
```

The 2015-2016 workbook contained one worksheet:

```text
2015_2016
```

The first row was confirmed to contain the actual table headers.

The dataset contained 40 columns, including:

```text
Judet
Cod unitate PJ
Denumire unitate PJ
Localitate
Mediu
Nivel
Tip invatamant
Forma de invatamant
Tipul formatiunii de studiu
Limba predare
Filiera
Profil
Specializare/Calificare
Numarul claselor existente
Numarul elevilor existenti
```

The raw grain was significantly more detailed than the grain required by the Power BI analysis.

### Română

A fost creat scriptul:

```text
07_inspect_enrollment.py
```

Workbook-ul 2015-2016 conținea un singur worksheet:

```text
2015_2016
```

Primul rând a fost confirmat ca fiind header-ul real.

Datasetul conținea 40 de coloane, printre care:

```text
Judet
Cod unitate PJ
Denumire unitate PJ
Localitate
Mediu
Nivel
Tip invatamant
Forma de invatamant
Tipul formatiunii de studiu
Limba predare
Filiera
Profil
Specializare/Calificare
Numarul claselor existente
Numarul elevilor existenti
```

Grain-ul raw era mult mai detaliat decât grain-ul necesar analizei Power BI.

---

## Step 15 — Profile the first enrollment dataset

### English

A profiling script was created:

```text
08_profile_enrollment.py
```

The 2015-2016 source contained:

```text
167,907 rows
40 columns
42 counties
10 education-level categories
```

The education categories were:

```text
Antepreşcolar
Preșcolar
Primar
Gimnazial
Profesional
Liceal
Postliceal
Club sportiv şcolar
Clubul copiilor
Palatul copiilor
```

The key analytical columns contained no missing values:

```text
Judet                         0
Nivel                         0
Numarul elevilor existenti    0
```

The enrollment values were non-negative whole numbers.

One exact duplicate row was detected.

### Română

A fost creat scriptul:

```text
08_profile_enrollment.py
```

Datasetul 2015-2016 conținea:

```text
167.907 rânduri
40 coloane
42 județe
10 categorii de nivel
```

Categoriile educaționale erau:

```text
Antepreşcolar
Preșcolar
Primar
Gimnazial
Profesional
Liceal
Postliceal
Club sportiv şcolar
Clubul copiilor
Palatul copiilor
```

Coloanele analitice principale nu aveau valori lipsă:

```text
Judet                         0
Nivel                         0
Numarul elevilor existenti    0
```

Valorile privind elevii erau întregi și non-negative.

A fost identificat un duplicat exact.

---

## Step 16 — Validate the first raw enrollment dataset

### English

A dedicated validation script was created:

```text
09_validate_enrollment_raw.py
```

The following checks were performed:

```text
exact duplicates
zero enrollment values
negative values
non-integer values
totals by education level
raw national total
```

For 2015-2016:

```text
Negative values: 0
Non-integer values: 0
```

The raw national total was:

```text
3,005,421 students
```

The following categories reported zero students in the first file:

```text
Club sportiv şcolar
Clubul copiilor
Palatul copiilor
```

The formal education levels selected for the analytical indicator were:

```text
Antepreşcolar
Preșcolar
Primar
Gimnazial
Profesional
Liceal
Postliceal
```

### Română

A fost creat scriptul:

```text
09_validate_enrollment_raw.py
```

Au fost verificate:

```text
duplicate exacte
valori zero
valori negative
valori non-integer
totaluri pe nivel
totalul național raw
```

Pentru 2015-2016:

```text
Valori negative: 0
Valori non-integer: 0
```

Totalul național raw a fost:

```text
3.005.421 elevi
```

Următoarele categorii aveau zero elevi în primul fișier:

```text
Club sportiv şcolar
Clubul copiilor
Palatul copiilor
```

Nivelurile formale selectate pentru indicatorul analitic au fost:

```text
Antepreşcolar
Preșcolar
Primar
Gimnazial
Profesional
Liceal
Postliceal
```

---

## Step 17 — Build the first processed enrollment prototype

### English

The initial single-year transformation script was created:

```text
10_transform_enrollment.py
```

The analytical grain was defined as:

```text
County × School Year × Education Level
```

The initial 2015-2016 result contained:

```text
262 analytical rows
42 counties
7 formal education levels
0 missing values
0 duplicate analytical keys
3,005,421 enrolled students
```

County abbreviations were mapped to the same Eurostat NUTS 3 codes used by Employment.

Examples:

```text
HD → RO423
CJ → RO113
B  → RO321
```

Validation returned:

```text
Missing NUTS 3 mappings: 0
Unique NUTS 3 codes: 42
```

This created a common geographical key between Employment and Enrollment.

During this initial prototype, one exact duplicate containing zero students was removed.

This duplicate policy was later reconsidered during the multi-year investigation.

### Română

A fost creat primul script de transformare:

```text
10_transform_enrollment.py
```

Grain-ul analitic a fost definit astfel:

```text
Județ × An școlar × Nivel educațional
```

Rezultatul inițial pentru 2015-2016 conținea:

```text
262 rânduri analitice
42 județe
7 niveluri formale
0 valori lipsă
0 duplicate pe cheia analitică
3.005.421 elevi
```

Abrevierile județelor au fost mapate la aceleași coduri Eurostat NUTS 3 utilizate în Employment.

Exemple:

```text
HD → RO423
CJ → RO113
B  → RO321
```

Validarea a returnat:

```text
Missing NUTS 3 mappings: 0
Unique NUTS 3 codes: 42
```

Astfel a fost creată o cheie geografică comună între Employment și Enrollment.

În acest prototip inițial a fost eliminat un duplicat exact cu zero elevi.

Politica privind duplicatele a fost ulterior reevaluată în analiza multi-an.

---

## Step 18 — Inventory all enrollment resources

### English

All available enrollment resources were inventoried using:

```text
11_inventory_enrollment_resources.py
```

One Excel resource was identified for every available school year.

The main analytical period selected for the project was:

```text
2015-2016
2016-2017
2017-2018
2018-2019
2019-2020
2020-2021
2021-2022
2022-2023
2023-2024
```

Although newer datasets were available, the main series stops at 2023-2024 because the Employment dataset currently ends in calendar year 2023.

A derived field was defined later as:

```text
analysis_year = starting year of school_year
```

Examples:

```text
2015-2016 → 2015
2023-2024 → 2023
```

This creates the common analysis range:

```text
2015–2023
```

This is a modelling convention and does not mean that a school year is identical to a calendar year.

### Română

Toate resursele Enrollment disponibile au fost inventariate folosind:

```text
11_inventory_enrollment_resources.py
```

A fost identificată câte o resursă Excel pentru fiecare an școlar disponibil.

Perioada principală selectată pentru proiect a fost:

```text
2015-2016
2016-2017
2017-2018
2018-2019
2019-2020
2020-2021
2021-2022
2022-2023
2023-2024
```

Deși existau și dataseturi mai recente, seria principală se oprește la 2023-2024 deoarece datasetul Employment se termină în anul calendaristic 2023.

Ulterior a fost definit câmpul:

```text
analysis_year = anul de început al school_year
```

Exemple:

```text
2015-2016 → 2015
2023-2024 → 2023
```

Astfel este obținută perioada comună:

```text
2015–2023
```

Aceasta este o convenție de modelare și nu înseamnă că anul școlar este identic cu anul calendaristic.

---

## Step 19 — Ingest all enrollment raw files

### English

A batch ingestion script was created:

```text
12_ingest_all_enrollment.py
```

Nine official Excel resources were downloaded and stored in:

```text
data/raw/enrollment/
```

Files:

```text
enrollment_2015_2016_raw.xlsx
enrollment_2016_2017_raw.xlsx
enrollment_2017_2018_raw.xlsx
enrollment_2018_2019_raw.xlsx
enrollment_2019_2020_raw.xlsx
enrollment_2020_2021_raw.xlsx
enrollment_2021_2022_raw.xlsx
enrollment_2022_2023_raw.xlsx
enrollment_2023_2024_raw.xlsx
```

No transformations were applied during ingestion.

### Română

A fost creat scriptul:

```text
12_ingest_all_enrollment.py
```

Cele nouă resurse Excel oficiale au fost descărcate și salvate în:

```text
data/raw/enrollment/
```

Fișierele sunt:

```text
enrollment_2015_2016_raw.xlsx
enrollment_2016_2017_raw.xlsx
enrollment_2017_2018_raw.xlsx
enrollment_2018_2019_raw.xlsx
enrollment_2019_2020_raw.xlsx
enrollment_2020_2021_raw.xlsx
enrollment_2021_2022_raw.xlsx
enrollment_2022_2023_raw.xlsx
enrollment_2023_2024_raw.xlsx
```

În etapa de ingestie nu au fost aplicate transformări.

---

## Step 20 — Compare enrollment structures across years

### English

All nine files were structurally compared using:

```text
13_compare_enrollment_structures.py
```

The comparison revealed multiple schema changes:

```text
2015-2016 → 40 columns
2016-2017 → 39 columns
2017-2018 → 40 columns
2018-2019 → 41 columns
2019-2020 → 44 columns
2020-2021 → 40 columns
2021-2022 → 47 columns
2022-2023 → 43 columns
2023-2024 → 43 columns
```

Changes included:

```text
added columns
removed columns
renamed measures
different worksheet names
different header positions
```

This confirmed that a single transformation based only on the 2015-2016 structure would not be reliable.

### Română

Cele nouă fișiere au fost comparate structural folosind:

```text
13_compare_enrollment_structures.py
```

Au fost identificate mai multe schimbări de schemă:

```text
2015-2016 → 40 coloane
2016-2017 → 39 coloane
2017-2018 → 40 coloane
2018-2019 → 41 coloane
2019-2020 → 44 coloane
2020-2021 → 40 coloane
2021-2022 → 47 coloane
2022-2023 → 43 coloane
2023-2024 → 43 coloane
```

Modificările au inclus:

```text
coloane adăugate
coloane eliminate
măsuri redenumite
worksheet-uri diferite
poziții diferite ale header-ului
```

Acest rezultat a demonstrat că o singură transformare bazată exclusiv pe structura 2015-2016 nu ar fi fost sigură.

---

## Step 21 — Identify changing headers and measures

### English

Files with structural differences were inspected using:

```text
14_inspect_enrollment_headers.py
```

The real header positions were determined as:

```text
2015-2016 → header 0
2016-2017 → header 0
2017-2018 → header 0
2018-2019 → header 0
2019-2020 → header 0
2020-2021 → header 0
2021-2022 → header 4
2022-2023 → header 4
2023-2024 → header 4
```

The main enrollment measure also changed.

Earlier files used:

```text
Numarul elevilor existenti
```

Later files used:

```text
Elevi exist anterior-asoc
```

Some files also contained planning variables such as:

```text
Elevi propusi anterior-plan
Elevi propusi curent-plan
```

These planning measures were not used as the main observed enrollment indicator.

### Română

Fișierele cu diferențe structurale au fost inspectate folosind:

```text
14_inspect_enrollment_headers.py
```

Pozițiile reale ale header-ului au fost:

```text
2015-2016 → header 0
2016-2017 → header 0
2017-2018 → header 0
2018-2019 → header 0
2019-2020 → header 0
2020-2021 → header 0
2021-2022 → header 4
2022-2023 → header 4
2023-2024 → header 4
```

S-a modificat și denumirea măsurii principale Enrollment.

Fișierele mai vechi utilizau:

```text
Numarul elevilor existenti
```

iar fișierele mai noi:

```text
Elevi exist anterior-asoc
```

În anumite fișiere existau și variabile de planificare:

```text
Elevi propusi anterior-plan
Elevi propusi curent-plan
```

Aceste măsuri de planificare nu au fost utilizate ca indicator principal privind elevii existenți.

---

## Step 22 — Profile all enrollment years

### English

All nine files were profiled using:

```text
15_profile_all_enrollment_years.py
```

Checks included:

```text
row count
column count
county coverage
education levels
missing values
negative values
zero values
exact duplicates
raw enrollment totals
```

All datasets contained:

```text
42 county-level units
```

No negative enrollment values were detected.

However, several years produced implausibly large raw totals:

```text
2016-2017 → 6,033,366
2017-2018 → 5,898,248
2018-2019 → 5,994,786
2019-2020 → 11,825,624
2020-2021 → 5,836,550
```

This showed that direct summation of the raw enrollment column was unsafe.

### Română

Cele nouă fișiere au fost profilate folosind:

```text
15_profile_all_enrollment_years.py
```

Au fost verificate:

```text
numărul de rânduri
numărul de coloane
acoperirea județelor
nivelurile educaționale
valorile lipsă
valorile negative
valorile zero
duplicatele exacte
totalurile raw
```

Toate dataseturile conțineau:

```text
42 unități județene
```

Nu au fost identificate valori negative.

Totuși, mai mulți ani produceau totaluri raw nerealist de mari:

```text
2016-2017 → 6.033.366
2017-2018 → 5.898.248
2018-2019 → 5.994.786
2019-2020 → 11.825.624
2020-2021 → 5.836.550
```

Acest rezultat a demonstrat că însumarea directă a întregii coloane raw nu este sigură.

---

## Step 23 — Diagnose measures and aggregate rows

### English

A diagnostic script was created:

```text
16_diagnose_enrollment_measures.py
```

The investigation showed that some source files contain both:

```text
detailed educational observations
+
aggregate total rows
```

Many aggregate rows had:

```text
Nivel = missing
```

Examples:

```text
2017-2018
Aggregate rows: 2,949,124
Detailed formal levels: 2,949,124
```

For 2019-2020:

```text
Aggregate rows: 8,869,218
Detailed formal levels: 2,956,406
```

The aggregate value for 2019-2020 represented repeated higher-level totals rather than additional students.

Therefore:

```text
missing Nivel
```

could not simply be interpreted as ordinary missing data.

The final analytical pipeline explicitly retains observations belonging to the selected formal education levels rather than summing all raw rows.

### Română

A fost creat scriptul:

```text
16_diagnose_enrollment_measures.py
```

Investigația a arătat că unele fișiere sursă conțin simultan:

```text
observații educaționale detaliate
+
rânduri agregate de total
```

Multe rânduri agregate aveau:

```text
Nivel = missing
```

Exemplu:

```text
2017-2018
Rânduri agregate: 2.949.124
Niveluri formale detaliate: 2.949.124
```

Pentru 2019-2020:

```text
Rânduri agregate: 8.869.218
Niveluri formale detaliate: 2.956.406
```

Valoarea agregată pentru 2019-2020 reprezenta totaluri de nivel superior repetate, nu elevi suplimentari.

Prin urmare:

```text
Nivel lipsă
```

nu putea fi tratat simplu ca missing data obișnuit.

Pipeline-ul final păstrează explicit observațiile care aparțin nivelurilor educaționale formale selectate, în loc să însumeze toate rândurile raw.

---

## Step 24 — Investigate exact duplicate observations

### English

Exact duplicate observations were investigated using:

```text
17_diagnose_enrollment_duplicates.py
```

Results included:

```text
2015-2016
Extra duplicate rows: 1
Students in extra duplicates: 0

2017-2018
Extra duplicate rows: 1
Students in extra duplicates: 0

2018-2019
Extra duplicate rows: 1
Students in extra duplicates: 24

2020-2021
Extra duplicate rows: 230
Students in extra duplicates: 3,273

2022-2023
Extra duplicate rows: 3
Students in extra duplicates: 0
```

The 2020-2021 duplicates demonstrated that exact duplicate rows can contain real reported student counts.

Therefore, automatic use of:

```python
drop_duplicates()
```

would risk removing legitimate observations.

Some educational formations can share all visible exported characteristics while still representing separate source observations.

The final multi-year pipeline therefore does not automatically remove exact duplicates.

### Română

Observațiile duplicate exacte au fost investigate folosind:

```text
17_diagnose_enrollment_duplicates.py
```

Rezultatele au inclus:

```text
2015-2016
Extra duplicate rows: 1
Elevi în duplicate suplimentare: 0

2017-2018
Extra duplicate rows: 1
Elevi în duplicate suplimentare: 0

2018-2019
Extra duplicate rows: 1
Elevi în duplicate suplimentare: 24

2020-2021
Extra duplicate rows: 230
Elevi în duplicate suplimentare: 3.273

2022-2023
Extra duplicate rows: 3
Elevi în duplicate suplimentare: 0
```

Duplicatele din 2020-2021 au demonstrat că rândurile perfect identice pot conține valori reale raportate.

Prin urmare, utilizarea automată a:

```python
drop_duplicates()
```

ar putea elimina observații legitime.

Anumite formațiuni educaționale pot avea toate caracteristicile exportate identice, fără să reprezinte aceeași observație sursă.

Pipeline-ul multi-an final nu elimină automat duplicatele exacte.

---

## Step 25 — Build the final multi-year enrollment pipeline

### English

The final transformation script was created:

```text
18_transform_all_enrollment.py
```

A configuration-driven approach is used to handle structural differences between years.

For each school year, the configuration defines:

```text
source filename
header row
enrollment measure column
```

The pipeline performs:

```text
read raw Excel
        ↓
select formal education levels
        ↓
standardize numeric enrollment measure
        ↓
validate missing / negative / non-integer values
        ↓
add school_year
        ↓
derive analysis_year
        ↓
map county abbreviation to NUTS 3
        ↓
aggregate to analytical grain
        ↓
validate each year
        ↓
concatenate all years
        ↓
validate final dataset
        ↓
export processed CSV
```

The final analytical grain is:

```text
County × School Year × Education Level
```

The temporal fields are:

```text
school_year
analysis_year
```

Example:

```text
school_year   = 2015-2016
analysis_year = 2015
```

`school_year` preserves the original temporal meaning of the education data.

`analysis_year` uses the starting year of the school year and enables controlled alignment with annual datasets such as Employment.

The two fields should not be interpreted as representing identical time periods.

### Română

A fost creat scriptul final:

```text
18_transform_all_enrollment.py
```

Pentru gestionarea diferențelor dintre ani este utilizată o abordare bazată pe configurații.

Pentru fiecare an școlar sunt definite:

```text
fișierul sursă
rândul header-ului
coloana cu măsura Enrollment
```

Pipeline-ul execută:

```text
citire Excel raw
        ↓
selectarea nivelurilor formale
        ↓
standardizarea măsurii numerice
        ↓
validarea missing / negative / non-integer
        ↓
adăugarea school_year
        ↓
derivarea analysis_year
        ↓
maparea județului la NUTS 3
        ↓
agregarea la grain-ul analitic
        ↓
validarea fiecărui an
        ↓
concatenarea tuturor anilor
        ↓
validarea datasetului final
        ↓
export CSV procesat
```

Grain-ul analitic final este:

```text
Județ × An școlar × Nivel educațional
```

Câmpurile temporale sunt:

```text
school_year
analysis_year
```

Exemplu:

```text
school_year   = 2015-2016
analysis_year = 2015
```

`school_year` păstrează semnificația temporală originală a datelor educaționale.

`analysis_year` utilizează anul de început al anului școlar și permite alinierea controlată cu dataseturi anuale precum Employment.

Cele două câmpuri nu trebuie interpretate ca reprezentând perioade temporale identice.

---

## Step 26 — Validate the final enrollment dataset

### English

The final processed Enrollment dataset contains:

```text
2,432 rows
6 columns
9 school years
42 counties
7 formal education levels
```

Period:

```text
2015-2016 → 2023-2024
```

Analysis years:

```text
2015 → 2023
```

Final validation:

```text
Missing values: 0
Duplicate analytical keys: 0
Unique counties: 42
Unique education levels: 7
Unique school years: 9
```

National enrollment totals by school year:

```text
2015-2016    3,005,421
2016-2017    3,016,804
2017-2018    2,949,124
2018-2019    2,988,088
2019-2020    2,956,406
2020-2021    2,918,275
2021-2022    2,948,781
2022-2023    2,953,703
2023-2024    2,951,062
```

All automated final checks passed successfully.

The processed dataset was exported to:

```text
data/processed/enrollment_clean.csv
```

Final columns:

```text
county_code
county_abbr
school_year
analysis_year
education_level
enrolled_students
```

### Română

Datasetul final Enrollment conține:

```text
2.432 rânduri
6 coloane
9 ani școlari
42 județe
7 niveluri educaționale formale
```

Perioada:

```text
2015-2016 → 2023-2024
```

Ani analitici:

```text
2015 → 2023
```

Validarea finală:

```text
Valori lipsă: 0
Duplicate pe cheia analitică: 0
Județe unice: 42
Niveluri educaționale unice: 7
Ani școlari unici: 9
```

Totalurile naționale pe an școlar:

```text
2015-2016    3.005.421
2016-2017    3.016.804
2017-2018    2.949.124
2018-2019    2.988.088
2019-2020    2.956.406
2020-2021    2.918.275
2021-2022    2.948.781
2022-2023    2.953.703
2023-2024    2.951.062
```

Toate verificările automate finale au trecut cu succes.

Datasetul procesat a fost exportat în:

```text
data/processed/enrollment_clean.csv
```

Coloanele finale:

```text
county_code
county_abbr
school_year
analysis_year
education_level
enrolled_students
```

---

# Enrollment Pipeline Status

## English

The complete Enrollment pipeline is operational.

```text
data.gov.ro CKAN API
        ↓
Dataset discovery
        ↓
Official Excel resources
        ↓
Raw Excel layer
        ↓
Schema inspection
        ↓
Cross-year structural validation
        ↓
Measure diagnosis
        ↓
Aggregate-row handling
        ↓
Duplicate investigation
        ↓
County / NUTS 3 standardization
        ↓
Yearly transformation
        ↓
Multi-year concatenation
        ↓
Data quality validation
        ↓
Processed CSV
        ↓
Power BI
```

Final output:

```text
Source: data.gov.ro
Period: 2015-2016 → 2023-2024
Analysis years: 2015 → 2023
Geographical units: 42
Formal education levels: 7
Observations: 2,432
Missing values: 0
Duplicate analytical keys: 0
Processed file: data/processed/enrollment_clean.csv
```

## Română

Pipeline-ul complet Enrollment este funcțional.

```text
data.gov.ro CKAN API
        ↓
Identificarea dataseturilor
        ↓
Resurse Excel oficiale
        ↓
Strat Excel raw
        ↓
Inspectarea schemelor
        ↓
Validarea structurii între ani
        ↓
Diagnosticarea măsurilor
        ↓
Gestionarea rândurilor agregate
        ↓
Investigarea duplicatelor
        ↓
Standardizarea județelor / NUTS 3
        ↓
Transformarea fiecărui an
        ↓
Concatenarea multi-an
        ↓
Validarea calității
        ↓
CSV procesat
        ↓
Power BI
```

Rezultatul final:

```text
Sursă: data.gov.ro
Perioadă: 2015-2016 → 2023-2024
Ani analitici: 2015 → 2023
Unități geografice: 42
Niveluri educaționale formale: 7
Observații: 2.432
Valori lipsă: 0
Duplicate pe cheia analitică: 0
Fișier procesat: data/processed/enrollment_clean.csv
```

---

# Baccalaureate Pipeline

## Step 27 — Define the Baccalaureate analytical scope

### English

The third major analytical component of the project focuses on Romanian Baccalaureate examination outcomes.

Official annual candidate-level datasets were investigated for the period:

```text
2015–2023
```

Only the first examination session was selected for the analytical pipeline.

The reason for this decision is methodological.

Candidates may participate in more than one Baccalaureate session during the same year. Combining multiple sessions without a reliable cross-session candidate identity would create a risk of counting the same individual more than once.

Therefore, the Baccalaureate indicator is defined consistently as:

```text
Baccalaureate — Session I
2015–2023
```

The target analytical grain was defined as:

```text
County × Year
```

This grain makes the Baccalaureate dataset compatible with the geographical structure used by Employment and Enrollment.

### Română

A treia componentă analitică majoră a proiectului este reprezentată de rezultatele examenului național de Bacalaureat.

Au fost investigate dataseturile oficiale la nivel de candidat pentru perioada:

```text
2015–2023
```

Pentru pipeline-ul analitic a fost selectată exclusiv prima sesiune a examenului.

Decizia este una metodologică.

Un candidat poate participa la mai multe sesiuni ale Bacalaureatului în același an. Combinarea sesiunilor fără un identificator sigur al candidatului între sesiuni ar introduce riscul numărării aceleiași persoane de mai multe ori.

Prin urmare, indicatorul Bacalaureat este definit consecvent astfel:

```text
Bacalaureat — Sesiunea I
2015–2023
```

Grain-ul analitic țintă a fost definit astfel:

```text
Județ × An
```

Această granularitate permite integrarea datasetului de Bacalaureat cu structura geografică utilizată de Employment și Enrollment.

---

## Step 28 — Inspect annual Baccalaureate source formats

### English

The Baccalaureate source files were not structurally homogeneous across years.

The investigation identified several source formats:

```text
2015 → CSV
2016 → CSV / ODS
2017 → CSV / ODS
2018 → XLSX
2019 → XLSX
2020 → XLSX
2021 → XLSX
2022 → XLSX
2023 → XLSX
```

The raw structures changed across years.

Important differences included:

```text
file format
delimiter behavior
text encoding
worksheet structure
column count
column names
grade representation
result representation
```

The 2015 CSV was identified as a UTF-16 tab-separated file despite its `.csv` extension.

The official 2016 CSV could not be parsed reliably and the official ODS version was used instead.

The official 2017 CSV also contained a structural problem: commas were used both as delimiters and as decimal separators without reliable quoting.

This produced inconsistent row widths.

The official ODS resource was therefore used for 2017 as well.

The Excel files from later years also showed schema changes.

In particular:

```text
2022 → 74 columns
2023 → 52 columns
```

This confirmed that the pipeline could not safely assume a single static schema for all years.

### Română

Fișierele sursă pentru Bacalaureat nu au avut o structură omogenă între ani.

Investigația a identificat mai multe formate:

```text
2015 → CSV
2016 → CSV / ODS
2017 → CSV / ODS
2018 → XLSX
2019 → XLSX
2020 → XLSX
2021 → XLSX
2022 → XLSX
2023 → XLSX
```

Structura datelor raw s-a modificat între ani.

Diferențele importante au inclus:

```text
formatul fișierului
comportamentul delimiterului
encoding-ul textului
structura worksheet-urilor
numărul de coloane
denumirea coloanelor
reprezentarea notelor
reprezentarea rezultatelor
```

Fișierul CSV din 2015 a fost identificat ca fiind de fapt un fișier UTF-16 separat prin TAB.

CSV-ul oficial din 2016 nu a putut fi interpretat în mod sigur, astfel că a fost utilizată versiunea oficială ODS.

CSV-ul oficial din 2017 prezenta de asemenea o problemă structurală: virgula era utilizată atât ca delimiter, cât și ca separator zecimal fără o delimitare sigură prin quoting.

Acest lucru genera un număr inconsistent de câmpuri pe rând.

Prin urmare, și pentru 2017 a fost utilizată resursa oficială ODS.

Fișierele Excel din anii următori au prezentat și ele modificări de schemă.

În special:

```text
2022 → 74 coloane
2023 → 52 coloane
```

Investigația a confirmat că pipeline-ul nu poate presupune o singură schemă statică pentru toți anii.

---

## Step 29 — Validate candidate-level source integrity

### English

Before transformation, the candidate-level datasets were validated individually.

The final number of candidate records identified for Session I was:

```text
2015    168,939
2016    137,338
2017    135,513
2018    136,864
2019    136,091
2020    155,650
2021    133,664
2022    126,453
2023    130,522
```

For every year:

```text
candidate rows = unique candidate codes
```

No duplicate candidate identifiers were detected inside the selected annual Session I datasets.

This provided an important integrity check before candidate-level standardization and aggregation.

### Română

Înainte de transformare, dataseturile la nivel de candidat au fost validate individual.

Numărul final de înregistrări pentru Sesiunea I a fost:

```text
2015    168.939
2016    137.338
2017    135.513
2018    136.864
2019    136.091
2020    155.650
2021    133.664
2022    126.453
2023    130.522
```

Pentru fiecare an:

```text
număr rânduri candidați = număr coduri unice de candidat
```

Nu au fost identificate coduri duplicate de candidat în dataseturile anuale selectate pentru Sesiunea I.

Aceasta reprezintă o verificare importantă de integritate înainte de standardizarea și agregarea datelor.

---

## Step 30 — Build and validate the SIIIR county mapping

### English

The Baccalaureate files contain a SIIIR institutional code.

A geographical mapping investigation was performed using the 2022 dataset because that year contains both:

```text
Cod SIIIR
Judet
```

The first two digits of the normalized SIIIR code were found to identify the county uniquely.

The mapping produced:

```text
42 SIIIR prefixes
→
42 Romanian county-level units
```

The mapping includes the 41 counties and Bucharest.

The final prefix mapping is:

```text
01 → AB
02 → AR
03 → AG
04 → BC
05 → BH
06 → BN
07 → BT
08 → BV
09 → BR
10 → BZ
11 → CS
12 → CJ
13 → CT
14 → CV
15 → DB
16 → DJ
17 → GL
18 → GJ
19 → HR
20 → HD
21 → IL
22 → IS
23 → IF
24 → MM
25 → MH
26 → MS
27 → NT
28 → OT
29 → PH
30 → SM
31 → SJ
32 → SB
33 → SV
34 → TR
35 → TM
36 → TL
37 → VS
38 → VL
39 → VN
40 → B
51 → CL
52 → GR
```

An initial diagnostic produced apparent conflicts for several prefixes.

The cause was not inconsistent geography.

The SIIIR column had initially been interpreted numerically, which removed leading zeroes from some codes.

The mapping was therefore revalidated after reading SIIIR as text.

### Română

Fișierele de Bacalaureat conțin codul instituțional SIIIR.

A fost realizată o investigație privind maparea geografică folosind datasetul din 2022, deoarece acesta conține simultan:

```text
Cod SIIIR
Judet
```

S-a constatat că primele două cifre ale codului SIIIR normalizat identifică în mod unic județul.

Maparea a produs:

```text
42 prefixuri SIIIR
→
42 unități județene din România
```

Maparea include cele 41 de județe și București.

Maparea finală a prefixurilor este:

```text
01 → AB
02 → AR
03 → AG
04 → BC
05 → BH
06 → BN
07 → BT
08 → BV
09 → BR
10 → BZ
11 → CS
12 → CJ
13 → CT
14 → CV
15 → DB
16 → DJ
17 → GL
18 → GJ
19 → HR
20 → HD
21 → IL
22 → IS
23 → IF
24 → MM
25 → MH
26 → MS
27 → NT
28 → OT
29 → PH
30 → SM
31 → SJ
32 → SB
33 → SV
34 → TR
35 → TM
36 → TL
37 → VS
38 → VL
39 → VN
40 → B
51 → CL
52 → GR
```

Un diagnostic inițial a produs aparent mai multe conflicte între prefixuri și județe.

Problema nu provenea din geografie.

Coloana SIIIR fusese interpretată inițial numeric, ceea ce elimina zero-ul de la începutul anumitor coduri.

Maparea a fost astfel revalidată după citirea codului SIIIR ca text.

---

## Step 31 — Normalize historical SIIIR codes

### English

A separate diagnostic was required for the 2015 dataset.

The 2015 source contained:

```text
33,721 codes with 9 digits
135,218 codes with 10 digits
```

The shorter codes belonged to counties whose standard prefix begins with zero.

The issue was therefore caused by a missing leading zero rather than by a different coding system.

The final normalization uses:

```python
.str.zfill(10)
```

After normalization:

```text
all SIIIR codes → 10 digits
valid county prefixes → 42
unknown prefixes → 0
missing prefixes → 0
```

The same standardized geographical logic could therefore be applied consistently to all Baccalaureate years.

### Română

Pentru datasetul din 2015 a fost necesar un diagnostic separat.

Sursa din 2015 conținea:

```text
33.721 coduri cu 9 cifre
135.218 coduri cu 10 cifre
```

Codurile mai scurte aparțineau județelor al căror prefix standard începe cu zero.

Problema provenea astfel din pierderea zero-ului inițial și nu din utilizarea unui sistem diferit de codificare.

Normalizarea finală utilizează:

```python
.str.zfill(10)
```

După normalizare:

```text
toate codurile SIIIR → 10 cifre
prefixuri județene valide → 42
prefixuri necunoscute → 0
prefixuri lipsă → 0
```

Aceeași logică geografică standardizată a putut fi astfel aplicată tuturor anilor de Bacalaureat.

---

## Step 32 — Standardize Baccalaureate result statuses

### English

The candidate-level result field was profiled across all years.

Four result categories were identified:

```text
Promovat
Nepromovat
Absent
Eliminat
```

No missing result statuses were detected.

The candidate indicators were defined as:

```text
is_passed
is_failed
is_absent
is_eliminated
```

The analytical definition of a present candidate is:

```text
present =
Promovat
+
Nepromovat
+
Eliminat
```

Therefore:

```text
present_candidates
=
candidates
-
absent_candidates
```

Eliminated candidates are considered present because they participated in the examination process.

The pass rate denominator therefore uses present candidates.

### Română

Câmpul privind rezultatul candidatului a fost profilat pentru toți anii.

Au fost identificate patru categorii:

```text
Promovat
Nepromovat
Absent
Eliminat
```

Nu au fost identificate statusuri lipsă.

Au fost definiți următorii indicatori la nivel de candidat:

```text
is_passed
is_failed
is_absent
is_eliminated
```

Definiția analitică a candidatului prezent este:

```text
prezent =
Promovat
+
Nepromovat
+
Eliminat
```

Prin urmare:

```text
present_candidates
=
candidates
-
absent_candidates
```

Candidații eliminați sunt considerați prezenți deoarece au participat la procesul de examinare.

Numitorul ratei de promovare utilizează astfel candidații prezenți.

---

## Step 33 — Standardize final-grade semantics

### English

The final-grade fields also required cross-year normalization.

For most years, candidates without a valid final average had a blank value.

The 2022 file used sentinel values instead:

```text
-3 → Nepromovat without valid final average
-2 → Absent
-1 → Eliminat
```

These values are not real examination grades.

The standardized final grade was therefore defined as:

```text
valid grade only if:

1 <= grade <= 10
```

All other values are treated as missing analytical grades.

Validation confirmed:

```text
Promovat → final grade >= 6
Nepromovat with valid grade → final grade < 6
Absent → no valid final grade
Eliminat → no valid final grade
```

The number of observations with valid grades is stored separately as:

```text
graded_candidates
```

### Română

Și câmpurile privind media finală au necesitat normalizare între ani.

În majoritatea anilor, candidații fără o medie finală validă aveau valoarea goală.

Fișierul din 2022 utiliza însă valori sentinel:

```text
-3 → Nepromovat fără medie finală validă
-2 → Absent
-1 → Eliminat
```

Aceste valori nu reprezintă note reale.

Prin urmare, nota finală standardizată a fost definită astfel:

```text
nota este validă numai dacă:

1 <= nota <= 10
```

Toate celelalte valori sunt tratate ca note analitice lipsă.

Validarea a confirmat:

```text
Promovat → medie finală >= 6
Nepromovat cu medie validă → medie finală < 6
Absent → fără medie finală validă
Eliminat → fără medie finală validă
```

Numărul observațiilor cu medie finală validă este păstrat separat în:

```text
graded_candidates
```

---

## Step 34 — Create the standardized candidate-level layer

### English

After source-specific normalization, all years were transformed into one common candidate-level schema.

The standardized candidate-level dataset was created as:

```text
data/interim/baccalaureate_candidate_standardized.csv
```

It contains:

```text
1,261,034 rows
```

Final candidate-level columns:

```text
year
candidate_code
siiir_code
county_prefix
county_abbr
status
final_grade
is_present
is_passed
is_failed
is_absent
is_eliminated
has_valid_grade
```

This file is an intermediate analytical layer.

It contains candidate-level information and is therefore intended to remain local to the data-processing workflow.

It must not be published as part of the public GitHub dataset layer.

Only aggregated Baccalaureate data are intended for publication and dashboard use.

### Română

După aplicarea normalizărilor specifice fiecărei surse, toți anii au fost transformați într-o schemă comună la nivel de candidat.

Datasetul standardizat a fost creat în:

```text
data/interim/baccalaureate_candidate_standardized.csv
```

Acesta conține:

```text
1.261.034 rânduri
```

Coloanele finale la nivel de candidat sunt:

```text
year
candidate_code
siiir_code
county_prefix
county_abbr
status
final_grade
is_present
is_passed
is_failed
is_absent
is_eliminated
has_valid_grade
```

Acest fișier reprezintă un strat analitic intermediar.

El conține informații la nivel de candidat și este destinat să rămână local în cadrul procesului de prelucrare.

Fișierul nu trebuie publicat ca parte a stratului public de date din repository-ul GitHub.

Pentru publicare și utilizare în dashboard sunt utilizate numai date agregate de Bacalaureat.

---

## Step 35 — Aggregate Baccalaureate results to County × Year

### English

The standardized candidate-level dataset was aggregated using:

```text
County × Year
```

as the final analytical grain.

The processed file was created as:

```text
data/processed/baccalaureate_clean.csv
```

Final shape:

```text
378 rows × 14 columns
```

which corresponds to:

```text
42 counties × 9 years
```

The final columns are:

```text
county_code
county
county_abbr
year
candidates
present_candidates
passed_candidates
failed_candidates
absent_candidates
eliminated_candidates
graded_candidates
final_grade_sum
pass_rate
average_grade
```

The main formulas are:

```text
pass_rate
=
passed_candidates
/
present_candidates
```

and:

```text
average_grade
=
final_grade_sum
/
graded_candidates
```

The additional fields:

```text
final_grade_sum
graded_candidates
```

are preserved intentionally.

They make it possible to calculate the correct weighted average in Power BI across multiple counties or years.

### Română

Datasetul standardizat la nivel de candidat a fost agregat folosind grain-ul final:

```text
Județ × An
```

Fișierul procesat a fost creat în:

```text
data/processed/baccalaureate_clean.csv
```

Dimensiunea finală este:

```text
378 rânduri × 14 coloane
```

corespunzând structurii:

```text
42 județe × 9 ani
```

Coloanele finale sunt:

```text
county_code
county
county_abbr
year
candidates
present_candidates
passed_candidates
failed_candidates
absent_candidates
eliminated_candidates
graded_candidates
final_grade_sum
pass_rate
average_grade
```

Principalele formule sunt:

```text
pass_rate
=
passed_candidates
/
present_candidates
```

și:

```text
average_grade
=
final_grade_sum
/
graded_candidates
```

Câmpurile suplimentare:

```text
final_grade_sum
graded_candidates
```

sunt păstrate intenționat.

Ele permit calcularea corectă a mediei ponderate în Power BI atunci când sunt selectate mai multe județe sau mai mulți ani.

---

## Step 36 — Validate the final Baccalaureate dataset

### English

The final Baccalaureate aggregation was validated before integration into Power BI.

Results:

```text
Rows: 378
Counties: 42
Years: 9
Period: 2015–2023
Missing values: 0
Duplicate County × Year keys: 0
```

Every year contains all 42 county-level units.

Candidate accounting was validated using:

```text
candidates
=
passed_candidates
+
failed_candidates
+
absent_candidates
+
eliminated_candidates
```

Present-candidate accounting was validated using:

```text
present_candidates
=
passed_candidates
+
failed_candidates
+
eliminated_candidates
```

National validation produced the following results:

```text
Year   Candidates   Present   Passed   Pass rate   Average grade

2015     168,939     159,716   108,320   67.82%      7.7304
2016     137,338     129,395    88,167   68.14%      7.7542
2017     135,513     128,510    93,641   72.87%      7.8762
2018     136,864     123,620    86,163   69.70%      7.8419
2019     136,091     129,168    89,216   69.07%      7.8327
2020     155,650     147,929    95,475   64.54%      7.9052
2021     133,664     127,001    88,590   69.76%      7.8630
2022     126,453     121,473    91,331   75.19%      7.9273
2023     130,522     125,352    94,004   74.99%      7.8055
```

The Baccalaureate processed dataset was therefore considered ready for dimensional modelling.

### Română

Agregarea finală pentru Bacalaureat a fost validată înainte de integrarea în Power BI.

Rezultatele:

```text
Rânduri: 378
Județe: 42
Ani: 9
Perioadă: 2015–2023
Valori lipsă: 0
Duplicate Județ × An: 0
```

Fiecare an conține toate cele 42 de unități județene.

Consistența numărului total de candidați a fost validată prin:

```text
candidates
=
passed_candidates
+
failed_candidates
+
absent_candidates
+
eliminated_candidates
```

Consistența candidaților prezenți a fost validată prin:

```text
present_candidates
=
passed_candidates
+
failed_candidates
+
eliminated_candidates
```

Validarea la nivel național a produs:

```text
An     Candidați   Prezenți   Promovați   Rată promovare   Medie

2015     168.939     159.716    108.320       67,82%        7,7304
2016     137.338     129.395     88.167       68,14%        7,7542
2017     135.513     128.510     93.641       72,87%        7,8762
2018     136.864     123.620     86.163       69,70%        7,8419
2019     136.091     129.168     89.216       69,07%        7,8327
2020     155.650     147.929     95.475       64,54%        7,9052
2021     133.664     127.001     88.590       69,76%        7,8630
2022     126.453     121.473     91.331       75,19%        7,9273
2023     130.522     125.352     94.004       74,99%        7,8055
```

Datasetul procesat pentru Bacalaureat a fost astfel considerat pregătit pentru modelarea dimensională.

---

# Baccalaureate Pipeline Status

## English

The complete Baccalaureate pipeline is operational.

```text
Official annual source files
        ↓
Format inspection
        ↓
Cross-year schema diagnosis
        ↓
ODS fallback for malformed CSV sources
        ↓
Candidate-code validation
        ↓
SIIIR normalization
        ↓
County mapping
        ↓
Result-status normalization
        ↓
Final-grade normalization
        ↓
Candidate-level standardized layer
        ↓
County × Year aggregation
        ↓
Data quality validation
        ↓
Processed CSV
        ↓
Power BI
```

Final output:

```text
Period: 2015–2023
Session: Session I
Geographical units: 42
Years: 9
Observations: 378
Missing values: 0
Duplicate County × Year keys: 0
Processed file: data/processed/baccalaureate_clean.csv
```

## Română

Pipeline-ul complet pentru Bacalaureat este funcțional.

```text
Fișiere sursă oficiale anuale
        ↓
Inspectarea formatelor
        ↓
Diagnosticarea schemelor între ani
        ↓
Fallback ODS pentru sursele CSV problematice
        ↓
Validarea codurilor de candidat
        ↓
Normalizarea SIIIR
        ↓
Maparea județelor
        ↓
Normalizarea statusurilor
        ↓
Normalizarea mediilor finale
        ↓
Strat standardizat la nivel de candidat
        ↓
Agregare Județ × An
        ↓
Validarea calității
        ↓
CSV procesat
        ↓
Power BI
```

Rezultatul final:

```text
Perioadă: 2015–2023
Sesiune: Sesiunea I
Unități geografice: 42
Ani: 9
Observații: 378
Valori lipsă: 0
Duplicate Județ × An: 0
Fișier procesat: data/processed/baccalaureate_clean.csv
```

---

# Higher Education Investigation

## Step 37 — Investigate INS TEMPO SCL103D

### English

After completing the Baccalaureate pipeline, Higher Education was investigated as a possible fourth analytical component.

The preferred objective was to obtain a dataset with a grain compatible with the existing model:

```text
County × Year
```

The INS TEMPO matrix investigated was:

```text
SCL103D
```

A dedicated script was created:

```text
44_inspect_higher_education_scl103d.py
```

The objective was to inspect the matrix metadata and determine whether Higher Education observations could be extracted programmatically.

The INS TEMPO endpoint repeatedly terminated the connection with:

```text
ConnectionResetError
WinError 10054
```

The script was preserved for traceability.

The failure was interpreted as an accessibility problem from the development environment, not as proof that the statistical series itself does not exist.

### Română

După finalizarea pipeline-ului de Bacalaureat, a fost investigată includerea educației superioare ca a patra componentă analitică.

Obiectivul preferat a fost obținerea unui dataset compatibil cu grain-ul existent:

```text
Județ × An
```

Matricea INS TEMPO investigată a fost:

```text
SCL103D
```

A fost creat scriptul:

```text
44_inspect_higher_education_scl103d.py
```

Scopul a fost inspectarea metadata matricei și verificarea posibilității de extragere programatică a observațiilor privind educația superioară.

Endpoint-ul INS TEMPO a întrerupt în mod repetat conexiunea cu:

```text
ConnectionResetError
WinError 10054
```

Scriptul a fost păstrat pentru trasabilitate.

Eșecul este interpretat ca o problemă de accesibilitate din mediul de dezvoltare, nu ca dovadă că seria statistică nu există.

---

## Step 38 — Search data.gov.ro for Higher Education alternatives

### English

Because the INS TEMPO API was not accessible reliably, the national open-data portal was investigated as an alternative source.

A discovery script was created:

```text
45_inventory_datagov_higher_education.py
```

The CKAN catalogue search identified several official datasets published by the Ministry of Education.

The most promising multi-year resource was:

```text
Number of students enrolled in bachelor's degree studies
by language of instruction
```

The resource contains data reported by Higher Education institutions through the national ANS platform.

The available period was:

```text
2014-2015 → 2020-2021
```

The workbook was downloaded for structural inspection.

### Română

Deoarece API-ul INS TEMPO nu a putut fi accesat stabil, portalul național de date deschise a fost investigat ca sursă alternativă.

A fost creat scriptul:

```text
45_inventory_datagov_higher_education.py
```

Căutarea în catalogul CKAN a identificat mai multe dataseturi oficiale publicate de Ministerul Educației.

Cea mai promițătoare resursă multi-an a fost reprezentată de:

```text
Numărul studenților înmatriculați la studii universitare
de licență, defalcat pe limba de studiu
```

Resursa conține date raportate de instituțiile de învățământ superior prin platforma națională ANS.

Perioada disponibilă era:

```text
2014-2015 → 2020-2021
```

Workbook-ul a fost descărcat pentru inspectarea structurii.

---

## Step 39 — Inspect the ANS Higher Education workbook

### English

A dedicated inspection script was created:

```text
46_ingest_and_inspect_higher_education_licenta.py
```

The source file is an XLSB workbook.

The workbook contains information such as:

```text
university code
university
university type
academic year
scientific field
language of instruction
number of students
reference date
```

The source documentation explains that data are reported at two reference dates:

```text
1 October
1 January
```

For state universities financed by the Ministry of Education, observations reported on 1 January are considered final.

Similar rules apply to military and private institutions, with documented exceptions in years where only October data were reported.

The workbook is analytically useful at university level.

However, it does not contain a direct county field suitable for the project.

Mapping the entire student population of a university to the county inferred from its name would not be methodologically safe because universities may operate faculties, extensions, or university centres outside the county of their main headquarters.

The source itself documents institutional reorganisations and university centres across the period.

For this reason, the ANS workbook was not transformed into a County × Year Higher Education indicator.

### Română

A fost creat un script dedicat pentru inspecție:

```text
46_ingest_and_inspect_higher_education_licenta.py
```

Fișierul sursă este un workbook XLSB.

Workbook-ul conține informații precum:

```text
cod universitate
universitate
tip universitate
an universitar
ramură de știință
limba de predare
număr studenți
data de referință
```

Documentația sursei explică faptul că datele sunt raportate la două date de referință:

```text
1 octombrie
1 ianuarie
```

Pentru universitățile de stat finanțate de Ministerul Educației, observațiile raportate la 1 ianuarie sunt considerate finale.

Reguli similare se aplică instituțiilor militare și particulare, existând excepții documentate pentru anii în care au fost raportate doar date la 1 octombrie.

Workbook-ul este util analitic la nivel de universitate.

Totuși, acesta nu conține un câmp direct pentru județ care să fie adecvat proiectului.

Atribuirea întregii populații de studenți a unei universități județului dedus din numele instituției nu ar fi metodologic sigură, deoarece universitățile pot avea facultăți, extensii sau centre universitare în alte județe decât sediul principal.

Sursa documentează inclusiv reorganizări instituționale și centre universitare pe parcursul perioadei.

Din acest motiv, workbook-ul ANS nu a fost transformat într-un indicator Higher Education la grain-ul Județ × An.

---

## Step 40 — Perform a robust INS TEMPO retry

### English

A final robust connectivity test was implemented using:

```text
47_retry_ins_scl103d_robust.py
```

The script tested multiple official-host endpoint variants with:

```text
retries
timeouts
exponential backoff
HTTP and HTTPS variants
SSL diagnostic fallback
```

The tested endpoint variants included:

```text
http://statistici.insse.ro:8077/tempo-ins/matrix/SCL103D
https://statistici.insse.ro:8077/tempo-ins/matrix/SCL103D
https://statistici.insse.ro/tempo-ins/matrix/SCL103D
http://statistici.insse.ro/tempo-ins/matrix/SCL103D
```

The tests produced two main classes of errors:

```text
WinError 10054
connection forcibly closed by remote host
```

and:

```text
WinError 10061
connection actively refused
```

All configured requests failed.

No analytical dataset was generated from the failed API requests.

The Higher Education component was therefore deferred rather than constructed using an unreliable geographical approximation.

### Română

A fost implementat un ultim test robust de conectivitate folosind:

```text
47_retry_ins_scl103d_robust.py
```

Scriptul a testat mai multe variante ale endpoint-ului oficial folosind:

```text
retry-uri
timeout-uri
exponential backoff
variante HTTP și HTTPS
fallback diagnostic SSL
```

Variantele testate au inclus:

```text
http://statistici.insse.ro:8077/tempo-ins/matrix/SCL103D
https://statistici.insse.ro:8077/tempo-ins/matrix/SCL103D
https://statistici.insse.ro/tempo-ins/matrix/SCL103D
http://statistici.insse.ro/tempo-ins/matrix/SCL103D
```

Testele au produs două clase principale de erori:

```text
WinError 10054
conexiune închisă forțat de server
```

și:

```text
WinError 10061
conexiune refuzată activ
```

Toate requesturile configurate au eșuat.

Nu a fost generat niciun dataset analitic din aceste requesturi nereușite.

Componenta Higher Education a fost astfel amânată în loc să fie construită folosind o aproximare geografică nesigură.

---

# Higher Education Decision

## English

Higher Education remains a valuable potential extension of the project.

Conceptually, it would extend the analytical chain from:

```text
pre-university enrollment
        ↓
Baccalaureate outcomes
        ↓
Higher Education
        ↓
employment
```

However, the current project prioritizes:

```text
official data
reproducibility
geographical consistency
methodological validity
```

over adding an indicator only for completeness.

The ANS source is official and useful but cannot currently be transformed safely into the required County × Year grain.

The preferred INS TEMPO source could not be accessed reliably from the development environment.

Therefore:

```text
Higher Education
=
DEFERRED FOR A FUTURE VERSION
```

It can later be added as a separate fact table if a reproducible county-level source becomes available.

### Română

Educația superioară rămâne o extensie potențială valoroasă a proiectului.

Conceptual, aceasta ar completa lanțul analitic:

```text
înscriere în învățământul preuniversitar
        ↓
rezultate Bacalaureat
        ↓
educație superioară
        ↓
ocupare
```

Totuși, proiectul actual prioritizează:

```text
date oficiale
reproductibilitate
consistență geografică
validitate metodologică
```

înaintea introducerii unui indicator doar pentru completitudine.

Sursa ANS este oficială și utilă, dar nu poate fi transformată în siguranță în grain-ul Județ × An necesar proiectului.

Sursa preferată INS TEMPO nu a putut fi accesată stabil din mediul de dezvoltare.

Prin urmare:

```text
Higher Education
=
AMÂNAT PENTRU O VERSIUNE VIITOARE
```

Componenta poate fi adăugată ulterior ca un fact table separat dacă devine disponibilă o sursă județeană reproductibilă.

---

# Final Processed Data Validation

## Step 41 — Create a cross-dataset validation layer

### English

After all three production datasets were completed, a final cross-dataset validation script was created:

```text
48_validate_processed_datasets.py
```

The script validates:

```text
data/processed/employment_clean.csv
data/processed/enrollment_clean.csv
data/processed/baccalaureate_clean.csv
```

The purpose of this final validation layer is to detect structural or analytical problems before the datasets are imported into Power BI.

The script does not modify the processed datasets.

It performs validation only.

### Română

După finalizarea celor trei dataseturi de producție, a fost creat un script final de validare cross-dataset:

```text
48_validate_processed_datasets.py
```

Scriptul validează:

```text
data/processed/employment_clean.csv
data/processed/enrollment_clean.csv
data/processed/baccalaureate_clean.csv
```

Scopul acestui strat final de validare este detectarea eventualelor probleme structurale sau analitice înainte de importarea datelor în Power BI.

Scriptul nu modifică dataseturile procesate.

Acesta realizează exclusiv validări.

---

## Step 42 — Validate Employment in the final audit

### English

The final Employment dataset contains:

```text
420 rows
5 columns
42 counties
10 years
2014–2023
```

The audit confirmed:

```text
required columns present
missing values = 0
duplicate County × Year keys = 0
42 counties in every year
negative employment values = 0
```

The conversion:

```text
employees
=
employees_thousands × 1000
```

was also validated successfully for every row.

The mapping:

```text
county_code → county
```

is one-to-one and internally consistent.

### Română

Datasetul final Employment conține:

```text
420 rânduri
5 coloane
42 județe
10 ani
2014–2023
```

Auditul a confirmat:

```text
toate coloanele necesare sunt prezente
valori lipsă = 0
duplicate Județ × An = 0
42 județe în fiecare an
valori negative pentru employment = 0
```

Conversia:

```text
employees
=
employees_thousands × 1000
```

a fost de asemenea validată pentru fiecare rând.

Maparea:

```text
county_code → county
```

este unu-la-unu și consistentă intern.

---

## Step 43 — Validate Enrollment in the final audit

### English

The final Enrollment dataset contains:

```text
2,432 rows
6 columns
42 counties
9 analysis years
7 formal education levels
```

The audit confirmed:

```text
required columns present
missing values = 0
duplicate analytical keys = 0
42 counties in every analysis year
negative enrollment values = 0
```

The expected education-level set was confirmed:

```text
Antepreşcolar
Preșcolar
Primar
Gimnazial
Profesional
Liceal
Postliceal
```

The temporal relationship was also validated:

```text
analysis_year
=
starting year of school_year
```

Examples:

```text
2015-2016 → 2015
2023-2024 → 2023
```

The mapping:

```text
county_code → county_abbr
```

is internally consistent.

### Română

Datasetul final Enrollment conține:

```text
2.432 rânduri
6 coloane
42 județe
9 ani analitici
7 niveluri educaționale formale
```

Auditul a confirmat:

```text
toate coloanele necesare sunt prezente
valori lipsă = 0
duplicate pe cheia analitică = 0
42 județe în fiecare an analitic
valori negative = 0
```

A fost confirmat setul așteptat de niveluri:

```text
Antepreşcolar
Preșcolar
Primar
Gimnazial
Profesional
Liceal
Postliceal
```

A fost validată și relația temporală:

```text
analysis_year
=
anul de început al school_year
```

Exemple:

```text
2015-2016 → 2015
2023-2024 → 2023
```

Maparea:

```text
county_code → county_abbr
```

este consistentă intern.

---

## Step 44 — Validate Baccalaureate in the final audit

### English

The final Baccalaureate dataset contains:

```text
378 rows
14 columns
42 counties
9 years
2015–2023
```

The final audit confirmed:

```text
required columns present
missing values = 0
duplicate County × Year keys = 0
42 counties in every year
negative analytical counts = 0
```

The following accounting relationships passed:

```text
candidates
=
passed
+
failed
+
absent
+
eliminated
```

and:

```text
present
=
passed
+
failed
+
eliminated
```

The pass-rate formula also passed:

```text
pass_rate
=
passed_candidates
/
present_candidates
```

The first validation of `average_grade` used an unnecessarily strict floating-point tolerance.

This produced apparent mismatches even though the underlying calculation was correct.

A diagnostic comparison found the maximum absolute difference to be approximately:

```text
0.0000495
```

The validation was updated to allow normal numerical / stored-value rounding tolerance.

The final relationship passed:

```text
average_grade
≈
final_grade_sum
/
graded_candidates
```

The average grade remained within the valid range:

```text
1–10
```

### Română

Datasetul final Baccalaureate conține:

```text
378 rânduri
14 coloane
42 județe
9 ani
2015–2023
```

Auditul final a confirmat:

```text
toate coloanele necesare sunt prezente
valori lipsă = 0
duplicate Județ × An = 0
42 județe în fiecare an
valori analitice negative = 0
```

Au trecut următoarele relații contabile:

```text
candidates
=
passed
+
failed
+
absent
+
eliminated
```

și:

```text
present
=
passed
+
failed
+
eliminated
```

A trecut și formula ratei de promovare:

```text
pass_rate
=
passed_candidates
/
present_candidates
```

Prima validare a câmpului `average_grade` utiliza o toleranță floating-point inutil de strictă.

Aceasta producea diferențe aparente, deși calculul de bază era corect.

Diagnosticul a identificat o diferență absolută maximă de aproximativ:

```text
0,0000495
```

Validarea a fost actualizată pentru a permite toleranța normală asociată preciziei numerice și valorilor stocate.

Relația finală a trecut:

```text
average_grade
≈
final_grade_sum
/
graded_candidates
```

Media a rămas în intervalul valid:

```text
1–10
```

---

## Step 45 — Validate cross-dataset geographical consistency

### English

The three processed datasets were compared using the common geographical key.

The final audit confirmed:

```text
Employment
Enrollment
Baccalaureate
```

all use exactly the same:

```text
42 county codes
```

Employment and Baccalaureate use consistent county names.

Enrollment and Baccalaureate use consistent county abbreviations.

The common analytical geographical key is therefore:

```text
county_code
=
Romanian NUTS 3 county-level code
```

This provides the basis for the future `DimCounty` dimension.

### Română

Cele trei dataseturi procesate au fost comparate folosind cheia geografică comună.

Auditul final a confirmat că:

```text
Employment
Enrollment
Baccalaureate
```

utilizează exact aceleași:

```text
42 coduri județene
```

Employment și Baccalaureate utilizează denumiri consistente ale județelor.

Enrollment și Baccalaureate utilizează abrevieri consistente ale județelor.

Cheia geografică analitică comună este astfel:

```text
county_code
=
cod județean românesc NUTS 3
```

Aceasta va reprezenta baza viitoarei dimensiuni `DimCounty`.

---

## Step 46 — Final validation result

### English

The final processed-data audit completed with:

```text
Errors: 0
Warnings: 0

FINAL STATUS: PASS
```

All three processed datasets passed the final structural and analytical validation.

Final production datasets:

```text
Employment
data/processed/employment_clean.csv
420 rows × 5 columns

Enrollment
data/processed/enrollment_clean.csv
2,432 rows × 6 columns

Baccalaureate
data/processed/baccalaureate_clean.csv
378 rows × 14 columns
```

The processed-data layer is therefore ready for Power BI modelling.

### Română

Auditul final al stratului de date procesate s-a încheiat cu:

```text
Errors: 0
Warnings: 0

FINAL STATUS: PASS
```

Toate cele trei dataseturi procesate au trecut validarea structurală și analitică finală.

Dataseturile finale de producție sunt:

```text
Employment
data/processed/employment_clean.csv
420 rânduri × 5 coloane

Enrollment
data/processed/enrollment_clean.csv
2.432 rânduri × 6 coloane

Baccalaureate
data/processed/baccalaureate_clean.csv
378 rânduri × 14 coloane
```

Stratul de date procesate este astfel pregătit pentru modelarea în Power BI.

---

# Analytical Scope and Temporal Alignment

## English

The current project combines three related but conceptually distinct statistical components:

```text
Pre-university enrollment
Baccalaureate outcomes
Employment
```

The common geographical unit is:

```text
Romanian county / NUTS 3
```

The common comparison period is primarily:

```text
2015–2023
```

However, the underlying temporal concepts are not identical.

Employment uses:

```text
calendar year
2014–2023
```

Enrollment uses:

```text
school year
2015-2016 → 2023-2024
```

with:

```text
analysis_year
=
school-year starting year
```

Baccalaureate uses:

```text
calendar examination year
2015–2023
```

Therefore, comparisons involving Enrollment must be interpreted as aligned analytical periods rather than perfectly identical temporal measurements.

The project should not infer causality from simple cross-dataset correlations.

Associations observed between education and employment indicators must be interpreted descriptively unless a separate causal design is introduced.

### Română

Proiectul actual combină trei componente statistice corelate, dar conceptual distincte:

```text
înscriere în învățământul preuniversitar
rezultate la Bacalaureat
ocupare
```

Unitatea geografică comună este:

```text
județul din România / NUTS 3
```

Perioada comună principală de comparație este:

```text
2015–2023
```

Totuși, conceptele temporale de bază nu sunt identice.

Employment utilizează:

```text
an calendaristic
2014–2023
```

Enrollment utilizează:

```text
an școlar
2015-2016 → 2023-2024
```

cu:

```text
analysis_year
=
anul de început al anului școlar
```

Baccalaureate utilizează:

```text
anul calendaristic al examenului
2015–2023
```

Prin urmare, comparațiile care implică Enrollment trebuie interpretate ca perioade analitice aliniate și nu ca măsurători temporale perfect identice.

Proiectul nu trebuie să interpreteze drept cauzalitate corelațiile simple dintre dataseturi.

Asocierile observate între indicatorii educaționali și cei privind ocuparea trebuie interpretate descriptiv, în absența unui design cauzal separat.

---

# Planned Power BI Dimensional Model

## English

The processed-data layer is designed for a star-schema-style Power BI model.

Planned dimensions:

```text
DimCounty
DimYear
DimEducationLevel
```

Planned fact tables:

```text
FactEmployment
FactEnrollment
FactBaccalaureate
```

Conceptual structure:

```text
                    DimCounty
                        |
            -------------------------
            |           |           |
            |           |           |
   FactEmployment  FactEnrollment  FactBaccalaureate
            |           |           |
            -------------------------
                        |
                     DimYear


DimEducationLevel
        |
FactEnrollment
```

`DimCounty` will centralize geographical attributes such as:

```text
county_code
county
county_abbr
```

`DimYear` will provide the shared analytical year axis.

`DimEducationLevel` will contain the seven formal Enrollment categories.

The fact tables will retain their own analytical measures while descriptive attributes are moved to dimensions where appropriate.

### Română

Stratul de date procesate este pregătit pentru un model Power BI de tip star schema.

Dimensiunile planificate sunt:

```text
DimCounty
DimYear
DimEducationLevel
```

Fact table-urile planificate sunt:

```text
FactEmployment
FactEnrollment
FactBaccalaureate
```

Structura conceptuală:

```text
                    DimCounty
                        |
            -------------------------
            |           |           |
            |           |           |
   FactEmployment  FactEnrollment  FactBaccalaureate
            |           |           |
            -------------------------
                        |
                     DimYear


DimEducationLevel
        |
FactEnrollment
```

`DimCounty` va centraliza atribute geografice precum:

```text
county_code
county
county_abbr
```

`DimYear` va furniza axa comună a anului analitic.

`DimEducationLevel` va conține cele șapte categorii formale din Enrollment.

Fact table-urile vor păstra măsurile analitice proprii, iar atributele descriptive vor fi mutate în dimensiuni acolo unde este potrivit.

---

# Power BI Aggregation Rules

## English

Some pre-calculated row-level indicators must not be averaged directly in Power BI.

For Baccalaureate, the correct overall pass rate is:

```text
SUM(passed_candidates)
/
SUM(present_candidates)
```

and not:

```text
AVERAGE(pass_rate)
```

Similarly, the correct overall average grade is:

```text
SUM(final_grade_sum)
/
SUM(graded_candidates)
```

and not:

```text
AVERAGE(average_grade)
```

This ensures that county-level and multi-year selections are weighted by their actual candidate populations.

### Română

Anumiți indicatori precalculați la nivel de rând nu trebuie mediați direct în Power BI.

Pentru Bacalaureat, rata corectă de promovare agregată este:

```text
SUM(passed_candidates)
/
SUM(present_candidates)
```

și nu:

```text
AVERAGE(pass_rate)
```

În mod similar, media generală corectă este:

```text
SUM(final_grade_sum)
/
SUM(graded_candidates)
```

și nu:

```text
AVERAGE(average_grade)
```

Astfel, selecțiile care includ mai multe județe sau ani sunt ponderate în funcție de populațiile reale de candidați.

---

# Project Status Before Power BI Stage

## English

Three major production data pipelines are complete and validated.

### Employment

```text
Eurostat API
→ Raw JSON
→ JSON-stat parsing
→ NUTS 3 filtering
→ Transformation
→ Validation
→ employment_clean.csv

✅ COMPLETE
```

### Enrollment

```text
data.gov.ro
→ CKAN discovery
→ Official Excel resources
→ Raw preservation
→ Schema diagnosis
→ Multi-year transformation
→ Validation
→ enrollment_clean.csv

✅ COMPLETE
```

### Baccalaureate

```text
Official annual files
→ Format diagnosis
→ Cross-year normalization
→ Candidate validation
→ SIIIR county mapping
→ Result normalization
→ Candidate-level standardized layer
→ County × Year aggregation
→ Validation
→ baccalaureate_clean.csv

✅ COMPLETE
```

### Higher Education

```text
INS TEMPO investigation
+
data.gov.ro / ANS investigation
+
robust API retry

⏸ DEFERRED
```

Reason:

```text
No sufficiently reproducible County × Year source
was available through the tested programmatic routes.
```

The component remains a future extension.

### Final processed-data validation

```text
48_validate_processed_datasets.py

Errors: 0
Warnings: 0

FINAL STATUS: PASS
```

The next project stage is:

```text
Power BI dimensional modelling
        ↓
DAX measures
        ↓
Dashboard development
        ↓
Final documentation
        ↓
GitHub cleanup and publication
```

## Română

Trei pipeline-uri principale de producție sunt finalizate și validate.

### Employment

```text
Eurostat API
→ JSON raw
→ Parsare JSON-stat
→ Filtrare NUTS 3
→ Transformare
→ Validare
→ employment_clean.csv

✅ COMPLET
```

### Enrollment

```text
data.gov.ro
→ Descoperire CKAN
→ Resurse Excel oficiale
→ Păstrarea datelor raw
→ Diagnosticarea schemelor
→ Transformare multi-an
→ Validare
→ enrollment_clean.csv

✅ COMPLET
```

### Baccalaureate

```text
Fișiere oficiale anuale
→ Diagnosticarea formatelor
→ Normalizare între ani
→ Validarea candidaților
→ Mapare SIIIR la județ
→ Normalizarea rezultatelor
→ Strat standardizat la nivel de candidat
→ Agregare Județ × An
→ Validare
→ baccalaureate_clean.csv

✅ COMPLET
```

### Higher Education

```text
Investigație INS TEMPO
+
investigație data.gov.ro / ANS
+
retry robust API

⏸ AMÂNAT
```

Motiv:

```text
Prin rutele programatice testate nu a fost disponibilă
o sursă Județ × An suficient de reproductibilă.
```

Componenta rămâne o extensie viitoare.

### Validarea finală a datelor procesate

```text
48_validate_processed_datasets.py

Errors: 0
Warnings: 0

FINAL STATUS: PASS
```

Următoarea etapă a proiectului este:

```text
Modelare dimensională Power BI
        ↓
Măsuri DAX
        ↓
Dezvoltarea dashboardului
        ↓
Documentație finală
        ↓
Curățare și publicare GitHub
```

---

# Project Structure Before Power BI Stage

```text
romania_education_employment/
│
├── data/
│   │
│   ├── raw/
│   │   │
│   │   ├── eurostat_employment_2014_2023_raw.json
│   │   │
│   │   ├── enrollment/
│   │   │   ├── enrollment_2015_2016_raw.xlsx
│   │   │   ├── enrollment_2016_2017_raw.xlsx
│   │   │   ├── enrollment_2017_2018_raw.xlsx
│   │   │   ├── enrollment_2018_2019_raw.xlsx
│   │   │   ├── enrollment_2019_2020_raw.xlsx
│   │   │   ├── enrollment_2020_2021_raw.xlsx
│   │   │   ├── enrollment_2021_2022_raw.xlsx
│   │   │   ├── enrollment_2022_2023_raw.xlsx
│   │   │   └── enrollment_2023_2024_raw.xlsx
│   │   │
│   │   ├── baccalaureate/
│   │   │   └── official annual Session I source files
│   │   │
│   │   └── higher_education/
│   │       └── investigated ANS / Higher Education source files
│   │
│   ├── interim/
│   │   └── baccalaureate_candidate_standardized.csv
│   │
│   └── processed/
│       ├── employment_clean.csv
│       ├── enrollment_clean.csv
│       └── baccalaureate_clean.csv
│
├── docs/
│   └── development_log.md
│
├── powerbi/
│
└── src/
    ├── Employment pipeline scripts
    ├── Enrollment pipeline scripts
    ├── Baccalaureate pipeline scripts
    ├── 44_inspect_higher_education_scl103d.py
    ├── 45_inventory_datagov_higher_education.py
    ├── 46_ingest_and_inspect_higher_education_licenta.py
    ├── 47_retry_ins_scl103d_robust.py
    └── 48_validate_processed_datasets.py
```

The candidate-level Baccalaureate intermediate file must remain excluded from the public repository.

The final GitHub cleanup should ensure that:

```text
data/interim/
```

is excluded through `.gitignore`.

Raw files should also be reviewed before publication based on source licensing, size, reproducibility, and privacy requirements.

---

# Development Progress Summary — Before Power BI

```text
PROJECT STRUCTURE                         ✅


EMPLOYMENT

Source identification                    ✅
API connectivity                         ✅
Raw data ingestion                       ✅
Raw data preservation                    ✅
JSON-stat parsing                        ✅
NUTS 3 filtering                         ✅
Transformation                           ✅
Data quality validation                  ✅
Processed dataset                        ✅


ENROLLMENT

Source identification                    ✅
CKAN API discovery                       ✅
Raw file ingestion                       ✅
Multi-year ingestion                     ✅
Workbook inspection                      ✅
Cross-year schema comparison             ✅
Header detection                         ✅
Measure investigation                    ✅
Aggregate-row diagnosis                  ✅
Duplicate investigation                  ✅
NUTS 3 standardization                   ✅
Multi-year transformation                ✅
Data quality validation                  ✅
Processed dataset                        ✅


BACCALAUREATE

Source identification                    ✅
Annual source inventory                  ✅
Cross-year format inspection             ✅
Malformed-source diagnosis               ✅
ODS fallback validation                  ✅
Candidate uniqueness validation          ✅
SIIIR investigation                      ✅
Leading-zero normalization               ✅
County mapping                           ✅
Result-status profiling                  ✅
Final-grade normalization                ✅
Candidate-level standardization          ✅
County × Year aggregation                ✅
Data quality validation                  ✅
Processed dataset                        ✅


HIGHER EDUCATION

INS TEMPO investigation                  ✅
data.gov.ro / ANS investigation          ✅
ANS workbook inspection                  ✅
Geographical suitability assessment      ✅
Robust INS API retry                     ✅
Production integration                   ⏸ DEFERRED


FINAL PROCESSED DATA AUDIT

Employment final validation              ✅
Enrollment final validation              ✅
Baccalaureate final validation           ✅
Cross-dataset county validation          ✅
Final audit status                       ✅ PASS


FINAL DIMENSIONAL MODEL                   ⏳
POWER BI                                 ⏳
DAX                                      ⏳
DASHBOARD                                ⏳
FINAL DOCUMENTATION                      ⏳
GITHUB CLEANUP                           ⏳
```

---

# Processed Data Baseline Before Power BI

```text
Employment
Period: 2014–2023
Grain: County × Year
Rows: 420
Counties: 42


Enrollment
Period: 2015-2016 → 2023-2024
Analysis years: 2015–2023
Grain: County × School Year × Education Level
Rows: 2,432
Counties: 42
Formal education levels: 7


Baccalaureate
Period: 2015–2023
Session: Session I
Grain: County × Year
Rows: 378
Counties: 42


Common geographical key:
county_code


Main common analytical period:
2015–2023


Processed-data validation:
Errors: 0
Warnings: 0
FINAL STATUS: PASS
```

The project is now ready to move from the data-engineering / preprocessing stage to the Power BI dimensional modelling stage.

---

# Power BI Dimensional Modelling and Dashboard Development

## Step 47 — Import the validated production datasets into Power BI

### English

After completion of the Python preprocessing and validation pipelines, the three validated production datasets were imported into Power BI:

```text
data/processed/employment_clean.csv
data/processed/enrollment_clean.csv
data/processed/baccalaureate_clean.csv
```

Only the validated processed datasets were used as analytical fact sources.

Raw and interim files were not used directly by the Power BI report.

The three analytical domains imported into the semantic model are:

```text
Employment
Enrollment
Baccalaureate
```

Their main analytical periods are:

```text
Employment:
2014–2023

Enrollment:
school years 2015-2016 → 2023-2024
analysis years 2015–2023

Baccalaureate:
2015–2023
Session I
```

The primary common comparison period across the three analytical domains is:

```text
2015–2023
```

Employment additionally preserves 2014 for its dedicated long-term trend analysis.

### Română

După finalizarea pipeline-urilor Python de preprocesare și validare, cele trei dataseturi de producție validate au fost importate în Power BI:

```text
data/processed/employment_clean.csv
data/processed/enrollment_clean.csv
data/processed/baccalaureate_clean.csv
```

În modelul analitic au fost utilizate exclusiv dataseturile procesate și validate.

Fișierele raw și interim nu sunt utilizate direct de raportul Power BI.

Cele trei domenii analitice integrate în model sunt:

```text
Employment
Enrollment
Baccalaureate
```

Perioadele principale sunt:

```text
Employment:
2014–2023

Enrollment:
ani școlari 2015-2016 → 2023-2024
ani analitici 2015–2023

Baccalaureate:
2015–2023
Sesiunea I
```

Perioada principală comună pentru comparații între cele trei domenii este:

```text
2015–2023
```

Employment păstrează suplimentar anul 2014 pentru analiza longitudinală dedicată.

---

## Step 48 — Build the dimensional semantic model

### English

A dimensional semantic model was created around three fact tables:

```text
FactEmployment
FactEnrollment
FactBaccalaureate
```

and three dimensions:

```text
DimCounty
DimYear
DimEducationLevel
```

The resulting architecture is a:

```text
Fact constellation / galaxy schema
```

because multiple fact tables share common dimensions.

`DimCounty` and `DimYear` are shared across the three analytical domains.

`DimEducationLevel` is related only to `FactEnrollment`, because education level is part of the Enrollment analytical grain.

The common geographical key is:

```text
county_code
```

representing the Romanian NUTS 3 county-level identifier.

The final relationships are:

```text
FactBaccalaureate[county_code]
    * → 1
DimCounty[county_code]

FactBaccalaureate[year]
    * → 1
DimYear[year]


FactEmployment[county_code]
    * → 1
DimCounty[county_code]

FactEmployment[year]
    * → 1
DimYear[year]


FactEnrollment[county_code]
    * → 1
DimCounty[county_code]

FactEnrollment[analysis_year]
    * → 1
DimYear[year]

FactEnrollment[education_level]
    * → 1
DimEducationLevel[education_level]
```

The Enrollment time relationship intentionally uses:

```text
FactEnrollment[analysis_year]
→
DimYear[year]
```

where:

```text
analysis_year
=
starting year of school_year
```

For example:

```text
2022-2023
→
analysis_year = 2022
```

This convention enables analytical alignment with annual Employment and Baccalaureate data while preserving the original `school_year` field in the source dataset.

All seven relationships use:

```text
Many-to-one (*:1)
Active relationship
Single cross-filter direction
Dimension → Fact
```

The model contains:

```text
0 many-to-many relationships
0 bidirectional relationships
0 direct Fact-to-Fact relationships
```

### Română

A fost construit un model semantic dimensional format din trei tabele fact:

```text
FactEmployment
FactEnrollment
FactBaccalaureate
```

și trei dimensiuni:

```text
DimCounty
DimYear
DimEducationLevel
```

Arhitectura rezultată este de tip:

```text
Fact constellation / galaxy schema
```

deoarece mai multe tabele fact utilizează dimensiuni comune.

`DimCounty` și `DimYear` sunt utilizate de toate cele trei domenii analitice.

`DimEducationLevel` este asociată exclusiv cu `FactEnrollment`, deoarece nivelul educațional face parte din granularitatea analitică Enrollment.

Cheia geografică comună este:

```text
county_code
```

corespunzătoare identificatorului județean românesc NUTS 3.

Relațiile finale sunt:

```text
FactBaccalaureate[county_code]
    * → 1
DimCounty[county_code]

FactBaccalaureate[year]
    * → 1
DimYear[year]


FactEmployment[county_code]
    * → 1
DimCounty[county_code]

FactEmployment[year]
    * → 1
DimYear[year]


FactEnrollment[county_code]
    * → 1
DimCounty[county_code]

FactEnrollment[analysis_year]
    * → 1
DimYear[year]

FactEnrollment[education_level]
    * → 1
DimEducationLevel[education_level]
```

Pentru Enrollment este utilizată intenționat relația:

```text
FactEnrollment[analysis_year]
→
DimYear[year]
```

unde:

```text
analysis_year
=
anul de început al school_year
```

Exemplu:

```text
2022-2023
→
analysis_year = 2022
```

Această convenție permite alinierea analitică cu datele anuale Employment și Baccalaureate, păstrând în același timp câmpul original `school_year`.

Toate cele șapte relații utilizează:

```text
Many-to-one (*:1)
Relație activă
Single cross-filter direction
Dimension → Fact
```

Modelul conține:

```text
0 relații many-to-many
0 relații bidirecționale
0 relații directe Fact-to-Fact
```

---

## Step 49 — Create the main DAX measures

### English

Explicit DAX measures were created for the main analytical indicators.

Using explicit measures provides controlled aggregation logic and avoids relying on implicit Power BI aggregations.

### Employment measures

The final visible Employment measures include:

```text
Total Employees
Employees 2023
Employment Change 2014-2023 %
Employment Change 2015-2023 %
Employment Change 2022-2023 %
```

The base aggregation is:

```DAX
Total Employees =
SUM(FactEmployment[employees])
```

The change measures compare the relevant beginning and ending values using the current county filter context when applicable.

### Enrollment measures

The final visible Enrollment measures include:

```text
Total Enrolled Students
Enrolled Students 2023
Enrollment Change 2015-2023
Enrollment Change 2015-2023 %
Enrollment Change 2022-2023 %
```

The base aggregation is:

```DAX
Total Enrolled Students =
SUM(FactEnrollment[enrolled_students])
```

The absolute Enrollment change measure is retained because it is useful for comparing education levels expressed as numbers of students.

### Baccalaureate measures

The final visible Baccalaureate measures include:

```text
Total Candidates
Candidates 2023
Pass Rate
Pass Rate 2023
Average Grade
Average Grade 2023
Absence Rate
Absence Rate 2023
County Pass Rate Gap 2023 (pp)
```

The Baccalaureate percentage and average measures use weighted aggregation logic.

The correct aggregated pass rate is:

```text
SUM(passed_candidates)
/
SUM(present_candidates)
```

rather than:

```text
AVERAGE(pass_rate)
```

The correct aggregated average grade is:

```text
SUM(final_grade_sum)
/
SUM(graded_candidates)
```

rather than:

```text
AVERAGE(average_grade)
```

This prevents small counties from receiving the same analytical weight as counties with much larger candidate populations.

### Română

Au fost create măsuri DAX explicite pentru principalii indicatori analitici.

Utilizarea măsurilor explicite permite controlul logicii de agregare și evită dependența de agregările implicite Power BI.

### Măsuri Employment

Măsurile finale vizibile includ:

```text
Total Employees
Employees 2023
Employment Change 2014-2023 %
Employment Change 2015-2023 %
Employment Change 2022-2023 %
```

Agregarea de bază este:

```DAX
Total Employees =
SUM(FactEmployment[employees])
```

Măsurile de variație compară valorile relevante de început și de final și respectă contextul de filtrare pentru județ atunci când acesta este selectat.

### Măsuri Enrollment

Măsurile finale vizibile includ:

```text
Total Enrolled Students
Enrolled Students 2023
Enrollment Change 2015-2023
Enrollment Change 2015-2023 %
Enrollment Change 2022-2023 %
```

Agregarea de bază este:

```DAX
Total Enrolled Students =
SUM(FactEnrollment[enrolled_students])
```

Măsura de variație absolută este păstrată deoarece permite compararea nivelurilor educaționale în număr de elevi.

### Măsuri Baccalaureate

Măsurile finale vizibile includ:

```text
Total Candidates
Candidates 2023
Pass Rate
Pass Rate 2023
Average Grade
Average Grade 2023
Absence Rate
Absence Rate 2023
County Pass Rate Gap 2023 (pp)
```

Indicatorii procentuali și media pentru Bacalaureat utilizează agregări ponderate.

Rata corectă de promovare agregată este:

```text
SUM(passed_candidates)
/
SUM(present_candidates)
```

și nu:

```text
AVERAGE(pass_rate)
```

Media corectă este:

```text
SUM(final_grade_sum)
/
SUM(graded_candidates)
```

și nu:

```text
AVERAGE(average_grade)
```

Astfel este evitată acordarea aceleiași ponderi analitice județelor cu populații foarte diferite de candidați.

---

## Step 50 — Standardize numeric display units

### English

Display units were standardized across Power BI cards, charts, and axes.

Large national totals are displayed using compact units such as:

```text
M = millions
K = thousands
```

Examples:

```text
6,625,410 employees
→
6.63M

130,522 Baccalaureate candidates
→
130.52K
```

A specific formatting issue was identified for Enrollment.

National Enrollment totals are approximately:

```text
3 million students
```

while county totals are generally:

```text
tens or hundreds of thousands
```

Using one fixed display unit produced undesirable representations such as:

```text
3000K
```

at national level or:

```text
0.095M
```

at county level.

A dynamic format string was therefore applied to:

```text
Total Enrolled Students
```

so the same numeric measure can display:

```text
National context
2,951,062
→
approximately 2.95M

County context
62,079
→
approximately 62K
```

The measure remains numeric and continues to work correctly in charts, cards, filtering, and aggregation.

### Română

Unitățile numerice de afișare au fost standardizate pentru carduri, grafice și axe.

Valorile naționale mari sunt afișate compact folosind:

```text
M = milioane
K = mii
```

Exemple:

```text
6.625.410 angajați
→
6,63M

130.522 candidați la Bacalaureat
→
130,52K
```

Pentru Enrollment a fost identificată o problemă specifică de formatare.

Totalurile naționale sunt de aproximativ:

```text
3 milioane de elevi
```

iar valorile județene sunt de regulă:

```text
zeci sau sute de mii
```

O unitate fixă producea reprezentări precum:

```text
3000K
```

la nivel național sau:

```text
0.095M
```

la nivel județean.

Pentru:

```text
Total Enrolled Students
```

a fost implementat un dynamic format string.

Aceeași măsură numerică poate fi astfel afișată:

```text
Context național
2.951.062
→
aproximativ 2,95M

Context județean
62.079
→
aproximativ 62K
```

Măsura rămâne numerică și funcționează în continuare corect pentru grafice, carduri, filtrare și agregare.

---

## Step 51 — Build the Executive Overview page

### English

The first report page was created as:

```text
Executive Overview
```

with the main title:

```text
Education & Employment in Romania
```

The page provides a high-level overview of the three analytical domains.

The main slicers are:

```text
Year
County
```

The principal KPI cards are:

```text
Total Employees
Total Enrolled Students
Total Candidates
Pass Rate
Average Grade
```

The main visuals are:

```text
Enrollment by Education Level

Top 10 Counties by Employment

Top 10 Counties by Baccalaureate Pass Rate
```

The page is designed primarily for a selected analytical year.

The final default year is:

```text
2023
```

Selecting a county updates the KPI cards and relevant visuals to provide a county-specific analytical view.

### Română

Prima pagină a raportului este:

```text
Executive Overview
```

cu titlul principal:

```text
Education & Employment in Romania
```

Pagina oferă o perspectivă generală asupra celor trei domenii analitice.

Slicerele principale sunt:

```text
Year
County
```

Cardurile KPI sunt:

```text
Total Employees
Total Enrolled Students
Total Candidates
Pass Rate
Average Grade
```

Vizualurile principale sunt:

```text
Enrollment by Education Level

Top 10 Counties by Employment

Top 10 Counties by Baccalaureate Pass Rate
```

Pagina este proiectată în principal pentru analiza unui singur an.

Anul implicit final este:

```text
2023
```

Selectarea unui județ actualizează cardurile KPI și vizualurile relevante pentru analiza județeană.

---

## Step 52 — Build the Employment Analysis page

### English

A dedicated Employment page was created:

```text
Employment Analysis
Romanian Counties | 2014–2023
```

The page contains a County slicer.

The main KPI cards are:

```text
Employment Change 2014-2023 %
Employment Change 2022-2023 %
Employees 2023
```

The main trend visual is:

```text
Employment Trend, 2014–2023
```

Two county-ranking visuals were added:

```text
Top 10 Counties by Employment Growth, 2014–2023

Bottom 10 Counties by Employment Change, 2014–2023
```

The County slicer also allows the long-term trajectory of an individual county to be inspected.

For example, selecting one county recalculates:

```text
long-term employment change
recent employment change
2023 employment level
employment trend
```

### Română

A fost creată pagina dedicată:

```text
Employment Analysis
Romanian Counties | 2014–2023
```

Pagina conține un slicer pentru județ.

Cardurile KPI principale sunt:

```text
Employment Change 2014-2023 %
Employment Change 2022-2023 %
Employees 2023
```

Graficul principal de evoluție este:

```text
Employment Trend, 2014–2023
```

Au fost adăugate două clasamente județene:

```text
Top 10 Counties by Employment Growth, 2014–2023

Bottom 10 Counties by Employment Change, 2014–2023
```

Slicerul pentru județ permite și analiza traiectoriei unui singur județ.

Selectarea unui județ recalculează:

```text
variația Employment pe termen lung
variația recentă
nivelul Employment în 2023
trendul Employment
```

---

## Step 53 — Build the Enrollment Analysis page

### English

The Enrollment page was created as:

```text
Enrollment Analysis
Romanian Counties | 2015–2023
```

The page contains two slicers:

```text
County
Education Level
```

The main KPI cards are:

```text
Enrolled Students 2023
Enrollment Change 2015-2023 %
Enrollment Change 2022-2023 %
```

The main time-series visual is:

```text
Enrollment Trend, 2015–2023
```

The page also contains:

```text
Enrollment Change by Education Level, 2015–2023

Top 10 Counties by Enrolled Students, 2023
```

The education-level change visual uses absolute student-count differences rather than only percentages.

This makes the magnitude of structural changes directly interpretable.

The County slicer allows the same indicators to be recalculated for individual counties.

The dynamic formatting of `Total Enrolled Students` ensures that national values are displayed in millions while county-level values are displayed in thousands where appropriate.

### Română

Pagina Enrollment a fost creată astfel:

```text
Enrollment Analysis
Romanian Counties | 2015–2023
```

Pagina conține două slicere:

```text
County
Education Level
```

Cardurile KPI sunt:

```text
Enrolled Students 2023
Enrollment Change 2015-2023 %
Enrollment Change 2022-2023 %
```

Graficul principal este:

```text
Enrollment Trend, 2015–2023
```

Pagina include și:

```text
Enrollment Change by Education Level, 2015–2023

Top 10 Counties by Enrolled Students, 2023
```

Graficul privind schimbarea pe nivel educațional utilizează diferența absolută în numărul de elevi, nu doar procente.

Astfel, magnitudinea schimbărilor structurale este direct interpretabilă.

Slicerul County permite recalcularea acelorași indicatori pentru fiecare județ.

Formatarea dinamică pentru `Total Enrolled Students` afișează valorile naționale în milioane și valorile județene în mii atunci când este necesar.

---

## Step 54 — Build the Baccalaureate Analysis page

### English

The Baccalaureate page was created as:

```text
Baccalaureate Analysis
Romanian Counties | 2015–2023 | Session I
```

The page contains a County slicer.

The main KPI cards are:

```text
Candidates 2023
Pass Rate 2023
Average Grade 2023
Absence Rate 2023
```

The main trend visuals are:

```text
Pass Rate Trend, 2015–2023

Average Grade Trend, 2015–2023
```

A ranking visual was created for:

```text
Bottom 10 Counties by Pass Rate, 2023
```

A scatter plot was also added:

```text
Candidates vs Pass Rate by County, 2023
```

with:

```text
X-axis = Candidates 2023
Y-axis = Pass Rate 2023
County = analytical detail
```

The scatter plot provides a descriptive view of whether counties with larger candidate populations systematically display different Baccalaureate outcomes.

No causal interpretation is inferred from this visual.

Selecting a county updates the county-specific KPI cards and trend charts.

### Română

Pagina pentru Bacalaureat a fost creată astfel:

```text
Baccalaureate Analysis
Romanian Counties | 2015–2023 | Session I
```

Pagina conține un slicer pentru județ.

Cardurile KPI sunt:

```text
Candidates 2023
Pass Rate 2023
Average Grade 2023
Absence Rate 2023
```

Graficele principale de trend sunt:

```text
Pass Rate Trend, 2015–2023

Average Grade Trend, 2015–2023
```

A fost creat și clasamentul:

```text
Bottom 10 Counties by Pass Rate, 2023
```

precum și scatter plot-ul:

```text
Candidates vs Pass Rate by County, 2023
```

cu:

```text
X-axis = Candidates 2023
Y-axis = Pass Rate 2023
County = detaliu analitic
```

Scatter plot-ul oferă o perspectivă descriptivă asupra relației dintre dimensiunea populației de candidați și rata de promovare.

Graficul nu este interpretat cauzal.

Selectarea unui județ actualizează KPI-urile și trendurile specifice județului.

---

## Step 55 — Build the County Comparison page

### English

A cross-domain comparison page was created:

```text
County Comparison
Employment, Enrollment &
Baccalaureate | 2015–2023
```

The page contains:

```text
Year slicer
County slicer
```

The Year slicer uses the common analytical period:

```text
2015–2023
```

and is intended primarily for single-year comparison.

The main KPI cards are:

```text
Total Employees
Total Enrolled Students
Total Candidates
Pass Rate
```

Three analytical comparison elements were added.

### Employment vs Enrollment by County

Scatter plot:

```text
X-axis = Total Enrolled Students
Y-axis = Total Employees
County = analytical detail
```

This visual shows the strong size effect between county population/activity scale and the two indicators.

### County Metrics Comparison

A detailed table was created containing:

```text
county
Total Employees
Total Enrolled Students
Total Candidates
Pass Rate
Average Grade
```

The table enables direct cross-domain comparison for each county.

### Employment vs Pass Rate by County

Scatter plot:

```text
X-axis = Total Employees
Y-axis = Pass Rate
County = analytical detail
```

This visual shows that counties with comparable Employment levels can still display substantially different Baccalaureate pass rates.

When one county is selected, KPI cards and the metrics table are filtered to that county.

The cross-county scatter plots remain useful as contextual distributions for interpreting the selected county relative to the national county structure.

### Română

A fost creată pagina cross-domain:

```text
County Comparison
Employment, Enrollment &
Baccalaureate | 2015–2023
```

Pagina conține:

```text
Year slicer
County slicer
```

Slicerul pentru an utilizează perioada comună:

```text
2015–2023
```

și este utilizat în principal pentru comparații într-un singur an.

Cardurile KPI sunt:

```text
Total Employees
Total Enrolled Students
Total Candidates
Pass Rate
```

Au fost create trei componente comparative.

### Employment vs Enrollment by County

Scatter plot:

```text
X-axis = Total Enrolled Students
Y-axis = Total Employees
County = detaliu analitic
```

Graficul evidențiază efectul puternic al dimensiunii județului asupra celor doi indicatori.

### County Metrics Comparison

A fost creat un tabel cu:

```text
county
Total Employees
Total Enrolled Students
Total Candidates
Pass Rate
Average Grade
```

Tabelul permite compararea directă a principalilor indicatori pentru fiecare județ.

### Employment vs Pass Rate by County

Scatter plot:

```text
X-axis = Total Employees
Y-axis = Pass Rate
County = detaliu analitic
```

Graficul arată că județe cu niveluri similare de Employment pot avea rate de promovare la Bacalaureat substanțial diferite.

Atunci când este selectat un județ, cardurile KPI și tabelul sunt filtrate pentru județul respectiv.

Scatter plot-urile cross-county păstrează contextul distribuției județene și permit interpretarea județului selectat în raport cu structura națională.

---

## Step 56 — Build the Key Findings page

### English

A final analytical summary page was created:

```text
Key Findings
Education & Employment in Romania | 2015–2023
```

Unlike the exploratory pages, this page contains fixed analytical conclusions rather than interactive slicers.

Four principal findings were selected.

### Employment growth

Employment increased from approximately:

```text
6.17M in 2015
```

to:

```text
6.63M in 2023
```

corresponding to:

```text
+7.43%
```

However, Employment declined by approximately:

```text
-0.95%
```

between 2022 and 2023.

### Enrollment change

Total Enrollment declined from approximately:

```text
3.01M in 2015
```

to:

```text
2.95M in 2023
```

corresponding to:

```text
-1.81%
```

The change was not uniform across education levels.

Between 2015 and 2023:

```text
Liceal
≈ -47.9K students

Profesional
≈ +26.7K students
```

### Baccalaureate recovery

The national Baccalaureate pass rate reached:

```text
74.99%
```

in 2023.

This was:

```text
+10.45 percentage points
```

above the 2020 low of:

```text
64.54%
```

and:

```text
+7.17 percentage points
```

above the 2015 value.

### Regional disparities

County pass rates in 2023 ranged from:

```text
51.84% — Ilfov
```

to:

```text
84.68% — Brăila
```

creating a gap of:

```text
32.84 percentage points
```

The page also contains the cross-domain interpretation:

```text
County size and employment levels did not translate directly into stronger
Baccalaureate outcomes.

Counties with similar employment levels showed substantial differences in
pass rates, indicating that the relationship is not one-to-one.
```

This conclusion is descriptive.

The dashboard does not claim that Employment causes Baccalaureate outcomes or vice versa.

### Română

A fost creată pagina finală de sinteză:

```text
Key Findings
Education & Employment in Romania | 2015–2023
```

Spre deosebire de paginile exploratorii, această pagină prezintă concluzii analitice fixe și nu utilizează slicere interactive.

Au fost selectate patru rezultate principale.

### Evoluția Employment

Employment a crescut aproximativ de la:

```text
6,17M în 2015
```

la:

```text
6,63M în 2023
```

corespunzător unei creșteri de:

```text
+7,43%
```

Totuși, între 2022 și 2023 Employment a scăzut cu aproximativ:

```text
-0,95%
```

### Evoluția Enrollment

Enrollment total a scăzut aproximativ de la:

```text
3,01M în 2015
```

la:

```text
2,95M în 2023
```

corespunzător unei variații de:

```text
-1,81%
```

Schimbarea nu a fost uniformă între nivelurile educaționale.

Între 2015 și 2023:

```text
Liceal
≈ -47,9K elevi

Profesional
≈ +26,7K elevi
```

### Evoluția Bacalaureatului

Rata națională de promovare a ajuns la:

```text
74,99%
```

în 2023.

Aceasta este cu:

```text
+10,45 puncte procentuale
```

peste minimul din 2020:

```text
64,54%
```

și cu:

```text
+7,17 puncte procentuale
```

peste valoarea din 2015.

### Disparități regionale

Ratele județene de promovare din 2023 au variat între:

```text
51,84% — Ilfov
```

și:

```text
84,68% — Brăila
```

rezultând un ecart de:

```text
32,84 puncte procentuale
```

Pagina include și interpretarea cross-domain:

```text
Dimensiunea județului și nivelul Employment nu s-au tradus direct
în rezultate mai bune la Bacalaureat.

Județe cu niveluri similare de Employment au prezentat diferențe
substanțiale în ratele de promovare, ceea ce indică faptul că relația
nu este unu-la-unu.
```

Această concluzie este descriptivă.

Dashboardul nu afirmă că Employment determină rezultatele la Bacalaureat sau invers.

---

## Step 57 — Clean the Power BI semantic model

### English

After dashboard development, the semantic model was cleaned to improve usability and presentation quality.

Technical and raw fields that are required internally but are not useful to report users were hidden from the Data pane.

Examples include:

```text
raw fact-table columns
technical county identifiers
intermediate candidate counts
helper aggregation measures
technical temporal fields
```

The final visible dimension fields are primarily:

```text
DimCounty
    county

DimEducationLevel
    education_level

DimYear
    year
```

The fact tables primarily expose business-facing DAX measures.

The underlying hidden columns remain available to the semantic model and continue to support relationships and DAX calculations.

No source data were deleted during this cleanup.

### Română

După dezvoltarea dashboardului, modelul semantic a fost curățat pentru a îmbunătăți utilizarea și prezentarea.

Câmpurile tehnice și raw necesare intern, dar nerelevante pentru utilizatorul raportului, au fost ascunse din Data pane.

Exemple:

```text
coloane raw din fact tables
identificatori tehnici ai județelor
totaluri intermediare pentru candidați
măsuri helper
câmpuri temporale tehnice
```

În dimensiuni au rămas vizibile în principal:

```text
DimCounty
    county

DimEducationLevel
    education_level

DimYear
    year
```

Tabelele fact expun în principal măsurile DAX relevante pentru analiză.

Coloanele ascunse continuă să existe în model și sunt utilizate de relații și de calculele DAX.

În această etapă nu au fost șterse date din sursele procesate.

---

## Step 58 — Perform final relationship QA

### English

All semantic-model relationships were reviewed using Power BI:

```text
Manage relationships
```

The final model contains:

```text
7 relationships
```

The audit confirmed:

```text
Active relationships:               7
Inactive relationships:             0

Many-to-one relationships:          7
Many-to-many relationships:         0

Single-direction relationships:     7
Bidirectional relationships:        0

Direct Fact-to-Fact relationships:  0
```

The verified relationships are:

```text
FactBaccalaureate[county_code]
→ DimCounty[county_code]

FactBaccalaureate[year]
→ DimYear[year]


FactEmployment[county_code]
→ DimCounty[county_code]

FactEmployment[year]
→ DimYear[year]


FactEnrollment[analysis_year]
→ DimYear[year]

FactEnrollment[county_code]
→ DimCounty[county_code]

FactEnrollment[education_level]
→ DimEducationLevel[education_level]
```

The model therefore follows the intended dimensional-filtering structure.

### Română

Toate relațiile modelului semantic au fost verificate folosind:

```text
Manage relationships
```

Modelul final conține:

```text
7 relații
```

Auditul a confirmat:

```text
Relații active:                     7
Relații inactive:                   0

Relații many-to-one:                7
Relații many-to-many:               0

Relații single-direction:           7
Relații bidirecționale:             0

Relații directe Fact-to-Fact:       0
```

Relațiile verificate sunt:

```text
FactBaccalaureate[county_code]
→ DimCounty[county_code]

FactBaccalaureate[year]
→ DimYear[year]


FactEmployment[county_code]
→ DimCounty[county_code]

FactEmployment[year]
→ DimYear[year]


FactEnrollment[analysis_year]
→ DimYear[year]

FactEnrollment[county_code]
→ DimCounty[county_code]

FactEnrollment[education_level]
→ DimEducationLevel[education_level]
```

Modelul respectă astfel structura dimensională și direcția de filtrare planificate.

---

## Step 59 — Perform final dashboard QA

### English

The report was tested both with national-level defaults and individual county selections.

The final QA process covered:

```text
KPI calculations
slicer behaviour
county filtering
year filtering
education-level filtering
trend recalculation
Top / Bottom rankings
scatter-plot behaviour
cross-domain comparison table
percentage formatting
dynamic numeric formatting
display units
chronological sorting
visual titles
model relationships
```

Example county selections were tested on each analytical page.

Employment indicators correctly recalculated for individual counties.

Enrollment measures and trends correctly responded to County and Education Level selections.

Baccalaureate KPI cards and trends correctly responded to county selections.

The County Comparison table correctly reduced to the selected county while preserving the intended analytical comparison context.

The final report is therefore considered functionally validated for the implemented analytical scope.

### Română

Raportul a fost testat atât cu valorile naționale implicite, cât și prin selectarea unor județe individuale.

Procesul final QA a verificat:

```text
calculele KPI
funcționarea slicerelor
filtrarea după județ
filtrarea după an
filtrarea după nivel educațional
recalcularea trendurilor
clasamentele Top / Bottom
funcționarea scatter plot-urilor
tabelul cross-domain
formatarea procentelor
formatarea numerică dinamică
unitățile de afișare
sortarea cronologică
titlurile vizualurilor
relațiile modelului
```

Au fost testate selecții individuale de județe pe fiecare pagină analitică.

Indicatorii Employment s-au recalculat corect pentru județele selectate.

Măsurile și trendurile Enrollment au răspuns corect la selecțiile County și Education Level.

KPI-urile și trendurile pentru Bacalaureat au răspuns corect la selecțiile județene.

Tabelul `County Comparison` s-a redus corect la județul selectat, păstrând contextul comparativ planificat.

Raportul este astfel considerat validat funcțional pentru scopul analitic implementat.

---

# Final Power BI Architecture

## English

The final analytical architecture is:

```text
Official public statistical sources
        ↓
Python ingestion
        ↓
Raw data preservation
        ↓
Schema investigation
        ↓
Cleaning and normalization
        ↓
Data-quality validation
        ↓
Processed datasets
        ↓
Power BI
        ↓
Dimensional semantic model
        ↓
DAX business measures
        ↓
Interactive dashboard
        ↓
Cross-domain analysis
        ↓
Key findings
```

The final Power BI semantic model contains:

```text
FACT TABLES
3

FactEmployment
FactEnrollment
FactBaccalaureate


DIMENSION TABLES
3

DimCounty
DimYear
DimEducationLevel


RELATIONSHIPS
7 active relationships


GEOGRAPHICAL UNITS
42 Romanian county-level units


MAIN COMMON PERIOD
2015–2023
```

### Română

Arhitectura analitică finală este:

```text
Surse statistice publice oficiale
        ↓
Ingestie Python
        ↓
Păstrarea datelor raw
        ↓
Investigarea schemelor
        ↓
Curățare și normalizare
        ↓
Validarea calității
        ↓
Dataseturi procesate
        ↓
Power BI
        ↓
Model semantic dimensional
        ↓
Măsuri business DAX
        ↓
Dashboard interactiv
        ↓
Analiză cross-domain
        ↓
Key Findings
```

Modelul semantic Power BI final conține:

```text
FACT TABLES
3

FactEmployment
FactEnrollment
FactBaccalaureate


DIMENSION TABLES
3

DimCounty
DimYear
DimEducationLevel


RELAȚII
7 relații active


UNITĂȚI GEOGRAFICE
42 unități județene din România


PERIOADĂ PRINCIPALĂ COMUNĂ
2015–2023
```

---

# Final Dashboard Structure

```text
1. Executive Overview

2. Employment Analysis

3. Enrollment Analysis

4. Baccalaureate Analysis

5. County Comparison

6. Key Findings
```

The report therefore moves progressively from:

```text
overall situation
        ↓
domain-specific analysis
        ↓
cross-domain county comparison
        ↓
final analytical conclusions
```

---

# Updated Development Progress Summary

```text
PROJECT STRUCTURE                         ✅ COMPLETE


EMPLOYMENT PIPELINE                       ✅ COMPLETE

Source identification                    ✅
API connectivity                         ✅
Raw data ingestion                       ✅
Raw preservation                         ✅
JSON-stat parsing                        ✅
NUTS 3 filtering                         ✅
Transformation                           ✅
Validation                               ✅
Processed dataset                        ✅


ENROLLMENT PIPELINE                       ✅ COMPLETE

Source identification                    ✅
CKAN API discovery                       ✅
Raw file ingestion                       ✅
Multi-year ingestion                     ✅
Schema comparison                        ✅
Header diagnosis                         ✅
Measure investigation                    ✅
Aggregate-row diagnosis                  ✅
Duplicate investigation                  ✅
NUTS 3 standardization                   ✅
Multi-year transformation                ✅
Validation                               ✅
Processed dataset                        ✅


BACCALAUREATE PIPELINE                    ✅ COMPLETE

Source identification                    ✅
Annual source inventory                  ✅
Cross-year format inspection             ✅
Malformed-source diagnosis               ✅
Candidate validation                     ✅
SIIIR normalization                      ✅
County mapping                           ✅
Result normalization                     ✅
Final-grade normalization                ✅
Candidate-level standardized layer       ✅
County × Year aggregation                ✅
Validation                               ✅
Processed dataset                        ✅


HIGHER EDUCATION

Source investigation                     ✅
Geographical suitability assessment      ✅
Production integration                   ⏸ DEFERRED


FINAL PROCESSED DATA AUDIT                ✅ PASS


POWER BI

Production-data import                    ✅
Dimensional model                         ✅
Fact constellation architecture           ✅
Dimension tables                          ✅
Relationships                             ✅
DAX measures                              ✅
Dynamic formatting                       ✅
Executive Overview                        ✅
Employment Analysis                       ✅
Enrollment Analysis                       ✅
Baccalaureate Analysis                    ✅
County Comparison                         ✅
Key Findings                              ✅
Visual interaction testing                ✅
Semantic-model cleanup                    ✅
Relationship QA                           ✅ PASS
Dashboard QA                              ✅ PASS


PUBLIC SOURCE-CODE CURATION               ✅ COMPLETE

PRIVACY / .GITIGNORE REVIEW               ✅ COMPLETE

DASHBOARD SCREENSHOTS                     ✅ COMPLETE

FINAL DOCUMENTATION                       ✅ COMPLETE

GITHUB CLEANUP                            ✅ COMPLETE

GITHUB PUBLICATION                        ✅ COMPLETE

FINAL SOURCE / LICENSING REVIEW           🔄 IN PROGRESS
```

---

# Public Repository Curation

## English

Before public GitHub publication, the complete development workspace was reviewed separately from the final public repository structure.

The development log intentionally preserves the complete history of the project, including exploratory scripts, diagnostic scripts, fallback approaches, superseded implementations, and deferred components.

The public `src/` directory contains a curated subset of the development scripts that best represent the final reproducible workflow.

The final public source-code selection contains 16 scripts:

```text
02_test_eurostat_api.py
03_ingest_employment.py
04_transform_employment.py

12_ingest_all_enrollment.py
18_transform_all_enrollment.py

21_inventory_baccalaureate_sources.py
26_ingest_all_baccalaureate.py
30_fast_count_baccalaureate_2016_ods.py
32_validate_siiir_county_mapping.py
34_diagnose_baccalaureate_2022_final_results.py
37_ingest_baccalaureate_2017_ods.py
39_validate_baccalaureate_core_all_years.py
41_profile_baccalaureate_results_all_years.py
42_transform_baccalaureate_candidate_level.py
43_aggregate_baccalaureate.py

48_validate_processed_datasets.py
```

Scripts not included in the public `src/` directory remain documented in this development log whenever they are relevant to the methodological history of the project.

They were excluded from the public code layer when they represented:

```text
exploratory investigation
temporary diagnostics
superseded implementations
deferred project components
or diagnostics capable of displaying unnecessary candidate-level output
```

No historical development step was removed from the documentation.

The purpose of the public-code curation is not to hide the development process, but to separate:

```text
complete development history
        ↓
curated reproducible public code
```

This keeps the GitHub repository easier to review while the development log preserves the full technical reasoning behind the project.

### Public data boundaries

The local development workspace contains three data layers:

```text
data/raw/
data/interim/
data/processed/
```

The public repository uses `.gitignore` to exclude:

```text
data/raw/
data/interim/
data/processed/enrollment_2015_2016_clean.csv
```

`data/raw/` contains original source files retained locally during development.

These files are not required in the public repository because the relevant ingestion scripts and source documentation identify how the data were obtained.

Keeping raw files outside the public repository also reduces unnecessary duplication and allows licensing, redistribution, file-size, and privacy considerations to be handled conservatively.

`data/interim/` contains the standardized Baccalaureate candidate-level analytical layer.

The main intermediate file is:

```text
data/interim/baccalaureate_candidate_standardized.csv
```

This file contains candidate-level identifiers used internally for:

```text
candidate validation
uniqueness validation
SIIIR normalization
geographical mapping
result normalization
final-grade normalization
County × Year aggregation
```

The candidate-level intermediate layer is therefore intended to remain local to the data-processing workflow.

It is not published as part of the public GitHub dataset layer.

Only aggregated Baccalaureate information is used by the final Power BI model.

The three final processed analytical datasets published in the repository are:

```text
data/processed/employment_clean.csv
data/processed/enrollment_clean.csv
data/processed/baccalaureate_clean.csv
```

These contain the analytical information used by the final Power BI model.

The old single-year Enrollment prototype:

```text
data/processed/enrollment_2015_2016_clean.csv
```

is retained locally as a development artifact but is excluded from the public repository.

### Power BI artifact

The final Power BI report is stored as:

```text
powerbi/romania_education_employment.pbix
```

The report contains the final semantic model, DAX measures, interaction logic, and six analytical pages.

### Dashboard documentation assets

Six final report screenshots are stored in:

```text
docs/images/
```

Files:

```text
executive_overview.png
employment_analysis.png
enrollment_analysis.png
baccalaureate_analysis.png
county_comparison.png
key_findings.png
```

### Publication safeguards

Before staging the rebuilt repository, `.gitignore` was explicitly tested for:

```text
data/raw/
data/interim/
data/processed/enrollment_2015_2016_clean.csv
```

The staged file list was then inspected before commit and push.

No raw dataset, candidate-level intermediate dataset, or single-year Enrollment prototype was included in the published commit.

The reviewed public Python scripts contain no embedded passwords, API keys, access tokens, private credentials, or absolute user-specific file paths.

The public repository was then committed and pushed to the existing `main` branch while the legacy project version remained preserved separately.

Source attribution and dataset licensing remain subject to a final documentation review because individual source resources may use different licensing metadata.

---

## Română

Înainte de publicarea pe GitHub, workspace-ul complet de dezvoltare a fost analizat separat de structura finală a repository-ului public.

Development log-ul păstrează intenționat istoricul complet al proiectului, inclusiv scripturile exploratorii, scripturile de diagnostic, soluțiile fallback, implementările înlocuite ulterior și componentele amânate.

Folderul public `src/` conține o selecție a scripturilor care reprezintă cel mai bine fluxul final reproductibil.

Selecția publică finală conține 16 scripturi:

```text
02_test_eurostat_api.py
03_ingest_employment.py
04_transform_employment.py

12_ingest_all_enrollment.py
18_transform_all_enrollment.py

21_inventory_baccalaureate_sources.py
26_ingest_all_baccalaureate.py
30_fast_count_baccalaureate_2016_ods.py
32_validate_siiir_county_mapping.py
34_diagnose_baccalaureate_2022_final_results.py
37_ingest_baccalaureate_2017_ods.py
39_validate_baccalaureate_core_all_years.py
41_profile_baccalaureate_results_all_years.py
42_transform_baccalaureate_candidate_level.py
43_aggregate_baccalaureate.py

48_validate_processed_datasets.py
```

Scripturile care nu sunt incluse în folderul public `src/` rămân documentate în acest development log atunci când sunt relevante pentru istoricul metodologic al proiectului.

Ele au fost excluse din stratul public de cod atunci când reprezentau:

```text
investigații exploratorii
diagnostice temporare
implementări înlocuite ulterior
componente amânate ale proiectului
sau diagnostice care puteau afișa inutil informații la nivel de candidat
```

Nicio etapă istorică de dezvoltare nu a fost eliminată din documentație.

Scopul selecției publice de cod nu este ascunderea procesului de dezvoltare, ci separarea:

```text
istoricului complet de dezvoltare
        ↓
codului public reproductibil și relevant
```

Astfel, repository-ul GitHub rămâne ușor de analizat, iar development log-ul păstrează raționamentul tehnic complet al proiectului.

### Limitele datelor publice

Workspace-ul local conține trei straturi de date:

```text
data/raw/
data/interim/
data/processed/
```

Repository-ul public utilizează `.gitignore` pentru excluderea:

```text
data/raw/
data/interim/
data/processed/enrollment_2015_2016_clean.csv
```

`data/raw/` conține fișierele originale ale surselor păstrate local în timpul dezvoltării.

Aceste fișiere nu sunt necesare în repository-ul public deoarece scripturile relevante de ingestie și documentația surselor descriu modul în care datele au fost obținute.

Păstrarea fișierelor raw în afara repository-ului public reduce și duplicarea inutilă și permite tratarea conservatoare a aspectelor privind licențierea, redistribuirea, dimensiunea fișierelor și protecția datelor.

`data/interim/` conține stratul analitic standardizat de Bacalaureat la nivel de candidat.

Principalul fișier intermediar este:

```text
data/interim/baccalaureate_candidate_standardized.csv
```

Acesta conține identificatori la nivel de candidat utilizați intern pentru:

```text
validarea candidaților
validarea unicității
normalizarea SIIIR
maparea geografică
normalizarea rezultatelor
normalizarea mediei finale
agregarea Județ × An
```

Stratul intermediar la nivel de candidat este destinat să rămână local în cadrul fluxului de procesare.

Acesta nu este publicat ca parte a stratului public de date din repository-ul GitHub.

Modelul final Power BI utilizează numai informații agregate de Bacalaureat.

Cele trei dataseturi procesate finale publicate în repository sunt:

```text
data/processed/employment_clean.csv
data/processed/enrollment_clean.csv
data/processed/baccalaureate_clean.csv
```

Acestea conțin informațiile analitice utilizate în modelul Power BI final.

Prototipul Enrollment pentru un singur an:

```text
data/processed/enrollment_2015_2016_clean.csv
```

este păstrat local ca artefact de dezvoltare, dar este exclus din repository-ul public.

### Artefactul Power BI

Raportul Power BI final este stocat în:

```text
powerbi/romania_education_employment.pbix
```

Raportul conține modelul semantic final, măsurile DAX, logica interacțiunilor și cele șase pagini analitice.

### Materiale vizuale pentru documentație

Cele șase screenshots finale sunt stocate în:

```text
docs/images/
```

Fișiere:

```text
executive_overview.png
employment_analysis.png
enrollment_analysis.png
baccalaureate_analysis.png
county_comparison.png
key_findings.png
```

### Măsuri de siguranță pentru publicare

Înainte de staging-ul repository-ului reconstruit, `.gitignore` a fost verificat explicit pentru:

```text
data/raw/
data/interim/
data/processed/enrollment_2015_2016_clean.csv
```

Lista fișierelor staged a fost apoi inspectată înainte de commit și push.

Niciun dataset raw, dataset intermediar la nivel de candidat sau prototip Enrollment pentru un singur an nu a fost inclus în commit-ul publicat.

Scripturile Python selectate pentru publicare nu conțin parole, chei API, access tokens, credentiale private sau path-uri locale absolute specifice utilizatorului.

Repository-ul public a fost apoi publicat pe branch-ul existent `main`, iar versiunea veche a proiectului a rămas păstrată separat.

Atribuirea surselor și licențierea dataseturilor rămân supuse unei verificări finale de documentație deoarece resursele sursă individuale pot utiliza metadata de licențiere diferite.

---

# Current Final Analytical Baseline

```text
EMPLOYMENT

Source:
Eurostat

Dataset:
nama_10r_3empers

Period:
2014–2023

Grain:
County × Year

Rows:
420

Counties:
42


ENROLLMENT

Source:
data.gov.ro / official education datasets

School-year period:
2015-2016 → 2023-2024

Analysis years:
2015–2023

Grain:
County × School Year × Education Level

Rows:
2,432

Counties:
42

Formal education levels:
7


BACCALAUREATE

Source:
Official annual Baccalaureate datasets

Period:
2015–2023

Session:
Session I

Final analytical grain:
County × Year

Rows:
378

Counties:
42


COMMON GEOGRAPHICAL KEY

county_code
Romanian NUTS 3 county-level code


MAIN COMMON ANALYTICAL PERIOD

2015–2023


PROCESSED-DATA VALIDATION

Errors:   0
Warnings: 0

FINAL STATUS:
PASS


POWER BI MODEL

Fact tables:       3
Dimension tables:  3
Relationships:     7
Active:            7
Many-to-many:      0
Bidirectional:     0


POWER BI REPORT

Pages:             6

Executive Overview
Employment Analysis
Enrollment Analysis
Baccalaureate Analysis
County Comparison
Key Findings
```

---

# Final Public Repository Structure

```text
romania-education-employment-powerbi/
│
├── data/
│   └── processed/
│       ├── employment_clean.csv
│       ├── enrollment_clean.csv
│       └── baccalaureate_clean.csv
│
├── docs/
│   ├── development_log.md
│   └── images/
│       ├── executive_overview.png
│       ├── employment_analysis.png
│       ├── enrollment_analysis.png
│       ├── baccalaureate_analysis.png
│       ├── county_comparison.png
│       └── key_findings.png
│
├── powerbi/
│   └── romania_education_employment.pbix
│
├── src/
│   ├── 02_test_eurostat_api.py
│   ├── 03_ingest_employment.py
│   ├── 04_transform_employment.py
│   ├── 12_ingest_all_enrollment.py
│   ├── 18_transform_all_enrollment.py
│   ├── 21_inventory_baccalaureate_sources.py
│   ├── 26_ingest_all_baccalaureate.py
│   ├── 30_fast_count_baccalaureate_2016_ods.py
│   ├── 32_validate_siiir_county_mapping.py
│   ├── 34_diagnose_baccalaureate_2022_final_results.py
│   ├── 37_ingest_baccalaureate_2017_ods.py
│   ├── 39_validate_baccalaureate_core_all_years.py
│   ├── 41_profile_baccalaureate_results_all_years.py
│   ├── 42_transform_baccalaureate_candidate_level.py
│   ├── 43_aggregate_baccalaureate.py
│   └── 48_validate_processed_datasets.py
│
├── .gitignore
└── README.md
```

The local development workspace additionally retains `data/raw/`, `data/interim/`, and other historical development artifacts, but these are not part of the published repository structure.

---

# Current Project Status

## English

The complete analytical workflow from public-source ingestion to interactive business intelligence reporting is operational and the rebuilt portfolio project has been published to GitHub.

The project currently demonstrates:

```text
Python
pandas
REST APIs
CKAN APIs
JSON
JSON-stat
Excel ingestion
ODS processing
data profiling
schema diagnosis
data cleaning
data transformation
data validation
cross-source harmonization
NUTS 3 geographical standardization
candidate-level normalization
aggregated analytical modelling
dimensional modelling
Power BI
DAX
dynamic formatting
interactive filtering
interaction design
cross-domain analysis
analytical interpretation
data-quality validation
privacy-aware repository curation
Git / GitHub publication workflow
```

Three production analytical pipelines are complete:

```text
Employment
Enrollment
Baccalaureate
```

A fourth potential component:

```text
Higher Education
```

was investigated but intentionally deferred because a sufficiently reproducible and geographically compatible County × Year source was not obtained through the tested programmatic routes.

The final processed-data validation returned:

```text
Errors:   0
Warnings: 0

FINAL STATUS:
PASS
```

The final Power BI semantic model contains:

```text
3 fact tables
3 dimension tables
7 active one-to-many relationships
0 many-to-many relationships
0 bidirectional relationships
```

The final report contains six pages:

```text
1. Executive Overview
2. Employment Analysis
3. Enrollment Analysis
4. Baccalaureate Analysis
5. County Comparison
6. Key Findings
```

The following publication stages are complete:

```text
public source-code curation
privacy / .gitignore review
dashboard screenshots
final README and development documentation
repository cleanup
GitHub publication
```

The rebuilt version was published to the existing repository URL and `main` branch while the previous project version remained preserved separately.

The only remaining documentation-maintenance task is:

```text
final source-attribution and licensing review
```

This final review does not change the analytical results or Power BI model; it concerns the precision of reuse / attribution documentation for the individual official source resources.

---

## Română

Fluxul analitic complet, de la ingestia surselor publice până la raportarea interactivă Business Intelligence, este funcțional, iar versiunea reconstruită a proiectului de portofoliu a fost publicată pe GitHub.

Proiectul demonstrează în prezent utilizarea:

```text
Python
pandas
REST APIs
CKAN APIs
JSON
JSON-stat
ingestie Excel
procesare ODS
profilarea datelor
diagnosticarea schemelor
curățarea datelor
transformarea datelor
validarea datelor
armonizare cross-source
standardizare geografică NUTS 3
normalizare la nivel de candidat
modelare analitică agregată
modelare dimensională
Power BI
DAX
formatare dinamică
filtrare interactivă
proiectarea interacțiunilor
analiză cross-domain
interpretare analitică
validarea calității datelor
curatarea repository-ului cu atenție la protecția datelor
workflow Git / GitHub pentru publicare
```

Cele trei pipeline-uri analitice de producție sunt finalizate:

```text
Employment
Enrollment
Baccalaureate
```

O a patra componentă potențială:

```text
Higher Education
```

a fost investigată, dar a fost amânată intenționat deoarece prin rutele programatice testate nu a fost obținută o sursă Județ × An suficient de reproductibilă și compatibilă geografic.

Validarea finală a datelor procesate a returnat:

```text
Errors:   0
Warnings: 0

FINAL STATUS:
PASS
```

Modelul semantic Power BI final conține:

```text
3 fact tables
3 dimension tables
7 relații active one-to-many
0 relații many-to-many
0 relații bidirecționale
```

Raportul final conține șase pagini:

```text
1. Executive Overview
2. Employment Analysis
3. Enrollment Analysis
4. Baccalaureate Analysis
5. County Comparison
6. Key Findings
```

Următoarele etape de publicare sunt finalizate:

```text
selecția publică a codului sursă
verificarea privacy / .gitignore
screenshots ale dashboardului
README și documentația finală de dezvoltare
curățarea repository-ului
publicarea pe GitHub
```

Versiunea reconstruită a fost publicată la URL-ul existent al repository-ului și pe branch-ul `main`, iar versiunea anterioară a proiectului a rămas păstrată separat.

Singura activitate rămasă la nivel de întreținere a documentației este:

```text
verificarea finală a atribuirii surselor și a licențelor
```

Această verificare finală nu modifică rezultatele analitice sau modelul Power BI; ea privește precizia documentării condițiilor de reutilizare și atribuire pentru resursele oficiale individuale.

---

# Final Publication Status

```text
DATA PIPELINES
Employment                         ✅ COMPLETE
Enrollment                         ✅ COMPLETE
Baccalaureate                      ✅ COMPLETE
Higher Education                   ⏸ DEFERRED

DATA QUALITY
Final processed-data audit         ✅ PASS
Errors                             0
Warnings                           0

POWER BI
Semantic model                     ✅ COMPLETE
DAX measures                       ✅ COMPLETE
Dashboard                          ✅ COMPLETE
Dashboard QA                       ✅ PASS
Screenshots                        ✅ COMPLETE

PUBLIC REPOSITORY
Public code curation               ✅ COMPLETE
Privacy / .gitignore review        ✅ COMPLETE
Repository cleanup                 ✅ COMPLETE
README                             ✅ COMPLETE
Development log                    ✅ COMPLETE
Git commit                         ✅ COMPLETE
GitHub push to main                ✅ COMPLETE
Legacy version preservation        ✅ COMPLETE

DOCUMENTATION MAINTENANCE
Final licensing review             🔄 IN PROGRESS
```

The analytical and portfolio build is complete and publicly available. Future work is optional enhancement or documentation maintenance rather than completion of the core project.
