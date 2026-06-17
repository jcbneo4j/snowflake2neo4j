from snowflake.connector import connect
import pandas as pd
import os

SNOWFLAKE_CONFIG = {
    "user": os.environ["SNOWFLAKE_USER"],
    "password": os.environ["SNOWFLAKE_PASSWORD"],
    "account": os.environ["SNOWFLAKE_ACCOUNT"],
    "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
    "database": os.environ["SNOWFLAKE_DATABASE"],
    "schema": os.environ["SNOWFLAKE_SCHEMA"],
    "role": os.environ.get("SNOWFLAKE_ROLE"),
}

ROLES = [
    'ACCOUNTADMIN',       
    'HC_ANALYST_DEMO',    
]

QUERY = """
SELECT '{role}' AS role_name, patient_id, last_name, first_name, ssn FROM clinic_schema.masked_patients
"""

all_results = []

cfg = dict(SNOWFLAKE_CONFIG)
conn = connect(**cfg)

for role in ROLES:
    print(f"Querying as role: {role}")
    conn.cursor().execute(f"USE ROLE {role}")
    cursor = conn.cursor().execute(QUERY.format(role=role))
    df = cursor.fetch_pandas_all()
    
    # Convert column names to lowercase
    df.columns = df.columns.str.lower()
    
    all_results.append(df)
    print(f"  → Retrieved {len(df)} rows")

# === MERGE TO SINGLE ROW PER PATIENT ===
df_full = all_results[0]  # ACCOUNTADMIN (full SSN)
df_masked = all_results[1]  # HC_ANALYST_DEMO (masked SSN)

# Rename SSN columns and role_name columns
df_full = df_full.rename(columns={'ssn': 'ssn_regular', 'role_name': 'role_name_regular'})
df_masked = df_masked.rename(columns={'ssn': 'ssn_masked', 'role_name': 'role_name_masked'})

# Merge on patient_id, last_name, first_name
merged_df = df_full.merge(
    df_masked,
    on=['patient_id', 'last_name', 'first_name'],
    how='left'
)

# Reorder columns to include role names
merged_df = merged_df[['patient_id', 'last_name', 'first_name', 'role_name_regular', 'ssn_regular', 'role_name_masked', 'ssn_masked']]

# === EXPORT ===
output_file = 'patients.csv'
merged_df.to_csv(output_file, index=False)

print(f"\n✅ Successfully exported {len(merged_df)} total rows (one per patient) to: {output_file}")
print(f"\nPreview:")
print(merged_df.head(10))


APPOINTMENTS_QUERY = """
SELECT patient_id, provider_name, appointment_date, visit_type
FROM healthcare_db.clinic_schema.appointments
"""

# Query appointments
conn.cursor().execute(f"USE ROLE ACCOUNTADMIN")  # or whichever role can read this table
appointments_cursor = conn.cursor().execute(APPOINTMENTS_QUERY)
appointments_df = appointments_cursor.fetch_pandas_all()

# Normalize column names
appointments_df.columns = appointments_df.columns.str.lower()

# Export appointments
appointments_output_file = "appointments.csv"
appointments_df.to_csv(appointments_output_file, index=False)

print(f"✅ Exported {len(appointments_df)} appointment rows to: {appointments_output_file}")
print(appointments_df.head(10))

