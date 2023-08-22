from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import shutil
import os


app = Flask(__name__, template_folder='static/templates')

@app.route('/')
def index():
    db_path = os.path.join('Databases', '3d_project_database.db')
    # make db_path absolute
    db_path = os.path.join(os.path.dirname(__file__), db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total assets
    cursor.execute("SELECT COUNT(*) FROM Assets")
    total_assets = cursor.fetchone()[0]

    # Assets by type
    cursor.execute("SELECT AssetType, COUNT(*) FROM Assets GROUP BY AssetType")
    assets_by_type = cursor.fetchall()

    # Recent additions
    cursor.execute("SELECT * FROM Assets ORDER BY LastModifiedDate DESC LIMIT 5")
    recent_assets = cursor.fetchall()

    conn.close()

    return render_template('index.html', total_assets=total_assets, assets_by_type=assets_by_type, recent_assets=recent_assets)



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
    conn.row_factory = sqlite3.Row  # Set row factory
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Assets WHERE AssetID=?", (asset_id,))
    asset_row = cursor.fetchone()

    asset = {
        "AssetID": asset_row["AssetID"],
        "AssetName": asset_row["AssetName"],
        "AssetType": asset_row["AssetType"],
        "CurrentVersion": asset_row["CurrentVersion"],
        "LastModifiedDate": asset_row["LastModifiedDate"],
        "ResponsibleTeamMember": asset_row["ResponsibleTeamMember"],
        "AssetStatus": asset_row["AssetStatus"],
        "SVNLink": asset_row["SVNLink"],
        "Notes": asset_row["Notes"]
    }

    cursor.execute("SELECT * FROM AssetFiles WHERE AssetID=?", (asset_id,))
    files = cursor.fetchall()

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


@app.route('/search_assets')
def search_assets():
    query = request.args.get('query')
    db_path = os.path.join('Databases', '3d_project_database.db')
    db_path = os.path.join(os.path.dirname(__file__), db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Search for assets and their associated files
    cursor.execute("""
    SELECT Assets.*, AssetFiles.FileName
    FROM Assets
    LEFT JOIN AssetFiles ON Assets.AssetID = AssetFiles.AssetID
    WHERE Assets.AssetName LIKE ?
    """, ('%' + query + '%',))

    search_results = cursor.fetchall()

    conn.close()

    return render_template('search_results.html', search_results=search_results)


if __name__ == '__main__':
    app.run(debug=True)
