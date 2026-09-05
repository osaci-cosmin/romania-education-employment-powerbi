# Methodology

## 1. Project Scope

This project examines education and employment indicators across Romanian counties between 2014 and 2023.

The analysis is descriptive and comparative and was developed as an interactive Power BI dashboard.

The main objective is to explore differences between counties, education levels and years using education and employment indicators.

## 2. Data Source

The data were obtained from the Romanian National Institute of Statistics (INS), through the TEMPO-Online database.

The analysis focuses on four main groups of indicators:

- Enrollment
- Graduates
- Baccalaureate Graduates
- Employees

The original project was based on publicly available aggregated statistical data.

## 3. Education Categories

Education indicators were organized into four categories:

- Pre-university Education
- Vocational Education
- Post-secondary and Technical Education
- Higher Education

Higher Education includes university-level studies such as bachelor's, master's, doctoral and post-doctoral education.

## 4. Unit of Analysis

The main unit of comparison is the Romanian county.

The dashboard allows comparisons across counties and education levels, as well as changes over time.

The analysed period covers ten years:

**2014–2023**

## 5. Data Model

The Power BI model uses shared dimension tables in order to provide consistent filtering across the dashboard.

The main dimensions are:

- County
- Year
- Education Level

The County dimension is connected to the relevant education, Baccalaureate and employment data tables.

The Year dimension provides a common time field for the relevant datasets.

The Education Level dimension is used to classify and filter education-related indicators.

Relationships between dimension and data tables follow a one-to-many structure.

## 6. Data Preparation

The data were prepared and organized before being used in the Power BI visualizations.

The main preparation steps included:

- organizing indicators by county and year;
- grouping education indicators into common education categories;
- standardizing fields used for filtering and visualization;
- creating a shared Year dimension;
- creating English presentation labels for the dashboard.

The original Romanian category labels were preserved in the underlying data, while English labels were created for presentation purposes.

## 7. Aggregation

The dashboard primarily uses average values to support comparisons between counties, years and education categories.

The main metrics displayed are:

- Average Enrollment
- Average Graduates
- Average Baccalaureate Graduates
- Average Employees

Using the same aggregation approach across the dashboard helps maintain consistency between visualizations.

## 8. Dashboard Structure

The Power BI report contains six pages.

### Overview

Provides a general view of enrollment, graduates and Baccalaureate graduates over time.

It also includes geographic information and filters for counties and education levels.

### Employment

Compares enrollment, graduates and employees over time and provides additional information about Baccalaureate graduates.

### Graduate Comparison

Allows comparison of average graduates and employees across selected counties and education levels.

### Enrollment Comparison

Allows comparison of average enrollment and employees across selected counties and education levels.

### Baccalaureate Comparison

Focuses on differences in Baccalaureate graduates and employees across counties.

### Key Findings

Summarizes the main trends observed in enrollment, graduates, Baccalaureate graduates and employment over time.

## 9. Interactive Filtering

The dashboard includes interactive filtering by:

- County
- Education Level

A shared Year dimension is used for time-based visualizations to maintain consistency across the relevant datasets.

These filters allow users to explore the data from different perspectives without changing the underlying model.

## 10. Interpretation

The dashboard is designed for descriptive and exploratory analysis.

The visualizations are intended to identify:

- differences between Romanian counties;
- differences between education categories;
- changes over time;
- patterns between education and employment indicators.

The results should not be interpreted as evidence of causal relationships between education and employment.

## 11. Limitations

The analysis is based on aggregated county-level data.

Therefore, the results describe patterns at county level and cannot be used to describe individual educational or employment trajectories.

The analysis also depends on the definitions, availability and coverage of the indicators provided through the INS TEMPO-Online database.