import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from .db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        db = get_db()
        err = None

        if not username:
            err = 'Username is required'
        elif not password:
            err = 'Password is required'
        elif password != password2:
            err = 'Passwords does not match'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?',
            (username,)
        ).fetchone() is not None:
            err = f'Username {username} already registered'

        if err is None:
            db.execute(
                'INSERT INTO user (username, password) \
                VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(err)

    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        err = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?',
            (username,)
        ).fetchone()

        if not username:
            err = 'Username is required'
        elif not password:
            err = 'Password is required'
        elif user is None:
            err = f'No such user: {username}'
        elif not check_password_hash(user['password'], password):
            err = 'Incorrect password'

        if err is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(err)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        ).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapper_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)
    return wrapper_view

