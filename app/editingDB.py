import sqlite3
import os

# Assuming you have a config or a known path for your DB
db_path = os.path.join(os.path.dirname(__file__), 'Databases', '3d_project_database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the AssetFiles table
cursor.execute('''
CREATE TABLE IF NOT EXISTS AssetFiles (
    FileID INTEGER PRIMARY KEY AUTOINCREMENT,
    AssetID INTEGER,
    FileName TEXT NOT NULL,
    FileType TEXT,
    Description TEXT,
    FOREIGN KEY (AssetID) REFERENCES Assets(AssetID) ON DELETE CASCADE
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
