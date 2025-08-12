
# 📄 Bioenergy Supply Dataset – Côte d’Ivoire (14 Districts)

This file documents the assumptions and construction logic for the dataset `regional_supply_full_corrected.csv`, which represents estimated annual bioenergy supply (in GJ) for each of Côte d’Ivoire’s 14 autonomous districts. The table supports spatially explicit scenario analysis for clean cooking and future sector coupling models.

---

## 📦 Dataset Construction Assumptions

### 1. Spatial Scope
- All estimates are aligned with Côte d’Ivoire’s **14 autonomous districts** (ADM1).
- Where source data was at a lower administrative level (ADM2), it was aggregated to district level using official mappings.

### 2. Empirical Estimates
Supply estimates were directly derived from field-verified sources:

- **Cocoa Pods** in:
  - Montagnes, Bas-Sassandra, Sassandra-Marahoué  
  - Source: *RVO (2021), GIZ/GBN (2020)*  
  - Assumed energy content: **21 GJ/t**

- **Palm Oil Residues (EFB)** in:
  - Bas-Sassandra, Gôh-Djiboua, Lagunes, Comoé  
  - Source: *Biokala, LONO studies, RVO*  
  - Assumed energy content: **8.5 GJ/t**

- **Rubber Wood** in:
  - Lagunes and Comoé  
  - Source: *SBP-certified supply base reports (2021)*  
  - Energy content: **15 GJ/t**

### 3. Urban Biowaste (Abidjan)
- Based on ~600,000 t/year of biodegradable waste
- Assumed energy content: **7 GJ/t**
- Total supply: **4.2 million GJ/year**
- Sources: *Feasibility Study on Biogas/Compost (2023)*, *GBN Sector Brief*

### 4. Extrapolated Supply (Proxy-Based)
For districts lacking empirical data:
- Supply = `Rural Households × Mean Biomass Intensity`
- Intensity derived from known districts with measured biomass supply
- Assigned technology: `"Mixed Biomass"` and `"Mixed (proxy)"`

---

## 🧾 Abbreviations
| Term          | Meaning                                        |
|---------------|------------------------------------------------|
| GJ            | Gigajoule (unit of energy)                     |
| EFB           | Empty Fruit Bunch (from palm oil processing)   |
| HH            | Household                                      |
| SBP           | Sustainable Biomass Program                    |
| ADM1 / ADM2   | Administrative Division Level 1 / 2            |
| RDF           | Refuse-Derived Fuel                            |
| ICS           | Improved Cookstove                             |

---

This dataset is designed to be modular and easily integrated into district-level energy system models for Côte d’Ivoire.
