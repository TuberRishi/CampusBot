import sqlite3
import datetime

DB_NAME = "college_events.db"
TABLE_NAME = "events_view"

def setup_database():
    """
    Sets up the SQLite database and populates it with sample event data.
    """
    print(f"Setting up database '{DB_NAME}'...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Drop the table if it already exists to ensure a clean setup
    cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
    print(f"Dropped existing table '{TABLE_NAME}' (if any).")

    # Create the events table (using the schema provided by the user)
    create_table_sql = f"""
    CREATE TABLE {TABLE_NAME} (
        event_id TEXT PRIMARY KEY NOT NULL,
        event_name TEXT NOT NULL,
        event_description TEXT,
        location TEXT NOT NULL,
        start_datetime TEXT NOT NULL,
        end_datetime TEXT,
        last_updated TEXT NOT NULL
    );
    """
    cursor.execute(create_table_sql)
    print(f"Table '{TABLE_NAME}' created successfully.")

    # Sample data to insert
    now = datetime.datetime.now().isoformat()
    sample_events = [
        ('techfest25', 'Tech Fest 2025', 'Annual technology festival with competitions and workshops.', 'Main Auditorium', '2025-10-10T09:00:00', '2025-10-11T17:00:00', now),
        ('guestlec01', 'Guest Lecture on AI', 'A talk by Dr. Eva Wallace on the future of AI.', 'Seminar Hall A', '2025-09-25T15:00:00', '2025-09-25T16:30:00', now),
        ('sportsday25', 'Annual Sports Day', 'Track and field events for all students.', 'College Sports Ground', '2025-11-05T08:00:00', '2025-11-05T18:00:00', now),
        ('codecomp03', 'CodeClash Coding Competition', 'A 3-hour competitive programming contest.', 'Computer Lab 3', '2025-10-10T10:00:00', '2025-10-10T13:00:00', now),
        ('artx25', 'Art Exhibition', 'Display of student artwork.', 'Fine Arts Building', '2025-09-15T11:00:00', '2025-09-20T17:00:00', now)
    ]

    # Insert the sample data
    insert_sql = f"INSERT INTO {TABLE_NAME} VALUES (?, ?, ?, ?, ?, ?, ?)"
    cursor.executemany(insert_sql, sample_events)
    print(f"Inserted {len(sample_events)} sample events.")

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    setup_database()
