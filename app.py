"""File server"""
from flask import Flask, request, redirect, render_template

app = Flask(__name__)


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.files = {}


class DataStore:
    """simple in-memory filestore, fix bugs as needed"""
    def __init__(self):
        self.users = {}

    def get_user_creds(self, user):
        """gets a users credentials from the data store"""
        return self.users[user].password

    def get_user_files(self, user):
        """lists users files"""
        return list(self.users[user].files.keys())

    def put_user_credentials(self, user, cred):
        """saves a users credentials to the data store"""
        new_user = User(user, cred)
        self.users[user] = new_user

    def get_user_file(self, user, filename):
        """gets a users file by name, returns None if user or file doesn't exist"""
        try:
            return self.users[user].files[filename]
        except:
            return None

    def put_user_file(self, user, filename, data):
        """stores file data for user/file"""
        self.users[user].files[filename] = data

    def delete_user_file(self, user, filename):
        """delete a users file"""
        try:
            del self.users[user].files[filename]
        except:
            pass


db = DataStore()
session = {
    'username': ''
}


@app.route('/')
def landing():
    if session['username'] == '' or db.get_user_creds(session['username']) is None:
        return render_template('index.html')
    else:
        return redirect('/files')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = ''
        if username is None or password is None:
            error = "Please enter both username and password."
        elif len(username) < 3 or len(username) > 20 or not str(username).isalnum():
            error = "Username must be 3 to 20 alphanumeric characters."
        elif db.users.get(username, None) is not None:
            error = "Username taken."
        elif len(password) < 8:
            error = "Password must be at least 8 characters"

        if error == '':
            db.put_user_credentials(username, password)
            return redirect('/')
        else:
            return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = ''
        if username is None or password is None:
            error = "Please enter both username and password."
        elif db.users.get(username, None) is None:
            error = "Username not recognized."
        elif password != db.get_user_creds(username):
            error = "Invalid password."

        if error == '':
            session['username'] = username
            return redirect('/files')
        else:
            return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session['username'] = ''
    return redirect('/')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if session['username'] != '':
        if request.method == 'GET':
            return render_template('upload.html')
        if request.method == 'POST':
            file = request.files['file']
            db.put_user_file(session['username'], file.filename, file.read())
            return redirect('/files')
    else:
        return redirect('/')


@app.route('/files')
def files():
    if session['username'] != '':
        username = session['username']
        user_files = db.get_user_files(username)
        return render_template('files.html', user=username, files=user_files)
    else:
        return redirect('/')


@app.route('/files/<filename>')
def show_file(filename):
    if session['username'] != '':
        username = session['username']
        return db.get_user_file(username, filename)
    else:
        return redirect('/')


@app.route('/delete/<filename>')
def delete_file(filename):
    if session['username'] != '':
        username = session['username']
        db.delete_user_file(username, filename)
        return redirect('/files')
    else:
        return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
