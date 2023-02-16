import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.gestor_db import get_db, close_db

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/registrar', method=('GET', 'POST'))
def registrar():
    if request.method == 'post':
        clave = request.form['clave']
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        ver_clave = db.execute(
            'SELECT * INTO invitacion WHERE clave = ? ', clave
        ).fetchone()
        error = None

        if not clave:
            error = 'Se requiere clave de registro.'
        elif not username:
            error = 'Se requiere nombre de usuario.'
        elif not password:
            error = 'Se requiere contraseña.'
        elif ver_clave is None:
            error = 'Clave no valida'
        else:
            try:
                db.execute(
                    'INSERT INTO user (username, password) VALUES (?, ?)',
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f'Usuario {username} ya esta registrado.'
            else:
                db.execute(
                    'DELETE FROM invitacion WHERE clave = ?', calve
                )
                db.commit()
                return redirect(url_for('user.login'))
        
        flash(error)
    
    return render_template('user/registrar.html')


@bp.route('/login', method=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username)
        ).fetchone()

        if user is None:
            error = 'Nombre de usario incorrecto'
        elif not check_password_hash(user['password'], password):
            error = 'Contraseña incorrecta'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('user/login.html')


@bp.route('/change_password', method=('GET', 'POST'))
def change_password():
    if request.method =='POST':
        pass


@bp.before_app_request
def cargar_logged_in_usuario():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id)
        ).fetchone()


@bp.route('user/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))


def login_requerido(vista):
    @functools.wraps(vista)
    def vista_envuelta(**kwargs):
        if g.user is None:
            return redirect(url_for('user.login'))
        
        return vista(**kwargs)
    
    return vista_envuelta