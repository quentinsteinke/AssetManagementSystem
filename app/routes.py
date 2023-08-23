from app import app
import sqlite3
import shutil
import os
from flask import render_template, request, redirect, url_for



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



@app.route('/add_asset', defaults={'project_id': None}, methods=['GET', 'POST'])
@app.route('/add_asset/<int:project_id>', methods=['GET', 'POST'])
def add_asset(project_id):
    db_path = os.path.join('Databases', '3d_project_database.db')
    db_path = os.path.join(os.path.dirname(__file__), db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if request.method == 'POST':
        asset_name = request.form.get('AssetName')
        asset_type = request.form.get('AssetType')
        current_version = request.form.get('CurrentVersion')
        last_modified_date = request.form.get('LastModifiedDate')
        responsible_team_member = request.form.get('ResponsibleTeamMember')
        asset_status = request.form.get('AssetStatus')
        project_id = request.form.get('ProjectID') or project_id  # Use the provided project_id if not set in form

        cursor.execute('''
            INSERT INTO Assets (AssetName, AssetType, CurrentVersion, LastModifiedDate, ResponsibleTeamMember, AssetStatus, ProjectID)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (asset_name, asset_type, current_version, last_modified_date, responsible_team_member, asset_status, project_id))

        conn.commit()
        conn.close()

        return redirect(url_for('view_project', project_id=project_id))

    # Fetch all projects for the dropdown
    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()
    conn.close()

    return render_template('add_asset.html', projects=projects, selected_project_id=project_id)


@app.route('/view_assets')
def view_assets():
    db_path = os.path.join('Databases', '3d_project_database.db')
    db_path = os.path.join(os.path.dirname(__file__), db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Assets')

    sort_by = request.args.get('sort-by')
    direction = request.args.get('direction', default='asc')

    sort_column_mapping = {
        'select': 'AssetID',
        'asset-name': 'AssetName',
        'asset-type': 'AssetType',
        'current-version': 'CurrentVersion',
        'last-modified-date': 'LastModifiedDate',
        'responsible-team-member': 'ResponsibleTeamMember',
        'asset-status': 'AssetStatus',
        'responsible-team-member': 'ResponsibleTeamMember',
        'project-name': 'ProjectName',
        'status': 'Status'
    }

    order_by_column = sort_column_mapping.get(sort_by, 'AssetName')

    assets = cursor.execute(f'SELECT * FROM Assets ORDER BY {order_by_column} {direction}').fetchall()
    
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


@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        # Extract form data
        project_name = request.form.get('ProjectName')
        project_description = request.form.get('ProjectDescription')
        start_date = request.form.get('StartDate')
        end_date = request.form.get('EndDate')
        status = request.form.get('Status')

        # Validate form data (basic validation for now)
        if not project_name or project_name.strip() == '':
            return 'Project name cannot be empty', 400

        # Insert project into the database
        db_path = os.path.join('Databases', '3d_project_database.db')
        db_path = os.path.join(os.path.dirname(__file__), db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO Projects (ProjectName, ProjectDescription, StartDate, EndDate, Status)
        VALUES (?, ?, ?, ?, ?)
        ''', (project_name, project_description, start_date, end_date, status))
        
        conn.commit()
        conn.close()

        # Redirect to a confirmation page or list of projects (to be implemented)
        return redirect(url_for('index'))

    # If GET request, render the form
    return render_template('create_project.html')


@app.route('/view_projects', methods=['GET'])
def view_projects():
    # Fetch all projects from the database
    db_path = os.path.join('Databases', '3d_project_database.db')
    db_path = os.path.join(os.path.dirname(__file__), db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()
    
    conn.close()

    # Render the template with the projects data
    return render_template('view_projects.html', projects=projects)


@app.route('/view_project/<int:project_id>', methods=['GET'])
def view_project(project_id):
    # Fetch the project details from the database
    db_path = os.path.join('Databases', '3d_project_database.db')
    db_path = os.path.join(os.path.dirname(__file__), db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Projects WHERE ProjectID = ?', (project_id,))
    project = cursor.fetchone()

    # Fetch the assets associated with this project
    cursor.execute('SELECT * FROM Assets WHERE ProjectID = ?', (project_id,))
    assets = cursor.fetchall()
    
    conn.close()

    # Render the template with the project and assets data
    return render_template('view_project.html', project=project, assets=assets)


@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    # Delete the project from the database
    db_path = os.path.join('Databases', '3d_project_database.db')
    db_path = os.path.join(os.path.dirname(__file__), db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM Projects WHERE ProjectID = ?', (project_id,))
    
    conn.commit()
    conn.close()

    # Redirect to the list of all projects
    return redirect(url_for('view_projects'))


@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    # Fetch the current project details from the database
    db_path = os.path.join('Databases', '3d_project_database.db')
    db_path = os.path.join(os.path.dirname(__file__), db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Update project in the database with form data
        project_name = request.form.get('ProjectName')
        project_description = request.form.get('ProjectDescription')
        start_date = request.form.get('StartDate')
        end_date = request.form.get('EndDate')
        status = request.form.get('Status')

        cursor.execute('''
        UPDATE Projects 
        SET ProjectName = ?, ProjectDescription = ?, StartDate = ?, EndDate = ?, Status = ?
        WHERE ProjectID = ?
        ''', (project_name, project_description, start_date, end_date, status, project_id))
        
        conn.commit()
        conn.close()

        # Redirect to the list of all projects or project details
        return redirect(url_for('view_projects'))

    cursor.execute('SELECT * FROM Projects WHERE ProjectID = ?', (project_id,))
    project = cursor.fetchone()
    conn.close()

    # Render the editing template with the current project data
    return render_template('edit_project.html', project=project)