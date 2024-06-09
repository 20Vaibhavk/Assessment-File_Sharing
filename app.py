from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
import os
from wtforms import Form, TextAreaField, validators, StringField, SubmitField
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Define the upload folder path
UPLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Desktop', 'project', 'files')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def show_files(username):
    user_folder = os.path.join(UPLOAD_FOLDER, username)
    return os.listdir(user_folder) if os.path.exists(user_folder) else []

def get_user():
    lst = []
    conn = sqlite3.connect("base.db")
    c = conn.cursor()
    for row in c.execute('SELECT username FROM data'):
        lst.append(row[0])
    conn.close()
    return lst

l = get_user()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def reg():
    return validate()

@app.route('/home', methods=['POST'])
def do_login():
    conn = sqlite3.connect("base.db")
    c = conn.cursor()
    error1 = None
    session['username'] = request.form['username']
    password = request.form['password']
    for row in c.execute('SELECT * FROM data'):
        if row[0] == session['username'] and row[1] == password:
            error2 = "Welcome, " + session['username'] + "!"
            conn.close()
            return render_template('home.html', error2=error2)
        elif row[0] != session['username'] or row[1] != password:
            error1 = "Wrong username or password! Please, try again."
    conn.commit()
    conn.close()
    return render_template('login.html', error1=error1)

@app.route('/home', methods=['GET'])
def home_page():
    error2 = "Welcome, " + session['username'] + "!"
    return render_template('home.html', error2=error2)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

def add_value(username, password, folder_password):
    conn = sqlite3.connect("base.db")
    c = conn.cursor()
    c.execute("INSERT INTO data (username, password, folder_password) VALUES (?, ?, ?)", (username, password, folder_password))
    conn.commit()
    conn.close()

def validate():
    error1 = None
    error = None
    user = request.form['user']
    password = request.form['pass']
    repeat_password = request.form['repeat_password']

    if user and password and repeat_password:
        if user in l:
            error = "This username is already used. Please, enter another username!"
        elif user not in l and (password != repeat_password or len(password) < 6):
            error = "The passwords aren't the same or the password is too short!"
        else:
            add_value(user, password, None)
            user_path = os.path.join(UPLOAD_FOLDER, user)
            os.makedirs(user_path, exist_ok=True)
            error1 = "You are successfully registered :)"
            return render_template('login.html', error1=error1)
    else:
        error = "The fields cannot be empty!"
    return render_template('register.html', error=error)

@app.route("/logout", methods=['POST'])
def logout():
    session.pop('username', None)
    return home()

@app.route("/home/directory", methods=['POST'])
def directory():
    files = show_files(session.get('username', None))
    return render_template("directory.html", files=files)

@app.route("/back", methods=['POST'])
def back():
    return redirect(url_for('home_page'))

@app.route("/delete", methods=['GET', 'POST'])
def delete():
    if request.method == 'GET':
        lst = show_files(session.get('username'))
        return render_template("delete.html", lst=lst)
    elif request.method == 'POST':
        choose = str(request.form.get('choose'))
        os.remove(os.path.join(UPLOAD_FOLDER, session.get("username", None), choose))
        return redirect(url_for('home_page'))

@app.route("/remove", methods=['POST'])
def remove():
    choose = request.form.get('choose')
    os.remove(os.path.join(UPLOAD_FOLDER, session.get("username", None), choose))
    return redirect(url_for('home_page'))

@app.route("/change", methods=['GET', 'POST'])
def change():
    if request.method == 'GET':
        return render_template("change.html")
    elif request.method == 'POST':
        conn = sqlite3.connect("base.db")
        c = conn.cursor()
        
        # Ensure the 'new_password' and 'repeat_password' fields are present in the form
        if 'new_password' in request.form and 'repeat_password' in request.form:
            new_password = request.form['new_password']
            repeat_password = request.form['repeat_password']
            
            # Check if the passwords match
            if new_password == repeat_password:
                c.execute("UPDATE data SET folder_password = ? WHERE username = ?", (new_password, session.get('username')))
                flash("Password refreshed successfully!", "success")
            else:
                flash("Passwords aren't the same!", "error")
        else:
            flash("Required fields are missing!", "error")

        conn.commit()
        conn.close()
        return render_template("change.html")

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('upload.html')

@app.route('/uploader', methods=['GET', 'POST'])
def uploadd_file():
    if 'username' not in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        f = request.files['file']
        user_folder = os.path.join(UPLOAD_FOLDER, session.get('username', None))
        
        # Ensure the user folder exists
        if not os.path.exists(user_folder):
            os.makedirs(user_folder, exist_ok=True)
        
        # Save the file
        f.save(os.path.join(user_folder, secure_filename(f.filename)))
        return render_template("uploader.html")

@app.route('/download', methods=['GET', 'POST'])
def download():
    if request.method == 'GET':
        return render_template("download.html")
    elif request.method == 'POST':
        users_name = request.form.get('users_name')
        folder_password = request.form.get('folder_password')
        if not users_name or not folder_password:
            flash("Please provide both username and folder password.", "error")
            return render_template("download.html")

        conn = sqlite3.connect("base.db")
        c = conn.cursor()
        for row in c.execute('SELECT * FROM data'):
            if users_name == row[0] and folder_password == row[2]:
                session['users_name'] = users_name
                spisok = show_files(users_name)
                conn.close()
                return render_template("downloading.html", spisok=spisok)
            #elif users_name != row[0] or folder_password != row[2]:
                #flash("Invalid data!", "error")
        conn.close()
        return render_template("download.html")

@app.route('/downloading', methods=['GET', 'POST'])
def downloading():
    return render_template("downloading.html")

@app.route('/download_file', methods=['GET', 'POST'])
def download_file():
    filename = request.form.get('filename')
    if filename:
        directory = os.path.join(UPLOAD_FOLDER, session.get("users_name", None))
        return send_from_directory(directory, filename)
    return redirect(url_for('download'))

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='127.0.0.1', port=4000)
