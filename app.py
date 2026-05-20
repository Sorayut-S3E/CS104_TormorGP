from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'motogp.db')


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team TEXT NOT NULL,
        rider TEXT,
        owner TEXT,
        sponsor TEXT,
        highlight TEXT,
        standing INTEGER UNIQUE
    );

    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track TEXT NOT NULL,
        highlight TEXT,
        country TEXT
    );

    CREATE TABLE IF NOT EXISTS merchandise (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL REFERENCES teams(id),
        coat REAL,
        shirt REAL,
        helmet REAL,
        cap REAL,
        image_url TEXT
    );

    -- Add image_url column to existing merchandise table (migration)
    -- SQLite ignores this if column already exists (wrapped via Python below)
    

    CREATE TABLE IF NOT EXISTS calendar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        track_id INTEGER NOT NULL REFERENCES tracks(id),
        ticket REAL,
        rider TEXT
    );

    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        calendar_id INTEGER NOT NULL REFERENCES calendar(id),
        result TEXT NOT NULL,
        standing INTEGER,
        records TEXT
    );
    """)

    # Seed data
    if c.execute('SELECT COUNT(*) FROM teams').fetchone()[0] == 0:
        teams_data = [
            (1, 'Red Bull KTM Factory Racing',     'Brad Binder / Jack Miller',              'Pierer Mobility AG', 'Red Bull',        'First KTM MotoGP win in 2020',       4),
            (2, 'Monster Energy Yamaha MotoGP',    'Fabio Quartararo / Alex Rins',           'Lin Jarvis',         'Monster Energy',  '9x World Champions',                  5),
            (3, 'Repsol Honda Team',               'Joan Mir / Luca Marini',                 'Alberto Puig',       'Repsol',          'Most successful MotoGP team',         6),
            (4, 'Ducati Lenovo Team',              'Francesco Bagnaia / Enea Bastianini',    "Gigi Dall'Igna",     'Lenovo / Ducati', 'Champions 2022-2024',                  1),
            (5, 'Aprilia Racing',                  'Aleix Espargaro / Maverick Viñales',     'Massimo Rivola',     'Aprilia',         'First pole in 2022',                  3),
            (6, 'Prima Pramac Racing',             'Jorge Martin / Franco Morbidelli',       'Paolo Campinoti',    'Prima / Pramac',  'Top satellite team',                  2),
            (7, 'Trackhouse Racing',               'Raul Fernandez / Miguel Oliveira',       'Justin Marks',       'Trackhouse',      'First full season in MotoGP in 2023', 8),
            (8, 'VR46 Racing Team',                'Marco Bezzecchi / Fabio Di Giannantonio','Pablo Nieto',        'Mooney / VR46',   "Founded by Valentino Rossi's academy", 7),
            (9, 'Gresini Racing MotoGP',           'Marc Marquez / Alex Marquez',            'Nadia Padovani',     'Gresini',         'Founded by Fausto Gresini in 1997',   9),
            (10,'LCR Honda',                       'Johann Zarco / Takaaki Nakagami',        'Lucio Cecchinello',  'Castrol Honda',   'Most successful satellite Honda team', 10),
        ]
        c.executemany("INSERT INTO teams(id,team,rider,owner,sponsor,highlight,standing) VALUES(?,?,?,?,?,?,?)", teams_data)

    if c.execute('SELECT COUNT(*) FROM tracks').fetchone()[0] == 0:
        tracks_data = [
            (1,  'Circuit de Barcelona-Catalunya',          'Fast corners, technical sector 2, great overtaking at Turn 1', 'Spain'),
            (2,  'Mugello Circuit',                         'Longest straight in MotoGP, scenic Tuscan hills, passionate Italian fans', 'Italy'),
            (3,  'Losail International Circuit',            'First night race in MotoGP history, desert setting', 'Qatar'),
            (4,  'Jerez-Ángel Nieto Circuit',              'Technical and twisty, home of Spanish fans', 'Spain'),
            (5,  'Le Mans Circuit Bugatti',                 'Unpredictable weather, historic racing venue', 'France'),
            (6,  'Assen TT Circuit',                        'Cathedral of Speed, oldest Grand Prix circuit', 'Netherlands'),
            (7,  'Sachsenring',                             'Unique anti-clockwise layout, steep elevation changes', 'Germany'),
            (8,  'Silverstone Circuit',                     'High-speed complex, challenging British weather', 'United Kingdom'),
            (9,  'Red Bull Ring',                           'Short lap, high-speed corners, spectacular scenery', 'Austria'),
            (10, 'Misano World Circuit Marco Simoncelli',   'Named after the late champion, technical layout', 'Italy'),
        ]
        c.executemany("INSERT INTO tracks(id,track,highlight,country) VALUES(?,?,?,?)", tracks_data)

    # Migration: add image columns if they don't exist yet
    existing_cols = [row[1] for row in c.execute("PRAGMA table_info(merchandise)").fetchall()]
    if 'image_url' not in existing_cols:
        c.execute("ALTER TABLE merchandise ADD COLUMN image_url TEXT")
    for col in ('coat_img', 'shirt_img', 'helmet_img', 'cap_img'):
        if col not in existing_cols:
            c.execute(f"ALTER TABLE merchandise ADD COLUMN {col} TEXT")

    if c.execute('SELECT COUNT(*) FROM merchandise').fetchone()[0] == 0:
        merch_data = [
            # id, team_id, coat, shirt, helmet, cap, image_url
            (1,  4,  299.99, 89.99, 599.99, 39.99, 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Ducati_logo.svg/320px-Ducati_logo.svg.png'),
            (2,  2,  249.99, 79.99, 549.99, 34.99, 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Yamaha_Motor_logo.svg/320px-Yamaha_Motor_logo.svg.png'),
            (3,  3,  279.99, 84.99, 579.99, 37.99, 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Honda_logo.svg/320px-Honda_logo.svg.png'),
            (4,  1,  259.99, 74.99, 559.99, 36.99, 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Red_Bull_Racing_logo.svg/320px-Red_Bull_Racing_logo.svg.png'),
            (5,  5,  229.99, 69.99, 529.99, 32.99, 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Aprilia-logo.svg/320px-Aprilia-logo.svg.png'),
            (6,  6,  219.99, 64.99, 499.99, 29.99, 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Ducati_logo.svg/320px-Ducati_logo.svg.png'),
            (7,  7,  269.99, 82.99, 559.99, 36.99, 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Aprilia_logo.svg/320px-Aprilia_logo.svg.png'),
            (8,  8,  259.99, 81.99, 539.99, 35.99, 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Ducati_logo.svg/320px-Ducati_logo.svg.png'),
            (9,  9,  289.99, 86.99, 589.99, 38.99, 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Ducati_logo.svg/320px-Ducati_logo.svg.png'),
            (10, 10, 254.99, 78.99, 544.99, 33.99, 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Honda_logo.svg/320px-Honda_logo.svg.png'),
        ]
        c.executemany("INSERT INTO merchandise(id,team_id,coat,shirt,helmet,cap,image_url) VALUES(?,?,?,?,?,?,?)", merch_data)

    if c.execute('SELECT COUNT(*) FROM calendar').fetchone()[0] == 0:
        calendar_data = [
            (1,  '2025-03-28', 3,  150.0, 'Bagnaia / Martin / Marquez'),
            (2,  '2025-04-13', 1,  200.0, 'Bagnaia / Bastianini / Martin'),
            (3,  '2025-04-27', 4,  120.0, 'Martin / Bagnaia / Espargaro'),
            (4,  '2025-05-11', 5,  130.0, 'Quartararo / Martin / Bagnaia'),
            (5,  '2025-06-01', 2,  140.0, 'Bagnaia / Bastianini / Miller'),
            (6,  '2025-06-15', 1,  135.0, 'Martin / Bagnaia / Mir'),
            (7,  '2025-06-29', 6,  125.0, 'Bagnaia / Espargaro / Martin'),
            (8,  '2025-07-06', 7,  115.0, 'Marquez / Martin / Bagnaia'),
            (9,  '2025-09-07', 9,  145.0, 'Bagnaia / Miller / Binder'),
            (10, '2025-09-21', 10, 130.0, 'Bagnaia / Martin / Bastianini'),
        ]
        c.executemany("INSERT INTO calendar(id,date,track_id,ticket,rider) VALUES(?,?,?,?,?)", calendar_data)

    if c.execute('SELECT COUNT(*) FROM results').fetchone()[0] == 0:
        results_data = [
            (1,  1,  'Qatar GP 2025 - Bagnaia wins',       1, 'Fastest lap: 1:53.247 - Bagnaia'),
            (2,  2,  'Americas GP 2025 - Bagnaia wins',    1, 'Fastest lap: 2:02.891 - Martin'),
            (3,  3,  'Spanish GP 2025 - Martin wins',      1, 'Fastest lap: 1:37.218 - Bagnaia'),
            (4,  4,  'French GP 2025 - Quartararo wins',   1, 'Fastest lap: 1:31.822 - Martin'),
            (5,  5,  'Italian GP 2025 - Bagnaia wins',     1, 'Fastest lap: 1:46.082 - Bastianini'),
            (6,  6,  'Catalan GP 2025 - Martin wins',      1, 'Fastest lap: 1:39.442 - Bagnaia'),
            (7,  7,  'Dutch GP 2025 - Marquez wins',       1, 'Fastest lap: 1:46.018 - Marquez'),
            (8,  8,  'German GP 2025 - Bagnaia wins',      1, 'Fastest lap: 1:31.447 - Martin'),
            (9,  9,  'Austrian GP 2025 - Espargaro wins',  1, 'Fastest lap: 1:38.742 - Bagnaia'),
            (10, 10, 'San Marino GP 2025 - Martin wins',   1, 'Fastest lap: 1:20.195 - Binder'),
        ]
        c.executemany("INSERT INTO results(id,calendar_id,result,standing,records) VALUES(?,?,?,?,?)", results_data)

    conn.commit()
    conn.close()


# ─── HOME ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    conn = get_db()
    teams    = conn.execute('SELECT * FROM teams ORDER BY standing').fetchall()
    upcoming = conn.execute('''
        SELECT c.id, c.date, t.track, c.ticket, c.rider
        FROM calendar c JOIN tracks t ON c.track_id = t.id
        ORDER BY c.date LIMIT 3
    ''').fetchall()
    results  = conn.execute('''
        SELECT r.id, r.result, r.standing, r.records, c.date, t.track
        FROM results r
        JOIN calendar c ON r.calendar_id = c.id
        JOIN tracks t ON c.track_id = t.id
        ORDER BY r.id DESC LIMIT 5
    ''').fetchall()
    riders   = conn.execute('SELECT id, team, rider FROM teams').fetchall()
    conn.close()
    return render_template('index.html', teams=teams, upcoming=upcoming, results=results, riders=riders)


# ─── COMPARE ────────────────────────────────────────────────────────────────
@app.route('/compare', methods=['GET', 'POST'])
def compare():
    conn = get_db()
    all_teams = conn.execute('SELECT * FROM teams').fetchall()
    rider1 = rider2 = None
    if request.method == 'POST':
        id1 = request.form.get('rider1')
        id2 = request.form.get('rider2')
        if id1:
            rider1 = conn.execute('SELECT * FROM teams WHERE id=?', (id1,)).fetchone()
        if id2:
            rider2 = conn.execute('SELECT * FROM teams WHERE id=?', (id2,)).fetchone()
    conn.close()
    return render_template('compare.html', all_teams=all_teams, rider1=rider1, rider2=rider2)


# ─── TEAMS ──────────────────────────────────────────────────────────────────
@app.route('/teams')
def teams():
    conn = get_db()
    data = conn.execute('SELECT * FROM teams ORDER BY standing').fetchall()
    conn.close()
    return render_template('teams.html', teams=data)


@app.route('/teams/add', methods=['GET', 'POST'])
def teams_add():
    if request.method == 'POST':
        conn = get_db()
        new_standing = int(request.form['standing']) if request.form['standing'] else None
        if new_standing:
            # ดัน standing ที่ชนกันขึ้นไปก่อน
            conn.execute(
                'UPDATE teams SET standing = standing + 1 WHERE standing >= ?',
                (new_standing,)
            )
        conn.execute(
            'INSERT INTO teams (team,rider,owner,sponsor,highlight,standing) VALUES (?,?,?,?,?,?)',
            (request.form['team'], request.form['rider'], request.form['owner'],
             request.form['sponsor'], request.form['highlight'], new_standing)
        )
        conn.commit(); conn.close()
        return redirect(url_for('teams'))
    return render_template('form_teams.html', action='Add', data=None)


@app.route('/teams/edit/<int:id>', methods=['GET', 'POST'])
def teams_edit(id):
    conn = get_db()
    if request.method == 'POST':
        new_standing = int(request.form['standing']) if request.form['standing'] else None
        if new_standing:
            old = conn.execute('SELECT standing FROM teams WHERE id=?', (id,)).fetchone()
            old_standing = old['standing'] if old else None
            if old_standing != new_standing:
                # ตั้ง standing เดิมเป็น NULL ก่อนเพื่อหลีกเลี่ยง UNIQUE conflict
                conn.execute('UPDATE teams SET standing = NULL WHERE id=?', (id,))
                # ดัน standing ที่ชนกันขึ้นไป
                conn.execute(
                    'UPDATE teams SET standing = standing + 1 WHERE standing >= ?',
                    (new_standing,)
                )
        conn.execute(
            'UPDATE teams SET team=?,rider=?,owner=?,sponsor=?,highlight=?,standing=? WHERE id=?',
            (request.form['team'], request.form['rider'], request.form['owner'],
             request.form['sponsor'], request.form['highlight'], new_standing, id)
        )
        conn.commit(); conn.close()
        return redirect(url_for('teams'))
    data = conn.execute('SELECT * FROM teams WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template('form_teams.html', action='Edit', data=data)


@app.route('/teams/delete/<int:id>')
def teams_delete(id):
    conn = get_db()
    conn.execute('DELETE FROM teams WHERE id=?', (id,))
    conn.commit(); conn.close()
    return redirect(url_for('teams'))


# ─── MERCHANDISE ────────────────────────────────────────────────────────────
@app.route('/merchandise')
def merchandise():
    conn = get_db()
    # JOIN merchandise → teams เพื่อดึงชื่อทีมผ่าน FK
    data = conn.execute('''
        SELECT m.id, t.team, m.coat, m.shirt, m.helmet, m.cap, m.team_id, m.image_url,
               m.coat_img, m.shirt_img, m.helmet_img, m.cap_img
        FROM merchandise m JOIN teams t ON m.team_id = t.id
        ORDER BY t.standing
    ''').fetchall()
    conn.close()
    return render_template('merchandise.html', merch=data)


@app.route('/merchandise/add', methods=['GET', 'POST'])
def merchandise_add():
    conn = get_db()
    if request.method == 'POST':
        conn.execute(
            'INSERT INTO merchandise (team_id,coat,shirt,helmet,cap,image_url,coat_img,shirt_img,helmet_img,cap_img) VALUES (?,?,?,?,?,?,?,?,?,?)',
            (request.form['team_id'], request.form['coat'], request.form['shirt'],
             request.form['helmet'], request.form['cap'],
             request.form.get('image_url', ''),
             request.form.get('coat_img', ''), request.form.get('shirt_img', ''),
             request.form.get('helmet_img', ''), request.form.get('cap_img', ''))
        )
        conn.commit(); conn.close()
        return redirect(url_for('merchandise'))
    teams = conn.execute('SELECT id, team FROM teams ORDER BY team').fetchall()
    conn.close()
    return render_template('form_merchandise.html', action='Add', data=None, teams=teams)


@app.route('/merchandise/edit/<int:id>', methods=['GET', 'POST'])
def merchandise_edit(id):
    conn = get_db()
    if request.method == 'POST':
        conn.execute(
            'UPDATE merchandise SET team_id=?,coat=?,shirt=?,helmet=?,cap=?,image_url=?,coat_img=?,shirt_img=?,helmet_img=?,cap_img=? WHERE id=?',
            (request.form['team_id'], request.form['coat'], request.form['shirt'],
             request.form['helmet'], request.form['cap'],
             request.form.get('image_url', ''),
             request.form.get('coat_img', ''), request.form.get('shirt_img', ''),
             request.form.get('helmet_img', ''), request.form.get('cap_img', ''), id)
        )
        conn.commit(); conn.close()
        return redirect(url_for('merchandise'))
    data  = conn.execute('SELECT * FROM merchandise WHERE id=?', (id,)).fetchone()
    teams = conn.execute('SELECT id, team FROM teams ORDER BY team').fetchall()
    conn.close()
    return render_template('form_merchandise.html', action='Edit', data=data, teams=teams)


@app.route('/merchandise/delete/<int:id>')
def merchandise_delete(id):
    conn = get_db()
    conn.execute('DELETE FROM merchandise WHERE id=?', (id,))
    conn.commit(); conn.close()
    return redirect(url_for('merchandise'))


# ─── TRACKS ─────────────────────────────────────────────────────────────────
@app.route('/tracks')
def tracks():
    conn = get_db()
    data = conn.execute('SELECT * FROM tracks ORDER BY country').fetchall()
    conn.close()
    return render_template('tracks.html', tracks=data)


@app.route('/tracks/add', methods=['GET', 'POST'])
def tracks_add():
    if request.method == 'POST':
        conn = get_db()
        conn.execute(
            'INSERT INTO tracks (track,highlight,country) VALUES (?,?,?)',
            (request.form['track'], request.form['highlight'], request.form['country'])
        )
        conn.commit(); conn.close()
        return redirect(url_for('tracks'))
    return render_template('form_tracks.html', action='Add', data=None)


@app.route('/tracks/edit/<int:id>', methods=['GET', 'POST'])
def tracks_edit(id):
    conn = get_db()
    if request.method == 'POST':
        conn.execute(
            'UPDATE tracks SET track=?,highlight=?,country=? WHERE id=?',
            (request.form['track'], request.form['highlight'], request.form['country'], id)
        )
        conn.commit(); conn.close()
        return redirect(url_for('tracks'))
    data = conn.execute('SELECT * FROM tracks WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template('form_tracks.html', action='Edit', data=data)


@app.route('/tracks/delete/<int:id>')
def tracks_delete(id):
    conn = get_db()
    conn.execute('DELETE FROM tracks WHERE id=?', (id,))
    conn.commit(); conn.close()
    return redirect(url_for('tracks'))


# ─── CALENDAR ───────────────────────────────────────────────────────────────
@app.route('/calendar')
def calendar():
    conn = get_db()
    # JOIN calendar → tracks เพื่อดึงชื่อสนามผ่าน FK
    data = conn.execute('''
        SELECT c.id, c.date, t.track, c.ticket, c.rider, c.track_id
        FROM calendar c JOIN tracks t ON c.track_id = t.id
        ORDER BY c.date
    ''').fetchall()
    conn.close()
    return render_template('calendar.html', calendar=data)


@app.route('/calendar/add', methods=['GET', 'POST'])
def calendar_add():
    conn = get_db()
    if request.method == 'POST':
        conn.execute(
            'INSERT INTO calendar (date,track_id,ticket,rider) VALUES (?,?,?,?)',
            (request.form['date'], request.form['track_id'], request.form['ticket'], request.form['rider'])
        )
        conn.commit(); conn.close()
        return redirect(url_for('calendar'))
    tracks = conn.execute('SELECT id, track FROM tracks ORDER BY track').fetchall()
    conn.close()
    return render_template('form_calendar.html', action='Add', data=None, tracks=tracks)


@app.route('/calendar/edit/<int:id>', methods=['GET', 'POST'])
def calendar_edit(id):
    conn = get_db()
    if request.method == 'POST':
        conn.execute(
            'UPDATE calendar SET date=?,track_id=?,ticket=?,rider=? WHERE id=?',
            (request.form['date'], request.form['track_id'], request.form['ticket'], request.form['rider'], id)
        )
        conn.commit(); conn.close()
        return redirect(url_for('calendar'))
    data   = conn.execute('SELECT * FROM calendar WHERE id=?', (id,)).fetchone()
    tracks = conn.execute('SELECT id, track FROM tracks ORDER BY track').fetchall()
    conn.close()
    return render_template('form_calendar.html', action='Edit', data=data, tracks=tracks)


@app.route('/calendar/delete/<int:id>')
def calendar_delete(id):
    conn = get_db()
    conn.execute('DELETE FROM calendar WHERE id=?', (id,))
    conn.commit(); conn.close()
    return redirect(url_for('calendar'))


# ─── RESULTS ────────────────────────────────────────────────────────────────
@app.route('/results')
def results():
    conn = get_db()
    # JOIN results → calendar → tracks
    data = conn.execute('''
        SELECT r.id, r.result, r.standing, r.records, c.date, t.track, r.calendar_id
        FROM results r
        JOIN calendar c ON r.calendar_id = c.id
        JOIN tracks t ON c.track_id = t.id
        ORDER BY r.id DESC
    ''').fetchall()
    conn.close()
    return render_template('results.html', results=data)


@app.route('/results/add', methods=['GET', 'POST'])
def results_add():
    conn = get_db()
    if request.method == 'POST':
        conn.execute(
            'INSERT INTO results (calendar_id,result,standing,records) VALUES (?,?,?,?)',
            (request.form['calendar_id'], request.form['result'],
             request.form['standing'], request.form['records'])
        )
        conn.commit(); conn.close()
        return redirect(url_for('results'))
    calendars = conn.execute('''
        SELECT c.id, c.date, t.track FROM calendar c
        JOIN tracks t ON c.track_id = t.id ORDER BY c.date
    ''').fetchall()
    conn.close()
    return render_template('form_results.html', action='Add', data=None, calendars=calendars)


@app.route('/results/edit/<int:id>', methods=['GET', 'POST'])
def results_edit(id):
    conn = get_db()
    if request.method == 'POST':
        conn.execute(
            'UPDATE results SET calendar_id=?,result=?,standing=?,records=? WHERE id=?',
            (request.form['calendar_id'], request.form['result'],
             request.form['standing'], request.form['records'], id)
        )
        conn.commit(); conn.close()
        return redirect(url_for('results'))
    data      = conn.execute('SELECT * FROM results WHERE id=?', (id,)).fetchone()
    calendars = conn.execute('''
        SELECT c.id, c.date, t.track FROM calendar c
        JOIN tracks t ON c.track_id = t.id ORDER BY c.date
    ''').fetchall()
    conn.close()
    return render_template('form_results.html', action='Edit', data=data, calendars=calendars)


@app.route('/results/delete/<int:id>')
def results_delete(id):
    conn = get_db()
    conn.execute('DELETE FROM results WHERE id=?', (id,))
    conn.commit(); conn.close()
    return redirect(url_for('results'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
