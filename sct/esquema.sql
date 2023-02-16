import sqlite3
import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

        return g.db


def close_db():
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    # Inicia la base en blanco y agrega la clave "admin", 
    # para registrar primer usuario
    db = get_db()

    with current_app.open_resource('esquema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        db.execute('INSERT INTO invitacion VALUES ("admin")')


def add_clave(clave):
    # Aqui de sergregaran las claves que mas tarde se usaran para registrarse
    db = get_db()
    db.execute('INSERT INTO invitacion VALUES (?)', clave)


@click.command('init-db')
def init_db_command():
    """Limpiar base de datos y crear nuevas tablas."""
    init_db()
    click.echo('Initialized the database.')


@click.command('agregar-invitacion')
@click.option(
    '--clave', help='Agrega una clave a las invitaciones', prompt='clave: '
)
def add_invitacion_command(clave):
    add_clave(clave)
    click.echo(f'Se a agregado la clave {clave}')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
