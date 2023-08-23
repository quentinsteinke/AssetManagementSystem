import sqlite3
import shutil
import os

# Assuming you have a config or a known path for your DB
db_path = os.path.join(os.path.dirname(__file__), 'Databases', '3d_project_database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the AssetFiles table
# Create a new temporary table with the desired structure
cursor.execute('''
CREATE TABLE IF NOT EXISTS Assets_temp (
    AssetID INTEGER PRIMARY KEY,
    AssetName TEXT NOT NULL,
    AssetType TEXT,
    CurrentVersion TEXT,
    LastModifiedDate TEXT,
    ResponsibleTeamMember TEXT,
    AssetStatus TEXT,
    SVNLink TEXT,
    Notes TEXT,
    ProjectID INTEGER,
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID) ON DELETE CASCADE
)
''')

# Copy data from the old Assets table to the new temporary table
cursor.execute('''
INSERT INTO Assets_temp (AssetID, AssetName, AssetType, CurrentVersion, LastModifiedDate, ResponsibleTeamMember, AssetStatus, SVNLink, Notes)
SELECT AssetID, AssetName, AssetType, CurrentVersion, LastModifiedDate, ResponsibleTeamMember, AssetStatus, SVNLink, Notes FROM Assets
''')

# Delete the old Assets table
cursor.execute('DROP TABLE Assets')

# Rename the new temporary table to Assets
cursor.execute('ALTER TABLE Assets_temp RENAME TO Assets')

# Commit the changes and close the connection
conn.commit()
conn.close()
