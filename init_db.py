import sqlite3
from helpers import get_db_connection
from bcrypt import hashpw, gensalt
import datetime as dt


def init_and_seed():
    conn = get_db_connection()

    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())

    count = conn.execute('SELECT COUNT(*) AS c FROM users').fetchone()['c']
    if count == 0:
        pw = hashpw('demo1234'.encode('utf-8'), gensalt())
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('demo', pw))
        user_id = cur.lastrowid

        today = dt.date.today()
        now = dt.datetime.now()
        d = lambda offset: (today + dt.timedelta(days=offset)).isoformat()
        t = lambda hours_ago: (now - dt.timedelta(hours=hours_ago)).strftime('%Y-%m-%d %H:%M:%S')

        # (title, priority, due_date) -- niente status: nascono tutte "Aperta"
        demo_tasks = [
            ('Rinnovo polizza auto - Cliente Rossi',           'Alta',  d(-5)),
            ('Verifica documenti sinistro Bianchi',            'Alta',  d(-2)),
            ('Preventivo RC professionale - Studio Verdi',     'Media', d(-1)),
            ('Emissione polizza infortuni - Ferrari',          'Bassa', d(0)),
            ('Contatto cliente per rinnovo scaduto',           'Alta',  d(1)),
            ('Aggiornamento anagrafica cliente Russo',         'Bassa', d(3)),
            ('Preventivo multi-garanzia - Colombo',            'Media', d(5)),
            ('Follow-up sinistro grandine - Ricci',            'Media', d(7)),
            ('Rinnovo RC auto - Marino',                       'Alta',  d(10)),
            ('Revisione polizza casa - Greco',                 'Bassa', d(14)),
            ('Predisposizione documentazione Zurich',          'Media', d(20)),
            ('Solleciti pagamenti premio scaduti',             'Alta',  d(-10)),
            ('Emissione polizza viaggio - Bruno',              'Bassa', d(2)),
            ('Verifica copertura RC terzi - Gallo',            'Media', d(6)),
            ('Chiusura pratica sinistro archiviata',           'Bassa', d(30)),
        ]

        task_ids = []
        for title, priority, due_date in demo_tasks:
            cur.execute(
                "INSERT INTO tasks(user_id, title, priority, status, due_date) VALUES(?,?,'Aperta',?)",
                (user_id, title, priority, due_date)
            )
            task_id = cur.lastrowid
            task_ids.append(task_id)
            # Ogni task nasce Aperta, esattamente come new_task()
            cur.execute('INSERT INTO status_history (task_id, from_status, to_status, changed_at) VALUES (?,?,?,?)',
                        (task_id, None, 'Aperta', t(100)))

        def advance(idx, new_status, hours_ago, note=None):
            """Applica una transizione di stato valida a una task già nata Aperta,
            aggiornando sia tasks.status sia status_history, in coerenza con l'app reale."""
            task_id = task_ids[idx]
            current = conn.execute('SELECT status FROM tasks WHERE id = ?', (task_id,)).fetchone()['status']
            cur.execute('UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?',
                        (new_status, t(hours_ago), task_id))
            cur.execute('INSERT INTO status_history (task_id, from_status, to_status, changed_at) VALUES (?,?,?,?)',
                        (task_id, current, new_status, t(hours_ago)))
            if note:
                cur.execute('INSERT INTO notes (task_id, content, created_at) VALUES (?,?,?)',
                            (task_id, note, t(hours_ago)))

        # Task 1 (Rinnovo polizza Rossi): Aperta -> In lavorazione, con nota
        advance(0, 'In lavorazione', 28,
                note='Cliente contattato telefonicamente, in attesa di documentazione.')

        # Task 3 (Preventivo RC Verdi): Aperta -> In lavorazione -> In attesa
        advance(2, 'In lavorazione', 50)
        advance(2, 'In attesa', 6,
                note='In attesa di riscontro dallo Studio Verdi sui massimali richiesti.')

        # Task 8 (Follow-up sinistro grandine): Aperta -> In attesa, con nota
        advance(7, 'In attesa', 1,
                note='Foto danni ricevute, in attesa di perizia.')

        # Task 9 (Rinnovo RC Marino): Aperta -> In lavorazione
        advance(8, 'In lavorazione', 3)

        # Alcune task "Completata", per varietà nella dashboard - percorso Aperta -> Completata
        for idx, hours_ago in [(3, 75), (5, 40), (10, 15), (12, 8)]:
            advance(idx, 'Completata', hours_ago)

    conn.commit()
    conn.close()