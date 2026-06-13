![MongoDB](https://img.shields.io/badge/MongoDB-6.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Polars](https://img.shields.io/badge/Polars-DataFrame-CD792C?style=for-the-badge&logo=polars&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)

🇬🇧 English | readme en français 👉 [🇫🇷 Français](README.md)
# 🏠 Real Estate Market Analysis – Laplace Immo Database

Project carried out as part of the **Data Engineer training – OpenClassrooms**.

The objective of this project is to design a relational database to centralize and analyze real estate transactions in France, in order to help the **Laplace Immo** agency better understand market dynamics.

The analysis focuses on real estate transactions from the **first half of 2020**.

---

# 🎯 Project Objectives

The goals of this project are:

* structure real estate data in a relational database  
* clean and transform source data  
* design a normalized relational schema  
* load data into a SQLite database  
* perform real estate market analysis using SQL queries  

---

# 🗂️ Data Sources

The data used comes from two main sources:

**DVF (Property Value Requests - Demandes de Valeurs Foncières)**  
Contains real estate transactions (transaction date, property value, surface area, property type, number of rooms, etc.).

**Geographical reference dataset**  
Contains information about regions, departments, municipalities, as well as population data.

These datasets were cleaned and prepared before being integrated into the database.

---

# 🏗️ Database Modeling

The database was designed following **normalization principles (3NF)**.

Main tables:

* `region`  
* `departement`  
* `commune`  
* `vente`  

Each real estate transaction is linked to its municipality, department, and region through **foreign keys**, ensuring data integrity.

---

# 🔧 Data Transformation and Cleaning

Several transformations were applied:

* selection of relevant columns  
* removal of redundant columns  
* removal of duplicates in geographical dimensions  
* conversion of numeric formats  
* handling of missing values  
* creation of a **`vente_clean` view**  

This view notably converts the `date_mutation` column into **ISO format (YYYY-MM-DD)** to facilitate time-based analysis.

---

# 📊 SQL Analyses

Several SQL queries were developed to analyze the real estate market.

Examples of analyses:

* total number of apartments sold  
* number of sales by region  
* proportion of apartments by number of rooms  
* ranking of departments by average price per m²  
* average price per m² for houses in Île-de-France  
* evolution of the number of sales between Q1 and Q2 2020  
* municipalities with the highest number of transactions per 1,000 inhabitants  

A file containing **sample SQL queries used for the analysis** is available in the repository.

---

# 🛠️ Technologies Used

* SQL  
* SQLite  
* Relational data modeling  
* Database normalization  
* Data analysis  

---

# 📂 Repository Content

example_sql_queries.sql → sample SQL queries used for analysis  
data_dictionary.xlsx → data dictionary  
project_presentation.pptx → project presentation  

---

# 🔒 Backup and GDPR Compliance

For this proof of concept, the database is stored locally using **SQLite** to ensure reproducibility.

Only the variables necessary for analysis were retained, in accordance with **GDPR data minimization principles**.

Results are presented in an **aggregated format** (by region, department, or municipality).

---

# 👨‍💻 Author

YAD95  
OpenClassrooms Project – Data Engineer
