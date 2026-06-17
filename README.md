# Healthcare Security Demo

A sample project showing how to secure healthcare data in **Snowflake** and **Neo4j** using roles, secure views, and graph privileges.

## Overview

This project demonstrates:
- Creating a healthcare database, schema, tables, and sample data in Snowflake.
- Restricting access with a custom Snowflake role.
- Masking sensitive data in a secure view.
- Creating Neo4j users and roles with limited graph access.
- Testing access with SQL and Cypher queries.

## Files

- `snowflake_setup.sql` — All Snowflake objects, data loading, roles, and secure view setup.
- `neo4j_security.cypher` — Neo4j users, roles, grants, denies, and test query.

## Snowflake Demo

The Snowflake portion uses a secure view to protect sensitive values and role-based access to limit what analysts can see. Secure views are intended to help control access to sensitive logic and data exposure [web:4][web:13].

### Run the Snowflake script

Execute the commands in `snowflake_setup.sql` in this order:
1. Create the database and schema.
2. Create and populate the tables.
3. Create the analyst role and grant permissions.
4. Create the secure masked view.
5. Grant the role to a user and test access.

## Neo4j Demo

The Neo4j portion creates separate users and roles, then uses privilege rules to restrict graph traversal and reading. Neo4j read and traverse privileges can be granted or denied at the role level, and `DENY` rules can restrict access to specific labels or relationship types [web:5][web:2].

### Run the Neo4j script

Execute the commands in `neo4j_security.cypher` in this order:
1. Create users.
2. Create roles.
3. Assign roles to users.
4. Add privilege restrictions.
5. Log in as a user and test the graph query.

## Usage

### Snowflake test query

```sql
USE ROLE HC_ANALYST_DEMO;

SELECT role_name, patient_id, last_name, first_name, ssn
FROM clinic_schema.masked_patients;
```

### Neo4j test query

```cypher
MATCH p=(a)<-[:HAS_APPOINTMENT]-(pt)-[:HAS_SSN]->(ssn)
RETURN p
LIMIT 25;
```

## Notes

- Replace `<user_name>` with your actual Snowflake username.
- Update passwords before using these scripts in any real environment.
- The sample data is synthetic and intended only for demonstration.

