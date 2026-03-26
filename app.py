

from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import sqlite3
from helpers import login_required, get_db_connection, display_date
from bcrypt import gensalt, hashpw, checkpw
import datetime as dt


STATUS_CLASSES = {
    "Aperta": "text-bg-secondary",
    "In attesa": "text-bg-warning",
    "In lavorazione": "text-bg-primary",
    "Completata": "text-bg-success",
}

STATUS_ALLOWED_TRANSITIONS = {
    "Aperta": ["In attesa", "In lavorazione",'Completata'],
    "In attesa": ["In lavorazione", "Completata"],
    "In lavorazione": [ "In attesa","Completata"],
    "Completata": ['Aperta']
}

PRIORITY_CLASSES = {
    "Bassa": "text-bg-secondary",
    "Media": "text-bg-warning",
    "Alta": "text-bg-danger"
}

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.jinja_env.filters['display_date'] = display_date

@app.route("/")
@login_required
def index():
    user_id = session['user_id']
    conn = get_db_connection()

    status_count = conn.execute('SELECT COUNT(*) AS count,status FROM tasks WHERE user_id = ? GROUP BY status',(user_id,)).fetchall()
    status_count = {row['status']: row['count'] for row in status_count}

    overdue_list = conn.execute('SELECT * FROM tasks WHERE user_id = ? AND due_date < ? AND status != "Completata" ORDER BY due_date ASC',(user_id,dt.date.today().strftime('%Y-%m-%d'))).fetchall()

    week_later = (dt.date.today() + dt.timedelta(days=7)).strftime('%Y-%m-%d')
    upcoming_list = conn.execute('SELECT * FROM tasks WHERE user_id = ? AND due_date >= ? AND due_date<=? AND status != "Completata" ORDER BY due_date ASC',(user_id,dt.date.today().strftime('%Y-%m-%d'),week_later)).fetchall()

    last_updates= conn.execute( 
        '''
        SELECT
        t.id AS task_id,
        t.title AS task_title,
        "Nota aggiunta" AS update_type,
        n.created_at AS updated_at
    FROM notes n
    JOIN tasks t ON n.task_id = t.id

    UNION ALL

    SELECT 
        t.id AS task_id,
        t.title AS task_title,
        "Stato cambiato" AS update_type,
        sh.changed_at AS updated_at
    FROM status_history sh
    JOIN tasks t ON sh.task_id = t.id
    WHERE sh.from_status IS NOT NULL

    ORDER BY updated_at DESC
    LIMIT 10
    ''').fetchall()
    conn.close()
    return render_template('/index.html', status_count=status_count, overdue_list=overdue_list, upcoming_list=upcoming_list, updates_list=last_updates)

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
                connection.execute('INSERT INTO users (username, password) VALUES (?,?)', (username, pw))
            except sqlite3.IntegrityError:
                message = 'Nome utente già esistente'
                connection.close()
                return render_template('/register.html', username_message=message)
            except Exception as e:
                app.logger.error(f"Registration error: {e}")
                message = 'Errore durante la registrazione'
                connection.close()
                return render_template('/register.html', username_message=message)
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
    selected_status = request.args.get("status") or ''
    return render_template('/tasks.html', tasks=tasks, status_classes=STATUS_CLASSES, priority_class=PRIORITY_CLASSES, selected_status=selected_status)

@app.route('/tasks/<int:task_id>',methods=['GET', 'POST'])
@login_required
def task_detail(task_id):
    if request.method == 'POST':
        content = request.form.get('content')
        status = request.form.get('status')
        user_id = session['user_id']
        conn = get_db_connection()
        row = conn.execute(
            'SELECT status FROM tasks WHERE id = ? AND user_id = ?',
            (task_id, user_id)
        ).fetchone()

        if row is None:
            conn.close()
            return redirect('/tasks')

        from_status = row['status']
        if (not content and status == from_status) or (status and status != from_status and status not in STATUS_ALLOWED_TRANSITIONS[from_status]):
            conn.close()
            return redirect(f'/tasks/{task_id}')
        else:
            if content:
                
                conn.execute('INSERT INTO notes (task_id, content) VALUES (?, ?)', (task_id, content))
                conn.execute('UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?', (task_id, user_id))
            if status and status != from_status and status in STATUS_ALLOWED_TRANSITIONS[from_status]:
                conn.execute('INSERT INTO status_history (task_id, from_status, to_status) VALUES (?, ?, ?)', (task_id, from_status, status))
                conn.execute('UPDATE tasks SET status = ? WHERE id = ? AND user_id = ?', (status, task_id, user_id))
                conn.execute('UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?', (task_id, user_id))
                
                
            conn.commit()
            conn.close()
            return redirect(f'/tasks/{task_id}')
    else:
        user_id = session['user_id']
        conn = get_db_connection()
        task = conn.execute(
            'SELECT * FROM tasks WHERE id = ? AND user_id = ?',
            (task_id, user_id)
        ).fetchone()

        if task is None:
            conn.close()
            return redirect('/tasks')
        notes = conn.execute('SELECT * FROM notes WHERE task_id = ? ORDER BY created_at DESC',(task_id,)).fetchall()
        status_history = conn.execute('SELECT * FROM status_history WHERE task_id = ? ORDER BY changed_at DESC',(task_id,)).fetchall()
        conn.close()
        return render_template('/task_detail.html', task=task, notes=notes, status_history=status_history, status_classes=STATUS_CLASSES,allowed = STATUS_ALLOWED_TRANSITIONS[task['status']], priority_class=PRIORITY_CLASSES[task['priority']])


@app.route('/new_task', methods=['GET', 'POST'])
@login_required
def new_task():
    if request.method == 'GET':
        return render_template('/new_task.html')
    if request.method == 'POST':
        title = request.form.get('title')
        priority = request.form.get('priority')
        due_date = request.form.get('due_date') or None
        note = request.form.get('note')
        user_id = session['user_id']
        if not title or not priority:
            return render_template('/new_task.html', title_message='Titolo richiesto' if not title else '', priority_message='Priorità richiesta' if not priority else '')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO tasks (user_id, title, priority, status, due_date) VALUES (?, ?, ?, ?, ?)', (user_id, title, priority, 'Aperta', due_date))
            task_id = cur.lastrowid
            cur.execute('INSERT INTO status_history (task_id, from_status, to_status) VALUES (?, ?, ?)', (task_id, None, 'Aperta'))
            if note:
                cur.execute('INSERT INTO notes (task_id, content) VALUES (?, ?)', (task_id, note))
            
            conn.commit()
            conn.close()
            return redirect(f'/tasks/{task_id}')

if __name__ == "__main__":
    app.run(debug=True)