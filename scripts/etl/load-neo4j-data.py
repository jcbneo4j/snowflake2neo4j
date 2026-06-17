import os
import csv
import uuid
from datetime import datetime
from neo4j import GraphDatabase

# Configuration
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password123")
BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "2"))  # adjust as needed

PATIENTS_CSV = "patients.csv"
APPOINTMENTS_CSV = "appointments.csv"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def parse_datetime(s):
    # Try to parse common datetime format; return ISO string
    try:
        return datetime.fromisoformat(s).isoformat()
    except Exception:
        return s

def stream_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def batch_iter(iterator, size):
    batch = []
    for item in iterator:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch

# Cypher used: UNWIND $patients AS p MERGE (pt:Patient {patient_id: p.patient_id}) SET pt += p
PATIENTS_CYPHER = """
UNWIND $patients AS pt
    MERGE (p:Patient {patient_id: toInteger(pt.patient_id)})
    SET p.first_name = pt.first_name,
        p.last_name = pt.last_name

    MERGE (su:SSN:Unmasked {id: toInteger(pt.patient_id)})
    SET su.role_name = pt.role_name_regular,
        su.ssn = pt.ssn_regular

    MERGE (sm:SSN:Masked {id: toInteger(pt.patient_id)})
    SET sm.role_name = pt.role_name_masked,
        sm.ssn = pt.ssn_masked

    MERGE (p)-[:HAS_SSN]->(su)
    MERGE (p)-[:HAS_SSN]->(sm)
"""

# Cypher used: UNWIND $appts AS a MATCH (pt:Patient {patient_id: a.patient_id}) MERGE (ap:Appointment {appointment_id: a.appointment_id}) SET ap += properties CREATE relationship
APPOINTMENTS_CYPHER = """
UNWIND $appts AS a
MATCH (pt:Patient {patient_id: a.patient_id})
MERGE (ap:Appointment {appointment_id: a.appointment_id})
SET ap.appointment_date = a.appointment_date,
    ap.provider_name = a.provider_name,
    ap.visit_type = a.visit_type
MERGE (pt)-[:HAS_APPOINTMENT]->(ap)
"""

def load_patients(session, batch):
    # Normalize and convert fields as needed
    params = {"patients": []}
    for row in batch:
        params["patients"].append({
            "patient_id": int(row.get("patient_id")) if row.get("patient_id") else None,
            "first_name": row.get("first_name"),
            "last_name": row.get("last_name"),
            "role_name_regular": row.get("role_name_regular"),
            "ssn_regular": row.get("ssn_regular"),
            "role_name_masked": row.get("role_name_masked"),
            "ssn_masked": row.get("ssn_masked"),
        })
    print(f"Running patient batch of {len(params['patients'])}")
    session.run(PATIENTS_CYPHER, params)

def load_appointments(session, batch):
    params = {"appts": []}
    for row in batch:
        # generate stable appointment_id if none provided
        appointment_id = str(uuid.uuid4())
        params["appts"].append({
            "appointment_id": appointment_id,
            "patient_id": int(row.get("patient_id")) if row.get("patient_id") else None,
            "appointment_date": parse_datetime(row.get("appointment_date")),
            "provider_name": row.get("provider_name"),
            "visit_type": row.get("visit_type"),
        })
    print(f"Running appointment batch of {len(params['appts'])}")
    session.run(APPOINTMENTS_CYPHER, params)

def main():
    with driver.session() as session:
        # Load patients in batches
        patient_iter = stream_csv(PATIENTS_CSV)
        for batch in batch_iter(patient_iter, BATCH_SIZE):
            load_patients(session, batch)

        # Load appointments in batches
        appt_iter = stream_csv(APPOINTMENTS_CSV)
        for batch in batch_iter(appt_iter, BATCH_SIZE):
            load_appointments(session, batch)

if __name__ == "__main__":
    main()
