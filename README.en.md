![MongoDB](https://img.shields.io/badge/MongoDB-6.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Polars](https://img.shields.io/badge/Polars-DataFrame-CD792C?style=for-the-badge&logo=polars&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)

🇬🇧 English | readme en français 👉 [🇫🇷 Français](README.md)

# Design and Analyze a NoSQL Database — Project 7

> **NosCités Association** • Paris & Lyon • Summer 2024

---

## --- Context ---

The **NosCités** association monitors short-term rental platforms (Airbnb) to measure their impact on the housing market in Paris and Lyon. Following a total crash of the Parisian rental database, a backup was recovered — the goal is to restore it, analyze it, and build a robust and sustainable architecture.

**Data:** 95,885 Paris listings + 9,973 Lyon listings — Airbnb scraping June 2024  
**Database:** MongoDB (NoSQL) — database `noscites`, collection `listings_paris`

---

## --- Tech Stack ---

| Tool | Usage |
|---|---|
| MongoDB + MongoDB Compass | Data storage and exploration |
| Python / Pandas | CSV data preparation and tagging |
| Polars | Advanced analytics (Rust engine, high performance) |
| MongoDB Connector for BI (ODBC) | MongoDB → Power BI connection |
| Power BI | Dashboard and data visualization |

---

## --- Repository Content ---

| File | Description |
|---|---|
| `presentation.pptx` | Full project presentation support |
| `presentation.pdf` | PDF version of the presentation |
| `polars_request.py` | Polars analytics queries script |
| `tagging_lyon_scripts.py` | Python script for Lyon data preparation |

> ⚠️ Raw CSV files (Airbnb data) are not included due to their size.

---

## --- What Was Done ---

### Part 1 — Restore & Understand the Data
- Import of 95,885 documents into MongoDB via MongoDB Compass
- Description of a document's structure (field types, data categories)
- Justification of the NoSQL choice over SQL for this type of data
- First checks: total number of documents, number of available listings

### Part 2 — Analyze the Data

**6 queries performed with MongoDB:**
1. Number of listings by accommodation type
2. Top 5 listings with the most reviews
3. Total number of unique hosts
4. Number of instantly bookable listings
5. Hosts with more than 100 listings
6. Number of superhosts and their proportion

**5 queries performed with Polars:**
1. Average booking rate per month and accommodation type
2. Median number of reviews for all listings
3. Median number of reviews by host category (superhost vs non-superhost)
4. Listing density by Paris neighbourhood
5. Neighbourhoods with the highest booking rate

> Polars was used for these queries because its Rust engine offers better performance on large datasets.

**MongoDB → Power BI Connection:**  
Since Power BI only accepts SQL engine, an intermediary was installed: **MongoDB Connector for BI (ODBC)**. This connector translates Power BI's SQL queries into MongoDB queries, enabling NoSQL data import and dashboard creation.

### Part 3 — Make the Database Sustainable

**Step 1 — Import Paris + Lyon**  
Lyon data was tagged with a `city: Lyon` field via a Python script, then imported into the same collection as Paris.

**Step 2 — Data Replication with ReplicaSet**  
A 3-node ReplicaSet was set up locally:
- **PRIMARY** (port 27020): receives all write operations
- **SECONDARY** (port 27021): replicates data in real time, takes over in case of failure
- **ARBITER** (port 27022): manages election votes, stores no data

**Step 3 — Data Distribution with Sharding**  
A sharding cluster was set up to separate Paris and Lyon data onto distinct servers. The shard key is the `city` field — each query is routed directly to the right shard without scanning the other city's data.

- **Config Server** (port 27030): stores the cluster map
- **Mongos** (port 27050): single query router
- **shardRS1** (port 27040): Paris data
- **shardRS2** (port 27041): Lyon data

---

📎 *For query details, results and screenshots, please refer to the presentation.*

---

## --- 👤 Author ---
YAD95  
Project completed as part of the **Data Engineer** training — OpenClassrooms
