

from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from helpers import login_required, get_db_connection
from bcrypt import gensalt, hashpw, checkpw


STATUS_CLASSES = {
    "Aperta": "text-bg-secondary",
    "In attesa": "text-bg-warning",
    "In lavorazione": "text-bg-primary",
    "Completata": "text-bg-success",
}


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
    return render_template('/index.html')

@app.route('/landing')
def landing():
    return render_template('/landing.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == 'GET':
        return render_template('/login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username:
            message = 'Nome utente richiesto'
            return render_template('/login.html', username_message=message)
        elif not password:
            message = 'Password richiesta'
            return render_template('/login.html', password_message=message)
        else:
            connection = get_db_connection()
            user = connection.execute ('SELECT * FROM users WHERE username = ?',(username,)).fetchone()
            connection.close()
            if user is None or not checkpw(password.encode('utf-8'),user['password']):
                message = 'Nome utente o password non corretti'
                return render_template('/login.html',check_message=message)
            else:
                session['user_id'] = user['id']
            return redirect('/')



@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == 'GET':
        return render_template('/register.html')
    
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not username:
            message = 'Nome utente richiesto'
            return render_template('/register.html', username_message=message)
        elif len(username) < 3:
            message = 'Nome utente non valido'
            return render_template('/register.html', username_message=message)
        elif not password:
            message = 'Password richiesta'
            return render_template('/register.html', password_message=message)
        elif len(password) < 8:
            message = 'Password non valida'
            return render_template('/register.html', password_message=message)
        elif password != confirmation:
            message = 'Password non valida'
            return render_template('/register.html', password_message=message)
        else:
            connection = get_db_connection()
            try: 
                pw = hashpw(password.encode('utf-8'), gensalt())
                connection.execute('INSERT INTO users (username, password) VALUES (?,?)',(username, pw))
            except:
                message = 'Nome utente già esistente'
                connection.close()
                return render_template('/register.html',username_message=message)
            else:
                connection.commit()
                connection.close()
            return redirect('/login')
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect ('/')


@app.route("/tasks")
@login_required
def tasks():
    user_id = session['user_id']
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ? ',(user_id,)).fetchall()
    conn.close()
    return render_template('/tasks.html', tasks=tasks)

@app.route('/tasks/<int:task_id>')
@login_required
def task_detail(task_id):
    user_id = session['user_id']
    conn = get_db_connection()
    task = conn.execute(' SELECT * FROM tasks WHERE id = ? AND user_id = ?',(task_id, user_id)).fetchone()
    notes = conn.execute('SELECT * FROM notes WHERE task_id = ? ORDER BY created_at DESC',(task_id,)).fetchall()
    status_history = conn.execute('SELECT * FROM status_history WHERE task_id = ? ORDER BY changed_at DESC',(task_id,)).fetchall()
    conn.close()
    return render_template('/task_detail.html', task=task, notes=notes, status_history=status_history, status_classes=STATUS_CLASSES)

if __name__ == "__main__":
    app.run(debug=True)