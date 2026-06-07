"""
Migration: Change tasks.patient_id from Integer to String to match patients.id (UUID)
PostgreSQL version
"""
from database import engine
from sqlalchemy import text

def migrate():
    with engine.begin() as conn:
        # Step 1: Drop FK constraint if exists
        try:
            conn.execute(text("""
                ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_patient_id_fkey
            """))
            print("Dropped FK constraint")
        except Exception as e:
            print(f"FK constraint drop skipped: {e}")

        # Step 2: Alter column type from INTEGER to VARCHAR
        conn.execute(text("""
            ALTER TABLE tasks
            ALTER COLUMN patient_id TYPE VARCHAR USING patient_id::VARCHAR
        """))
        print("Column type changed to VARCHAR")

        # Step 3: Re-add FK constraint
        conn.execute(text("""
            ALTER TABLE tasks
            ADD CONSTRAINT tasks_patient_id_fkey
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        """))
        print("FK constraint re-added")

        # Verify
        result = conn.execute(text("SELECT COUNT(*) FROM tasks"))
        count = result.fetchone()[0]
        print(f"Migration complete! Tasks count: {count}")

if __name__ == "__main__":
    migrate()
