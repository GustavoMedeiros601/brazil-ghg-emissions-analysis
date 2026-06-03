# Brazil Emissions Analysis

Exploratory data analysis of greenhouse gas (GHG) emissions in Brazil using public datasets from SEEG and IBGE.

The project builds a complete analytical workflow, from raw data preparation to exploratory analysis, generating structured datasets and visual insights about emissions across Brazilian states, economic sectors and historical trends.

---

# Problem Context

Understanding greenhouse gas emissions is essential for evaluating environmental impacts, supporting public policy discussions and monitoring climate-related indicators.

Although Brazil provides extensive public datasets through SEEG and IBGE, these sources require cleaning, transformation and integration before meaningful analysis can be performed.

This project addresses that challenge by creating a reproducible data pipeline that transforms raw datasets into analytical outputs ready for exploration and visualization.

---

# Objectives

- Analyze greenhouse gas emissions across Brazilian states
- Calculate emissions per capita using population estimates
- Compare emissions between economic sectors
- Explore historical emission trends in Brazil
- Demonstrate practical applications of data preparation and exploratory analysis techniques

---

# Data Sources

## SEEG

Sistema de Estimativas de Emissões e Remoções de Gases de Efeito Estufa.

Data used:

- State-level emissions
- Sector-level emissions
- Historical emissions series

## IBGE

Instituto Brasileiro de Geografia e Estatística.

Data used:

- Municipal population estimates (2022)

---

# Technologies

- Python
- Pandas
- Matplotlib
- Jupyter Notebook
- Pathlib

---

# Project Structure

```text
BRAZIL-EMISSIONS-ANALYSIS/
│
├── data/
│   ├── raw/
│   │   ├── 1-SEEG10_GERAL-BR_UF_2022.10.27-FINAL-SITE.xlsx
│   │   └── POP2022_Municipios.xls
│   │
│   └── processed/
│       ├── emissao_anual_brasil.csv
│       ├── emissao_estado_2021.csv
│       ├── emissao_per_capita_2021.csv
│       ├── emissao_setor_2021.csv
│       └── emissoes_co2e_gwp_ar5_1970_2021.csv
│
├── notebook/
│   ├── 01_data_preparation_emissions.ipynb
│   └── 02_exploratory_analysis.ipynb
│
└── README.md
```

---

# Workflow

```text
Raw Data (SEEG + IBGE)
           │
           ▼
Data Cleaning
           │
           ▼
Data Transformation
           │
           ▼
Population Integration
           │
           ▼
Per Capita Calculations
           │
           ▼
Processed Datasets
           │
           ▼
Exploratory Analysis
           │
           ▼
Visual Insights
```

---

# Generated Datasets

| Dataset | Description |
|----------|-------------|
| emissao_estado_2021 | Total greenhouse gas emissions by state |
| emissao_per_capita_2021 | Emissions per capita by state |
| emissao_setor_2021 | Emissions grouped by economic sector |
| emissao_anual_brasil | Historical national emissions series |
| emissoes_co2e_gwp_ar5_1970_2021 | Historical emissions dataset used for trend analysis |

---

# Analysis Performed

The exploratory notebook investigates:

## State Emissions

Comparison of total emissions across Brazilian states.

## Emissions Per Capita

Analysis of emissions relative to population size.

## Economic Sectors

Evaluation of sector participation in total emissions.

## Historical Trends

Investigation of emission patterns over time.

---

# Skills Demonstrated

- Data Cleaning
- Data Transformation
- Data Integration
- Exploratory Data Analysis (EDA)
- Data Visualization
- Analytical Thinking
- Reproducible Data Workflows
- Public Data Processing

---

# How to Run

## 1. Clone the repository

```bash
git clone https://github.com/SEU-USUARIO/brazil-emissions-analysis.git
cd brazil-emissions-analysis
```

## 2. Install dependencies

```bash
pip install pandas matplotlib openpyxl python-calamine
```

## 3. Run the notebooks

Execute the notebooks in the following order:

1. `01_data_preparation_emissions.ipynb`
2. `02_exploratory_analysis.ipynb`

---

# Future Improvements

Potential future enhancements include:

- Interactive Power BI dashboard
- Geospatial analysis using Brazilian maps
- Automated data update pipeline
- Additional environmental indicators
- Forecasting and predictive modeling
- Public analytical dashboard

---

# Author

**Gustavo Medeiros**

Software Engineering Student focused on Data Analytics, Business Intelligence and Artificial Intelligence.

- LinkedIn: www.linkedin.com/in/gustavo-medeiros-m-da-silva-48a11a294
