import sqlite3

# Connect to a new SQLite database (or connect if it already exists)
conn = sqlite3.connect('3d_project_database.db')
cursor = conn.cursor()

# Create the Assets table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Assets (
    AssetID INTEGER PRIMARY KEY,
    AssetName TEXT NOT NULL,
    AssetType TEXT,
    CurrentVersion TEXT,
    LastModifiedDate TEXT,
    ResponsibleTeamMember TEXT,
    AssetStatus TEXT,
    SVNLink TEXT,
    Notes TEXT
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

"Database and Assets table created successfully."