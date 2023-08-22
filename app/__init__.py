from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os


app = Flask(__name__, template_folder='static/templates')

@app.route('/')
def index():
    # Fetch assets from the database
    db_path = os.path.join('Databases', '3d_project_database.db')
    print(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Assets')
    assets = cursor.fetchall()
    conn.close()
    return render_template('index.html', assets=assets)

@app.route('/add_asset', methods=['POST'])
def add_asset():
    # Insert asset into the database
    asset_data = request.form
    db_path = os.path.join('Databases', '3d_project_database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Assets (AssetName, AssetType, CurrentVersion, LastModifiedDate, ResponsibleTeamMember, AssetStatus, SVNLink, Notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (asset_data['asset_name'], asset_data['asset_type'], asset_data['current_version'], 
          asset_data['last_modified_date'], asset_data['team_member'], asset_data['status'], 
          asset_data['svn_link'], asset_data['notes']))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
