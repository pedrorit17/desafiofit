from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'desafiofit2024'
app.jinja_env.globals['enumerate'] = enumerate

DB_PATH = os.path.join(os.path.dirname(__file__), 'desafiofit.db')


def calcular_pontos_cardio(minutos, categoria):
    if not minutos:
        return 0
    if categoria == 'emagrecimento':
        if minutos >= 50:
            return 5
        elif minutos >= 40:
            return 4
        elif minutos >= 30:
            return 3
        elif minutos >= 20:
            return 2
        return 0
    else:  # hipertrofia
        if minutos >= 25:
            return 5
        elif minutos >= 20:
            return 4
        elif minutos >= 15:
            return 3
        elif minutos >= 10:
            return 2
        return 0


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.create_function('calcular_pontos_cardio', 2, calcular_pontos_cardio)
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS competidores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                categoria TEXT NOT NULL CHECK(categoria IN ('emagrecimento', 'hipertrofia')),
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS registros_diarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competidor_id INTEGER NOT NULL REFERENCES competidores(id),
                dia INTEGER NOT NULL CHECK(dia BETWEEN 1 AND 30),
                musculacao INTEGER NOT NULL DEFAULT 0,
                post_insta INTEGER NOT NULL DEFAULT 0,
                cardio_minutos INTEGER NOT NULL DEFAULT 0,
                atividade_coletiva INTEGER NOT NULL DEFAULT 0,
                pontos INTEGER NOT NULL DEFAULT 0,
                registrado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(competidor_id, dia)
            );
        ''')


def calcular_pontos_total(musculacao, post_insta, cardio_minutos, atividade_coletiva, categoria):
    pontos = 0
    if musculacao:
        pontos += 20
    if post_insta:
        pontos += 2
    pontos += calcular_pontos_cardio(cardio_minutos, categoria)
    if atividade_coletiva:
        pontos += 5
    return pontos


@app.route('/')
def index():
    with get_db() as conn:
        ranking = conn.execute('''
            SELECT
                c.id,
                c.nome,
                c.categoria,
                COALESCE(SUM(r.pontos), 0)                              AS total_pontos,
                COUNT(r.id)                                              AS dias_registrados,
                COALESCE(SUM(r.cardio_minutos), 0)                      AS total_cardio,
                COALESCE(SUM(calcular_pontos_cardio(r.cardio_minutos, c.categoria)), 0) AS pts_cardio,
                COALESCE(SUM(r.atividade_coletiva), 0)                  AS total_coletivas,
                COALESCE(SUM(r.post_insta), 0)                          AS total_posts
            FROM competidores c
            LEFT JOIN registros_diarios r ON c.id = r.competidor_id
            GROUP BY c.id
            ORDER BY
                total_pontos      DESC,
                dias_registrados  DESC,
                pts_cardio        DESC,
                total_coletivas   DESC,
                total_posts       DESC,
                c.nome
        ''').fetchall()

        total_cardio_geral = conn.execute(
            'SELECT COALESCE(SUM(cardio_minutos), 0) AS total FROM registros_diarios'
        ).fetchone()['total']

    return render_template('index.html', ranking=ranking, total_cardio_geral=total_cardio_geral)


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    with get_db() as conn:
        competidores = conn.execute(
            'SELECT id, nome, categoria FROM competidores ORDER BY nome'
        ).fetchall()

    if request.method == 'POST':
        competidor_id = request.form.get('competidor_id')
        dia = request.form.get('dia', type=int)
        musculacao = 1 if request.form.get('musculacao') else 0
        post_insta = 1 if request.form.get('post_insta') else 0
        cardio_minutos = request.form.get('cardio_minutos', 0, type=int)
        atividade_coletiva = 1 if request.form.get('atividade_coletiva') else 0

        if not competidor_id or not dia:
            flash('Competidor e dia são obrigatórios.', 'erro')
            return render_template('registrar.html', competidores=competidores)

        with get_db() as conn:
            comp = conn.execute(
                'SELECT categoria FROM competidores WHERE id = ?', (competidor_id,)
            ).fetchone()

            if not comp:
                flash('Competidor não encontrado.', 'erro')
                return render_template('registrar.html', competidores=competidores)

            pontos = calcular_pontos_total(
                musculacao, post_insta, cardio_minutos, atividade_coletiva, comp['categoria']
            )

            try:
                conn.execute('''
                    INSERT INTO registros_diarios
                        (competidor_id, dia, musculacao, post_insta, cardio_minutos, atividade_coletiva, pontos)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (competidor_id, dia, musculacao, post_insta, cardio_minutos, atividade_coletiva, pontos))
                flash(f'Dia {dia} registrado com sucesso! +{pontos} pontos.', 'sucesso')
                return redirect(url_for('index'))
            except sqlite3.IntegrityError:
                flash(f'Este competidor já tem registro para o dia {dia}.', 'erro')

    return render_template('registrar.html', competidores=competidores)


@app.route('/competidor/novo', methods=['GET', 'POST'])
def novo_competidor():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        categoria = request.form.get('categoria')

        if not nome or categoria not in ('emagrecimento', 'hipertrofia'):
            flash('Nome e categoria são obrigatórios.', 'erro')
            return render_template('novo_competidor.html')

        with get_db() as conn:
            try:
                conn.execute(
                    'INSERT INTO competidores (nome, categoria) VALUES (?, ?)',
                    (nome, categoria)
                )
                flash(f'{nome} cadastrado com sucesso!', 'sucesso')
                return redirect(url_for('index'))
            except sqlite3.IntegrityError:
                flash('Já existe um competidor com esse nome.', 'erro')

    return render_template('novo_competidor.html')


@app.route('/competidor/<int:competidor_id>')
def detalhe_competidor(competidor_id):
    with get_db() as conn:
        comp = conn.execute(
            'SELECT * FROM competidores WHERE id = ?', (competidor_id,)
        ).fetchone()

        if not comp:
            flash('Competidor não encontrado.', 'erro')
            return redirect(url_for('index'))

        registros = conn.execute('''
            SELECT dia, musculacao, post_insta, cardio_minutos, atividade_coletiva, pontos
            FROM registros_diarios
            WHERE competidor_id = ?
            ORDER BY dia
        ''', (competidor_id,)).fetchall()

        total = conn.execute('''
            SELECT
                COALESCE(SUM(pontos), 0) AS total_pontos,
                COALESCE(SUM(cardio_minutos), 0) AS total_cardio,
                COUNT(*) AS dias_registrados
            FROM registros_diarios WHERE competidor_id = ?
        ''', (competidor_id,)).fetchone()

    return render_template('detalhe.html', comp=comp, registros=registros, total=total)


@app.route('/api/pontos_cardio')
def api_pontos_cardio():
    minutos = request.args.get('minutos', 0, type=int)
    categoria = request.args.get('categoria', 'emagrecimento')
    pts = calcular_pontos_cardio(minutos, categoria)
    return jsonify({'pontos': pts})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
