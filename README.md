# 🗃️ DeskManager

Applicazione web per gestire pratiche e attività di lavoro: stati, note, scadenze. L'ho fatta pensando a chi ha più pratiche aperte in contemporanea e deve capire a colpo d'occhio cosa è urgente, cosa è scaduto e cosa è successo di recente.

Ogni pratica ha una priorità e uno stato che segue un percorso obbligato — non si può passare da "Completata" a "In lavorazione" per sbaglio — con lo storico di tutti i passaggi e le note aggiunte nel tempo.

## Demo

🔗 [Link al deploy live](https://deskmanager.onrender.com)

### ⚠️ Nota sulla demo live

Il piano gratuito di Render non ha disco persistente, quindi il database si azzera ogni volta che il servizio si riavvia. È normale, non un bug. L'utente demo (`demo` / `demo1234`) viene ricreato in automatico a ogni riavvio, ma qualsiasi cosa crei durante la sessione (pratiche, nuovi utenti) sparirà al riavvio successivo. Usala per girarci dentro, non per salvarci dati veri.

## Funzionalità

- Dashboard con il conteggio delle pratiche per stato, quelle scadute, quelle in scadenza nei prossimi 7 giorni e un feed con le ultime attività
- Elenco pratiche in tabella, ordinabile e filtrabile per priorità e stato, con ricerca libera
- Pagina di dettaglio con lo storico completo degli stati, le note in accordion e un form unico per aggiungere una nota e/o cambiare stato
- Transizioni di stato controllate (sotto trovi il dettaglio)
- Creazione, modifica ed eliminazione delle pratiche
- Login con sessione lato server e password hashate con bcrypt — ogni utente vede solo le proprie pratiche

## Stack tecnico

| Livello  | Tecnologie                                  |
| -------- | ------------------------------------------- |
| Backend  | Flask, Flask-Session, sqlite3               |
| Auth     | bcrypt                                      |
| Frontend | Bootstrap 5, DataTables.js, Bootstrap Icons |
| Database | SQLite                                      |

## Il flusso degli stati

Una pratica nasce sempre "Aperta" e da lì può andare solo dove è previsto:

- Aperta → In attesa, In lavorazione, Completata
- In attesa → In lavorazione, Completata
- In lavorazione → In attesa, Completata
- Completata → Aperta (si può riaprire)

Nel dettaglio pratica il form mostra solo le transizioni valide da quello stato — le altre non sono nemmeno selezionabili. Ogni cambio finisce nello storico con data e ora.

## Come eseguirlo in locale

```bash
git clone https://github.com/Sara-Reb/DeskManager.git
cd DeskManager

python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

Crea un file `.env` nella root del progetto:

```env
SECRET_KEY=una-chiave-casuale-lunga-e-sicura
```

E avvia:

```bash
python app.py
```

L'app parte su `http://127.0.0.1:5000`. Al primo avvio il database viene creato e popolato con dati di esempio, quindi puoi entrare subito con l'utente demo:

- **username:** `demo`
- **password:** `demo1234`

## Formattazione codice

I template Jinja sono formattati con [Prettier](https://prettier.io) e il plugin [prettier-plugin-jinja-template](https://github.com/davidodenwald/prettier-plugin-jinja-template), che permette a Prettier di capire la sintassi Jinja senza romperla. La configurazione è in `.prettierrc`.

```bash
npm install
npx prettier --write templates/
```

## Limiti noti

- Niente protezione CSRF sui form
- Niente rate-limit sui tentativi di login
- Nessuna test suite automatizzata, per ora

## Sviluppi futuri

- Export delle pratiche in CSV/PDF
- Notifiche per le scadenze imminenti
- Gestione multi-utente con ruoli, per lavorarci in team
