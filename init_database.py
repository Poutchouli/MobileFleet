# init_database.py
# This script initializes the fleet management database in PostgreSQL.
# It creates the schema and populates it with sample data, including hashed passwords.
# In production mode (FLASK_ENV=production), this script will not run to preserve existing data.

import os
import psycopg2
import time
from psycopg2 import sql
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Environment Check ---
FLASK_ENV = os.environ.get("FLASK_ENV", "development")
if FLASK_ENV == "production":
    print("🚫 Production environment detected. Skipping database initialization to preserve existing data.")
    print("   If you need to initialize the database in production, run this script manually with FLASK_ENV=development")
    exit(0)

print(f"🔧 Running database initialization in {FLASK_ENV} mode...")

# --- Database Connection Configuration ---
# This will be provided by the .env file.
DB_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = None
    # Retry loop to wait for the database container to be ready
    while not conn:
        try:
            conn = psycopg2.connect(DB_URL)
        except psycopg2.OperationalError:
            print("Waiting for database connection...")
            time.sleep(1)
    print("✅ Database connection established successfully.")
    return conn

def execute_queries(cursor, queries):
    """Helper function to execute a list of SQL queries."""
    for query in queries:
        try:
            # Check if the query is a tuple (SQL statement, parameters)
            if isinstance(query, tuple):
                cursor.execute(query[0], query[1])
            else:
                cursor.execute(query)
        except psycopg2.Error as e:
            print(f"❌ Error executing query: {e}")
            raise

def drop_tables(cursor):
    """Drops all tables in the correct order to avoid foreign key constraints."""
    print("\nDropping existing tables...")
    tables_to_drop = [
        "phone_returns", "asset_history_log", "ticket_updates", "tickets", "assignments",
        "phone_numbers", "sim_cards", "phones", "rh_data", "workers", "manager_secteurs", 
        "secteurs", "users", "roles", "phone_requests"
    ]
    for table in tables_to_drop:
        cursor.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(table)))
        print(f"   - Dropped table: {table}")
    print("✅ All existing tables dropped.")

def create_schema(cursor):
    """Creates all tables for the application with English names."""
    print("\nCreating database schema...")
    schema_queries = [
        """
        CREATE TABLE roles (
            id SERIAL PRIMARY KEY,
            role_name VARCHAR(50) NOT NULL UNIQUE CHECK (role_name IN ('Administrator', 'Manager', 'Support', 'Integration Manager')),
            description TEXT
        );
        """,
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            role_id INTEGER NOT NULL REFERENCES roles(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """,
        """
        CREATE TABLE secteurs (
            id SERIAL PRIMARY KEY,
            secteur_name VARCHAR(255) NOT NULL UNIQUE,
            manager_id INTEGER NULL REFERENCES users(id),
            description TEXT
        );
        """,
        """
        CREATE TABLE workers (
            id SERIAL PRIMARY KEY,
            worker_id VARCHAR(50) NOT NULL UNIQUE,
            full_name VARCHAR(255) NOT NULL,
            secteur_id INTEGER NOT NULL REFERENCES secteurs(id),
            status VARCHAR(20) NOT NULL CHECK (status IN ('Active', 'Inactive', 'Arrêt', 'Congés')),
            notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """,
        """
        CREATE TABLE rh_data (
            id SERIAL PRIMARY KEY,
            worker_id INTEGER NOT NULL UNIQUE REFERENCES workers(id) ON DELETE CASCADE,
            id_philia VARCHAR(100),
            mdp_philia VARCHAR(100),
            contract_type VARCHAR(50),
            contract_end_date DATE
        );
        """,
        """
        CREATE TABLE sim_cards (
            id SERIAL PRIMARY KEY,
            iccid VARCHAR(22) NOT NULL UNIQUE,
            carrier VARCHAR(100),
            plan_details TEXT,
            puk VARCHAR(255) NULL,
            status VARCHAR(20) NOT NULL CHECK (status IN ('In Stock', 'In Use', 'Deactivated'))
        );
        """,
        """
        CREATE TABLE phones (
            id SERIAL PRIMARY KEY,
            asset_tag VARCHAR(50) NOT NULL UNIQUE,
            imei VARCHAR(15) NOT NULL UNIQUE,
            serial_number VARCHAR(100) NOT NULL UNIQUE,
            manufacturer VARCHAR(100),
            model VARCHAR(100),
            purchase_date DATE,
            warranty_end_date DATE,
            status VARCHAR(50) NOT NULL CHECK (status IN ('In Stock', 'In Use', 'In Repair', 'Retired', 'Disponible pour enlèvement', 'Préparation SI terminée')),
            notes TEXT,
            worker_id INTEGER REFERENCES workers(id),
            sim_card_id INTEGER REFERENCES sim_cards(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """,
        """
        CREATE TABLE phone_numbers (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(20) NOT NULL UNIQUE,
            sim_card_id INTEGER UNIQUE REFERENCES sim_cards(id),
            rio VARCHAR(255) NULL,
            status VARCHAR(20) NOT NULL CHECK (status IN ('Active', 'Inactive', 'Porting'))
        );
        """,
        """
        CREATE TABLE assignments (
            id SERIAL PRIMARY KEY,
            phone_id INTEGER NOT NULL REFERENCES phones(id),
            sim_card_id INTEGER NOT NULL REFERENCES sim_cards(id),
            worker_id INTEGER NOT NULL REFERENCES workers(id),
            assignment_date TIMESTAMPTZ NOT NULL DEFAULT now(),
            return_date TIMESTAMPTZ NULL
        );
        """,
        """
        CREATE TABLE tickets (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            phone_id INTEGER NOT NULL REFERENCES phones(id),
            reported_by_manager_id INTEGER NOT NULL REFERENCES users(id),
            assigned_to_support_id INTEGER NULL REFERENCES users(id),
            status VARCHAR(20) NOT NULL CHECK (status IN ('New', 'Open', 'Pending', 'On-Hold', 'Solved', 'Closed')),
            priority VARCHAR(20) NOT NULL CHECK (priority IN ('Low', 'Medium', 'High', 'Urgent')),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            resolved_at TIMESTAMPTZ NULL
        );
        """,
        """
        CREATE TABLE ticket_updates (
            id SERIAL PRIMARY KEY,
            ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
            update_author_id INTEGER NOT NULL REFERENCES users(id),
            update_text TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            is_internal_note BOOLEAN NOT NULL DEFAULT false
        );
        """,
        """
        CREATE TABLE asset_history_log (
            id SERIAL PRIMARY KEY,
            asset_type VARCHAR(20) NOT NULL CHECK (asset_type IN ('Phone', 'SIM', 'Ticket')),
            asset_id INTEGER NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            event_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            user_id INTEGER NULL REFERENCES users(id),
            details TEXT
        );
        """,
        """
        CREATE TABLE phone_requests (
            id SERIAL PRIMARY KEY,
            requester_id INTEGER NOT NULL REFERENCES users(id),
            employee_name VARCHAR(100) NOT NULL,
            department VARCHAR(100) NOT NULL,
            position VARCHAR(100) NOT NULL,
            request_reason TEXT NOT NULL,
            phone_type_preference VARCHAR(50),
            urgency_level VARCHAR(20) NOT NULL CHECK (urgency_level IN ('Low', 'Medium', 'High', 'Critical')),
            status VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Denied', 'Fulfilled', 'Cancelled')),
            submitted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            reviewed_by INTEGER REFERENCES users(id),
            reviewed_at TIMESTAMPTZ,
            review_notes TEXT,
            fulfilled_by INTEGER REFERENCES users(id),
            fulfilled_at TIMESTAMPTZ,
            assigned_phone_id INTEGER REFERENCES phones(id)
        );
        """,
        """
        CREATE TABLE manager_secteurs (
            manager_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            secteur_id INTEGER NOT NULL REFERENCES secteurs(id) ON DELETE CASCADE,
            assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (manager_id, secteur_id)
        );
        """,
        """
        CREATE TABLE phone_returns (
            id SERIAL PRIMARY KEY,
            assignment_id INTEGER REFERENCES assignments(id),
            phone_id INTEGER NOT NULL REFERENCES phones(id),
            worker_id INTEGER NOT NULL REFERENCES workers(id),
            manager_id INTEGER NOT NULL REFERENCES users(id),
            return_date TIMESTAMPTZ NOT NULL DEFAULT now(),
            accessories_returned TEXT[], -- e.g., ARRAY['cable', 'chargeur', 'boite']
            phone_condition VARCHAR(255),
            notes TEXT,
            status VARCHAR(50) DEFAULT 'Pending Pickup'
        );
        """,
        """
        -- Function to update the updated_at timestamp
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """,
        """
        -- Trigger to automatically update updated_at for phones table
        CREATE TRIGGER update_phones_updated_at 
            BEFORE UPDATE ON phones 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
        """
    ]
    execute_queries(cursor, schema_queries)
    print("✅ Database schema created successfully.")

def insert_sample_data(cursor):
    """Inserts sample data, including securely hashed passwords."""
    print("\nInserting sample data...")

    # --- Generate Hashes ---
    # One password hash for each role for simplicity in demo
    admin_pass = generate_password_hash("adminpass")
    manager_pass = generate_password_hash("managerpass")
    support_pass = generate_password_hash("supportpass")
    integration_pass = generate_password_hash("integrationpass")

    # --- Define Data for Insertion ---
    # Using lists of tuples for clarity and organization
    roles_data = [
        ('Administrator', 'Full system access.'),
        ('Manager', 'Manages a secteur and its workers.'),
        ('Support', 'Manages support tickets.'),
        ('Integration Manager', 'Manages phone requests and integrations.')
    ]

    users_data = [
        # role_id 1: Administrator
        ('admin', admin_pass, 'Alice Admin', 'alice.admin@example.com', 1),
        # role_id 2: Managers
        ('manager_north', manager_pass, 'Bob Manager', 'bob.manager@example.com', 2),
        ('manager_south', manager_pass, 'Charlie Manager', 'charlie.manager@example.com', 2),
        # role_id 3: Support
        ('support_tech', support_pass, 'David Support', 'david.support@example.com', 3),
        ('support_junior', support_pass, 'Fay Junior Support', 'fay.support@example.com', 3),
        # role_id 4: Integration Manager
        ('integration_mgr', integration_pass, 'Igor Integration', 'igor.integration@example.com', 4)
    ]

    # Note: User IDs will be 1, 2, 3, 4, 5, 6. Bob is 2, Charlie is 3, Igor is 6.
    secteurs_data = [
        ('Northern Sector', 2, 'Field agents in the northern region.'),
        ('Southern Sector', 3, 'Field agents in the southern region.'),
        ('Logistics', 2, 'Warehouse and logistics staff.')
    ]

    workers_data = [
        ('WKR-001', 'Eve Employee', 1, 'Active'),     # Northern Sector - CDI
        ('WKR-002', 'Frank Field', 1, 'Congés'),      # Northern Sector - CDI
        ('WKR-003', 'Grace Ground', 2, 'Active'),     # Southern Sector - CDD expiring soon
        ('WKR-004', 'Heidi Home', 2, 'Arrêt'),        # Southern Sector - CDD critical
        ('WKR-005', 'Ivan Installer', 3, 'Active'),   # Logistics - CDD future
        ('WKR-006', 'Julie Tech', 1, 'Inactive'),     # Northern Sector - CDI
        ('WKR-007', 'Karl Sales', 2, 'Congés'),       # Southern Sector - CDI
        ('WKR-008', 'Laura Engineer', 1, 'Active'),   # Northern Sector - CDD expired
        ('WKR-009', 'Marc Operations', 3, 'Active'),  # Logistics - CDD warning
        ('WKR-010', 'Nina Support', 2, 'Active'),     # Southern Sector - CDD normal
        ('WKR-011', 'Oliver Field', 1, 'Active'),     # Northern Sector - CDI
        ('WKR-012', 'Paula Admin', 3, 'Congés')       # Logistics - CDD critical 2 days
    ]

    phones_data = [
        ('PHN-001', '111111111111111', 'SN-AAA', 'Apple', 'iPhone 14', 'In Use'),
        ('PHN-002', '222222222222222', 'SN-BBB', 'Samsung', 'Galaxy S23', 'In Use'),
        ('PHN-003', '333333333333333', 'SN-CCC', 'Google', 'Pixel 7', 'In Stock'),
        ('PHN-004', '444444444444444', 'SN-DDD', 'Apple', 'iPhone 13', 'In Repair'),
        ('PHN-005', '555555555555555', 'SN-EEE', 'Samsung', 'Galaxy S22', 'Retired')
    ]

    sim_cards_data = [
        ('1111111111111111111111', 'Proximus', '12345678', 'In Use'),
        ('2222222222222222222222', 'Orange', '87654321', 'In Use'),
        ('3333333333333333333333', 'T-Mobile', '11223344', 'In Stock'),
        ('4444444444444444444444', 'BASE', '44332211', 'Deactivated')
    ]
    
    phone_numbers_data = [
        ('+32470123456', 1, 'Active'),
        ('+32471987654', 2, 'Active'),
        ('+32472112233', 3, 'Active')
    ]

    assignments_data = [
        (1, 1, 1), # Phone 1, SIM 1, Worker 1 (Eve)
        (2, 2, 3)  # Phone 2, SIM 2, Worker 3 (Grace)
    ]

    phone_requests_data = [
        # (requester_id, employee_name, department, position, request_reason, phone_type_preference, urgency_level, status)
        (2, 'John Doe', 'Sales', 'Sales Representative', 'New employee needs work phone', 'iPhone', 'Medium', 'Pending'),
        (3, 'Jane Smith', 'Engineering', 'Software Developer', 'Phone damaged, replacement needed', 'Samsung Galaxy', 'High', 'Approved'),
        (6, 'Mike Johnson', 'Operations', 'Field Technician', 'Current phone outdated, needs upgrade', 'Any Android', 'Low', 'Fulfilled')
    ]

    rh_data = [
        # worker_id, id_philia, mdp_philia, contract_type, contract_end_date
        (1, 'philia001', 'pwd_eve123', 'CDI', None),           # Eve Employee - CDI (light blue)
        (2, 'philia002', 'pwd_frank456', 'CDI', None),           # Frank Field - CDI (light blue)
        (3, 'philia003', 'pwd_grace789', 'CDD', '2025-08-05'),   # Grace Ground - CDD 13 days left (yellow)
        (4, 'philia004', 'pwd_heidi012', 'CDD', '2025-07-27'),   # Heidi Home - CDD 4 days left (light red)
        (5, 'philia005', 'pwd_ivan345', 'CDD', '2026-06-30'),   # Ivan Installer - CDD future (light green)
        (6, 'philia006', 'pwd_julie678', 'CDI', None),           # Julie Tech - CDI (light blue)
        (7, 'philia007', 'pwd_karl901', 'CDI', None),           # Karl Sales - CDI (light blue)
        (8, 'philia008', 'pwd_laura234', 'CDD', '2025-07-20'),   # Laura Engineer - CDD expired (dark red)
        (9, 'philia009', 'pwd_marc567', 'CDD', '2025-08-01'),   # Marc Operations - CDD 9 days left (yellow)
        (10, 'philia010', 'pwd_nina890', 'CDD', '2025-09-15'), # Nina Support - CDD normal (light green)
        (11, 'philia011', 'pwd_oliver123', 'CDI', None),         # Oliver Field - CDI (light blue)
        (12, 'philia012', 'pwd_paula456', 'CDD', '2025-07-25')  # Paula Admin - CDD 2 days left (light red)
    ]

    # --- Execute Inserts ---
    # Using executemany for efficient bulk insertion
    cursor.executemany("INSERT INTO roles (role_name, description) VALUES (%s, %s);", roles_data)
    cursor.executemany("INSERT INTO users (username, password_hash, full_name, email, role_id) VALUES (%s, %s, %s, %s, %s);", users_data)
    cursor.executemany("INSERT INTO secteurs (secteur_name, manager_id, description) VALUES (%s, %s, %s);", secteurs_data)
    cursor.executemany("INSERT INTO workers (worker_id, full_name, secteur_id, status) VALUES (%s, %s, %s, %s);", workers_data)
    cursor.executemany("INSERT INTO phones (asset_tag, imei, serial_number, manufacturer, model, status) VALUES (%s, %s, %s, %s, %s, %s);", phones_data)
    cursor.executemany("INSERT INTO sim_cards (iccid, carrier, puk, status) VALUES (%s, %s, %s, %s);", sim_cards_data)
    cursor.executemany("INSERT INTO phone_numbers (phone_number, sim_card_id, status) VALUES (%s, %s, %s);", phone_numbers_data)
    cursor.executemany("INSERT INTO assignments (phone_id, sim_card_id, worker_id) VALUES (%s, %s, %s);", assignments_data)
    cursor.executemany("INSERT INTO phone_requests (requester_id, employee_name, department, position, request_reason, phone_type_preference, urgency_level, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", phone_requests_data)
    cursor.executemany("INSERT INTO rh_data (worker_id, id_philia, mdp_philia, contract_type, contract_end_date) VALUES (%s, %s, %s, %s, %s);", rh_data)

    print("✅ Sample data inserted successfully.")


def main():
    """Main function to orchestrate the database initialization."""
    print("--- Starting Mobile Fleet Database Initialization ---")
    conn = None
    try:
        conn = get_db_connection()
        if conn is None: return

        with conn.cursor() as cursor:
            drop_tables(cursor)
            create_schema(cursor)
            insert_sample_data(cursor)

        conn.commit()
        print("\n🎉 Database initialization complete. All changes have been committed.")

    except (Exception, psycopg2.Error) as error:
        print(f"\n❌ A critical error occurred: {error}")
        if conn:
            print("   - Rolling back changes.")
            conn.rollback()

    finally:
        if conn:
            conn.close()
            print("\n🔌 Database connection closed.")
        print("--- Initialization Script Finished ---")

if __name__ == "__main__":
    main()
