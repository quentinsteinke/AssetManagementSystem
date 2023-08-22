from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import shutil
import os


app = Flask(__name__, template_folder='static/templates')

@app.route('/')
def index():
    # Fetch assets from the database
    db_path = os.path.join('Databases', '3d_project_database.db')
    # make db_path absolute
    db_path = os.path.join(os.path.dirname(__file__), db_path)

    # print(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Assets')
    assets = cursor.fetchall()
    conn.close()
    return render_template('index.html', assets=assets)


@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        asset_data = request.form
        asset_name = asset_data.get('asset_name')
        
        if not asset_name or asset_name.strip() == '':
            return 'Asset name cannot be empty', 400

        # Insert asset into the database
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
        
        asset_id = cursor.lastrowid
        # print(f"Asset ID: {asset_id}")

        uploaded_file = request.files.get('asset_file')
        if uploaded_file:
            app_folder = os.path.dirname(__file__)
            asset_folder = os.path.join(app_folder, 'static', 'assets', str(asset_id))
            # print(f"Creating folder: {asset_folder}")
            os.makedirs(asset_folder, exist_ok=True)

            file_path = os.path.join(asset_folder, uploaded_file.filename)
            # print(f"Saving file to: {file_path}")
            uploaded_file.save(file_path)
            
            # Add a record in the AssetFiles table
            cursor.execute('''
            INSERT INTO AssetFiles (AssetID, FileName, FileType, Description)
            VALUES (?, ?, ?, ?)
            ''', (asset_id, uploaded_file.filename, 'photo', 'User uploaded photo'))
        
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
    # print(assets)
    conn.close()

    return render_template('view_assets.html', assets=assets)


@app.route('/view_asset/<int:asset_id>', methods=['GET'])
def view_asset(asset_id):
    db_path = os.path.join('Databases', '3d_project_database.db')
    db_path = os.path.join(os.path.dirname(__file__), db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Assets WHERE AssetID=?", (asset_id,))
    asset_tuple = cursor.fetchone()

    asset = {
        "AssetID": asset_tuple[0],
        "AssetName": asset_tuple[1],
        "AssetType": asset_tuple[2],
        "CurrentVersion": asset_tuple[3],
        "LastModifiedDate": asset_tuple[4],
        "ResponsibleTeamMember": asset_tuple[5],
        "AssetStatus": asset_tuple[6],
        "SVNLink": asset_tuple[7],
        "Notes": asset_tuple[8]
    }

    cursor.execute("SELECT * FROM AssetFiles WHERE AssetID=?", (asset_id,))
    files = cursor.fetchall()
    print(f"-------------------- {files}")

    conn.close()

    return render_template('view_asset.html', asset=asset, files=files, asset_id=asset_id)


@app.route('/delete_assets', methods=['GET', 'POST'])
def delete_assets():
    selected_assets = request.form.getlist('selected_assets')
    db_path = os.path.join('Databases', '3d_project_database.db')
    db_path = os.path.join(os.path.dirname(__file__), db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for asset_id in selected_assets:
        # Delete associated files from filesystem
        asset_folder = os.path.join(os.path.dirname(__file__), 'static', 'assets', str(asset_id))
        if os.path.exists(asset_folder):
            shutil.rmtree(asset_folder)
            
        # Delete records from AssetFiles table
        cursor.execute("DELETE FROM AssetFiles WHERE AssetID=?", (asset_id,))
        
        # Delete the asset from Assets table
        cursor.execute("DELETE FROM Assets WHERE AssetID=?", (asset_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_assets'))


if __name__ == '__main__':
    app.run(debug=True)
