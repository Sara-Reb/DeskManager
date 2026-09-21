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
        d = lambda offset: (today + dt.timedelta(days=offset)).isoformat()

        demo_tasks = [
            ('Rinnovo polizza auto - Cliente Rossi',           'Alta',  'Aperta',         d(-5)),
            ('Verifica documenti sinistro Bianchi',            'Alta',  'In lavorazione', d(-2)),
            ('Preventivo RC professionale - Studio Verdi',     'Media', 'In attesa',      d(-1)),
            ('Emissione polizza infortuni - Ferrari',          'Bassa', 'Completata',     d(0)),
            ('Contatto cliente per rinnovo scaduto',           'Alta',  'Aperta',         d(1)),
            ('Aggiornamento anagrafica cliente Russo',         'Bassa', 'Completata',     d(3)),
            ('Preventivo multi-garanzia - Colombo',            'Media', 'Aperta',         d(5)),
            ('Follow-up sinistro grandine - Ricci',            'Media', 'In attesa',      d(7)),
            ('Rinnovo RC auto - Marino',                       'Alta',  'In lavorazione', d(10)),
            ('Revisione polizza casa - Greco',                 'Bassa', 'Aperta',         d(14)),
            ('Predisposizione documentazione Zurich',          'Media', 'Completata',     d(20)),
            ('Solleciti pagamenti premio scaduti',             'Alta',  'Aperta',         d(-10)),
            ('Emissione polizza viaggio - Bruno',              'Bassa', 'Completata',     d(2)),
            ('Verifica copertura RC terzi - Gallo',            'Media', 'In lavorazione', d(6)),
            ('Chiusura pratica sinistro archiviata',           'Bassa', 'Completata',     d(30)),
        ]

        for title,priority,status,due_date in demo_tasks:
            cur.execute('INSERT INTO tasks(user_id, title, priority, status, due_date) VALUES(?,?,?,?,?)',(user_id, title, priority, status, due_date))
            task_id = cur.lastrowid
            cur.execute('INSERT INTO status_history (task_id, from_status, to_status) VALUES(?,?,?)', (task_id, None, status))
    conn.commit()
    conn.close()