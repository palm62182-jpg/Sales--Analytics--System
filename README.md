# Sales--Analytics--System
Sales Analytics & Data Enrichment System
A robust Python-based data engineering pipeline that processes raw sales data, performs multi-level validation, integrates with external REST APIs for data enrichment, and generates comprehensive business intelligence reports.

 Key Features
Multi-Format Data Ingestion: Handles pipe-delimited (.txt) and comma-separated (.csv) files with support for multiple encodings (UTF-8, Latin-1, CP1252).

Data Cleaning & Validation:

Removes special characters and handles formatting in currency/numeric fields.

Enforces strict business rules (Transaction, Product, and Customer ID verification).

Interactive Data Filtering: CLI-based interface allowing users to filter analysis by Region and Transaction Amount ranges.

REST API Integration: Enriches internal sales records by fetching real-time product categories, brands, and ratings from the DummyJSON API.

Business Intelligence Reporting: Generates a professional sales_report.txt featuring:

Region-wise performance analysis.

Top 5 Products & Customers.

Chronological Daily Sales Trends.

API Enrichment success metrics.

 System Architecture
The project follows a modular functional programming approach:

File I/O Module: Manages safe file reading and raw data parsing.

Validation Engine: Filters out non-compliant business records.

Analytics Engine: Performs aggregations (Revenue, AOV, Regional % of total).

Enrichment Service: Manages asynchronous communication with the external Product API.

Reporting Service: Formats data into a human-readable text-based dashboard.

 Getting Started
Prerequisites
Python 3.x

requests library

Installation & Execution
Clone the repository:


Bash

cd sales-analytics-system
Run the application:

Bash

python main.py
Project Structure
Plaintext

├── main.py                     # Entry point (Workflow Orchestration)
├── cleaned_sales_data.csv      # Input data source
├── data/
│   └── enriched_sales_data.txt # Output: Cleaned data + API attributes
└── output/
    └── sales_report.txt        # Final Business Intelligence Report
📊 Sample Report Output
Plaintext

============================================
           SALES ANALYTICS REPORT
============================================
OVERALL SUMMARY
--------------------------------------------
Total Revenue:        ₹15,45,000.00
Total Transactions:   95
Average Order Value:  ₹16,263.16
Date Range:           2024-12-01 to 2024-12-31

REGION-WISE PERFORMANCE
--------------------------------------------
Region    Sales          % of Total  Transactions
North     ₹4,50,000      29.13%      25
South     ₹3,80,000      24.60%      22
🛠️ Technologies Used
Language: Python 3.10+

Libraries: requests (API), csv, re (Regex), collections (Data structures)

API: DummyJSON Product API
