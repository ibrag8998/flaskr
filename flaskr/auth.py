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
        password = request.form.get('password1')
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
            return refirect(url_for('auth.login'))

        flash(err)

    return render_template('auth/register.html')

