from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Default admin user (if not already present)
def create_default_admin():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = "ketan"')
    if cursor.fetchone() is None:
        cursor.execute('''
        INSERT INTO users (username, password, role) VALUES (?, ?, ?)
        ''', ('ketan', 'Atmiya@369', 'admin'))
        conn.commit()
    conn.close()

create_default_admin()

# Home (login page)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('index.html')

# Dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

# User creation page (for admin)
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO users (username, password, role) VALUES (?, ?, ?)
        ''', (username, password, role))
        conn.commit()
        conn.close()
        
        flash(f'User {username} created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('user_creation.html')

# File upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('upload.html')

# File download page
@app.route('/download/<filename>')
def download_file(filename):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    return send_from_directory('uploads', filename)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os

# Assuming other code (imports, app setup, routes) is already defined

# Directory where uploaded files are stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# File download page - Displays list of uploaded files
@app.route('/download')
def download_file():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Ensure the user is logged in
    
    # List files in the 'uploads' directory
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('download.html', files=files)

# Route for the download page (lists available files)
@app.route('/download')
def download_page():
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Ensure the user is logged in
    
    # List all files in the 'uploads' folder
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('download.html', files=files)

# Route for downloading a specific file (this should not conflict with download_page)
@app.route('/download/<filename>')
def download_file(filename):
    if 'user_id' not in session:
        return redirect(url_for('index'))  # Ensure user is logged in
    
    # Check if the file exists and send it for download
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        flash("File not found!", "danger")
        return redirect(url_for('download_page'))


    
# Login route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]  # Store user role in session
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('index.html')

@app.route('/download')
def download_page():
    print("In download_page route")  # Debugging
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('download.html', files=files)


