// Create users
CREATE USER neo4j_full SET PASSWORD "password123" CHANGE NOT REQUIRED;
CREATE USER neo4j_limited SET PASSWORD "password123" CHANGE NOT REQUIRED;

// Create roles
CREATE ROLE access_full AS COPY OF reader;
CREATE ROLE access_limited AS COPY OF reader;

// Assign users to roles
GRANT ROLE access_full TO neo4j_full;
GRANT ROLE access_limited TO neo4j_limited;

// Add privileges
DENY TRAVERSE ON GRAPH neo4j NODES Unmasked TO access_limited;
DENY TRAVERSE ON GRAPH neo4j NODES Masked TO access_full;

// Test query
MATCH p=(a)<-[:HAS_APPOINTMENT]-(pt)-[:HAS_SSN]->(ssn)
RETURN p
LIMIT 25;
