from flask import (
    Blueprint,
    render_template,
    request,
    g,
    redirect,
    url_for,
    flash,
    abort
)

from .db import get_db
from .auth import login_required


bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        err = None

        if not title:
            err = 'Title is required'

        if err is None:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

        flash(err)

    return render_template('blog/create.html')


def get_post(id_, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id_,)
    ).fetchone()

    if post is None:
        abort(404, f'Post #{id_} does not exist')

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id_>/update', methods=['GET', 'POST'])
@login_required
def update(id_):
    post = get_post(id_)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        err = None

        if not title:
            err = 'Title is required'

        if err is None:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id_)
            )
            db.commit()
            return redirect(url_for('blog.index'))

        flash(err)

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id_>/delete', methods=['POST'])
@login_required
def delete(id_):
    get_post(id_)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id_,))
    db.commit()
    return redirect(url_for('blog.index'))

