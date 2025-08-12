
# 📄 Bioenergy Supply and Household Projection – Côte d’Ivoire (14 Districts)

This documentation outlines the assumptions and methodology used to build the dataset `District-level_Household_Projections_UPDATED.csv`, which provides household projections for Côte d’Ivoire’s 14 autonomous districts from 2025 to 2050. This dataset supports the energy demand and cost modelling components of the national bioenergy scenario analysis.

---

## 🧭 Geographic Scope
- The dataset aligns with Côte d’Ivoire’s 14 **autonomous districts** (ADM1 level) as defined in the RGPH 2021 census.
- It enables consistent spatial aggregation for demand, technology adoption, and cost analysis.

---

## 📈 Projection Methodology

### 1. Base Year (2021)
- Sourced from **RGPH 2021 Census**: total population and households per district.
- Calculated district-specific **household size** = Population ÷ Households.

### 2. Growth Assumptions
- A **uniform annual population growth rate of 2.5%** is applied across all districts.
- Household count = Population ÷ Household size (fixed per district from 2021).

### 3. Urban vs. Rural Split
- Urbanisation rates per district are based on census patterns and national planning assumptions:
    - Abidjan: 100% urban
    - Yamoussoukro: 85% urban
    - Montagnes, Savanes, Zanzan, etc.: ~45–55% urban
- Derived annually using fixed shares for simplicity.

---

## 🧾 Data Columns
| Column             | Description                                       |
|--------------------|---------------------------------------------------|
| `District`         | Name of ADM1 district (14 total)                  |
| `Year`             | Projection year (2025–2050, 5-year intervals)     |
| `Total_Households` | Estimated total households per district           |
| `Urban_Households` | Portion of households in urban areas              |
| `Rural_Households` | Portion of households in rural areas              |

---

## 🔍 Source References
- **RGPH 2021 National Census** (INS Côte d’Ivoire)
- Growth and urbanisation parameters inspired by IEA and World Bank datasets (used in national energy outlooks)

This file replaces any previous versions and should be considered the authoritative source for model input projections.

