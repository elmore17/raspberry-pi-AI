import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import psycopg2
from config import Config
from ai_text_music import model_convert_audio_to_text, moderate_text

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM users WHERE id = %s', (user_id,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1])
    return None

def get_db_connection():
    return psycopg2.connect(database="kisprod", user="postgres", password="elmore", host="localhost", port="5432")

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, filename, status, created_at FROM audio_files WHERE user_id = %s ORDER BY created_at DESC', (current_user.id,))
    files = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', files=files)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if username exists
        cur.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cur.fetchone():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        # Create new user
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)',
                   (username, generate_password_hash(password)))
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, username, password FROM users WHERE username = %s', (username,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()
        
        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1])
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and file.filename.endswith('.mp3'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the audio file
        text = model_convert_audio_to_text(filepath)
        status = 'approved' if moderate_text(text) else 'rejected'
        
        # Save to database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO audio_files (user_id, filename, text_content, status) VALUES (%s, %s, %s, %s)',
                   (current_user.id, filename, text, status))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('File uploaded and processed successfully')
    else:
        flash('Invalid file type. Please upload an MP3 file')
    
    return redirect(url_for('index'))

@app.route('/file/<int:file_id>')
@login_required
def view_file(file_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT filename, text_content, status FROM audio_files WHERE id = %s AND user_id = %s',
               (file_id, current_user.id))
    file_data = cur.fetchone()
    cur.close()
    conn.close()
    
    if not file_data:
        flash('File not found')
        return redirect(url_for('index'))
    
    return render_template('file.html', file=file_data)

if __name__ == '__main__':
    app.run(debug=True) 