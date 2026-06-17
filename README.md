i# Healthcare Security Demo

A sample project showing how to secure healthcare data in **Snowflake** using roles with secure views, and ingest into a **Neo4j** graph with RBAC.

## Overview

This project demonstrates:
- Creating a healthcare database, schema, tables, and sample data in Snowflake.
- Restricting access with a custom Snowflake role.
- Masking sensitive data in a secure view.
- Creating Neo4j users and roles with limited graph access.
- Extracting data from Snowflake with Python.
- Loading extracted data into Neo4j with Python.

## Repository Structure

- `scripts/setup/snowflake_setup.sql` — Snowflake database, schema, tables, sample data, role, secure view, and test query.
- `scripts/setup/neo4j_setup.cypher` — Neo4j users, roles, grants, denies, and test query.
- `scripts/etl/snowflake_extract.py` — Python script to extract data from Snowflake.
- `scripts/etl/load-neo4j-data.py` — Python script to load extracted data into Neo4j.
- `requirements.txt` — Python dependencies for the ETL scripts.

## Prerequisites

- Python 3.10+ recommended.
- Access to a Snowflake account with permission to create objects and roles.
- Access to a Neo4j database with permission to create users, roles, and privileges.
- A virtual environment is strongly recommended.

## Install Dependencies

Create and activate a virtual environment:

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Snowflake’s Python connector is installed with `snowflake-connector-python`, and the Neo4j Python driver is installed with `neo4j` 

## Setup Steps

### 1. Run the Snowflake setup script

Open `scripts/setup/snowflake_setup.sql` in Snowflake Worksheets or run it with your preferred SQL runner.

This script:
- Creates the `healthcare_db` database.
- Creates the `clinic_schema` schema.
- Creates `patients`, `appointments`, and `billing` tables.
- Loads sample data.
- Creates the `hc_analyst_demo` role.
- Creates a secure masked view for patient SSNs.
- Grants access and tests the role.

### 2. Run the Neo4j setup script

Open `scripts/setup/neo4j_setup.cypher` in Neo4j Browser, Bloom, or your Cypher client.

This script:
- Creates `neo4j_full` and `neo4j_limited` users.
- Creates `access_full` and `access_limited` roles.
- Assigns roles to users.
- Applies `DENY TRAVERSE` rules for label-based restrictions.
- Includes a test query to validate access.

## Extract from Snowflake

Run the Snowflake extract script after the Snowflake setup is complete.

```bash
python scripts/etl/snowflake_extract.py
```

This script should:
- Connect to Snowflake using your connection settings.
- Query the secured or source Snowflake data.
- Export the extracted result to a file for Neo4j loading.

Typical environment variables you may want to provide:
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`

## Load into Neo4j

After the extract step completes, run the Neo4j load script:

```bash
python scripts/etl/load-neo4j-data.py
```

This script should:
- Read the extracted Snowflake output file.
- Connect to Neo4j with the configured credentials.
- Create nodes and relationships from the extracted data.
- Verify the graph load with the test query.

Typical environment variables you may want to provide:
- `NEO4J_URI`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`
- `NEO4J_DATABASE`

## Example Execution Order

1. Install Python dependencies.
2. Run `scripts/setup/snowflake_setup.sql`.
3. Run `scripts/setup/neo4j_setup.cypher`.
4. Run `scripts/etl/snowflake_extract.py`.
5. Run `scripts/etl/load-neo4j-data.py`.

## Example Test Queries

### Snowflake

```sql
USE ROLE HC_ANALYST_DEMO;

SELECT role_name, patient_id, last_name, first_name, ssn
FROM clinic_schema.masked_patients;
```

### Neo4j

```cypher
MATCH p=(a)<-[:HAS_APPOINTMENT]-(pt)-[:HAS_SSN]->(ssn)
RETURN p
LIMIT 25;
```

## Notes

- Replace placeholder usernames and connection values before running.
- Update passwords before using these scripts in any real environment.
- The sample data is synthetic and intended only for demonstration.

