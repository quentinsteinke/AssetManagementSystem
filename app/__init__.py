from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os


app = Flask(__name__, template_folder='static/templates')

@app.route('/')
def index():
    # Fetch assets from the database
    db_path = os.path.join('Databases', '3d_project_database.db')
    # make db_path absolute
    db_path = os.path.join(os.path.dirname(__file__), db_path)

    print(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Assets')
    assets = cursor.fetchall()
    conn.close()
    return render_template('index.html', assets=assets)


@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        print(request.form)
        asset_data = request.form

        asset_name = asset_data.get('asset_name')
        if not asset_name or asset_name.strip() == '':
            return 'Asset name cannot be empty', 400
        
        # Insert asset into the database
        asset_data = request.form
        db_path = os.path.join('Databases', '3d_project_database.db')
        # make db_path absolute
        db_path = os.path.join(os.path.dirname(__file__), db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Assets (AssetName, AssetType, CurrentVersion, LastModifiedDate, ResponsibleTeamMember, AssetStatus, SVNLink, Notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset_data['asset_name'],
            asset_data['asset_type'],
            asset_data['current_version'],
            asset_data['last_modified_date'],
            asset_data['responsible_team_member'],
            asset_data['asset_status'],
            asset_data['svn_link'],
            asset_data['notes']
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('add_asset.html')


@app.route('/view_assets')
def view_assets():
    db_path = os.path.join('Databases', '3d_project_database.db')
    db_path = os.path.join(os.path.dirname(__file__), db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Assets')
    assets = cursor.fetchall()
    conn.close()

    return render_template('view_assets.html', assets=assets)


if __name__ == '__main__':
    app.run(debug=True)
