from flask import Flask, render_template, request, redirect, url_for, abort
from login import app_login, load_user
from admin_app import admin_app
from flask_login import LoginManager, login_required, current_user
from dbloader import connect_to_db

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True  # Remove in final version
app.config['SECRET_KEY'] = 'bruh'
app.jinja_env.auto_reload = True  # Remove in final version

conn, cur = connect_to_db()

app.register_blueprint(app_login)
app.register_blueprint(admin_app)


login_manager = LoginManager(app)
login_manager.login_view = 'app_login.login'


@login_manager.user_loader
def _load_user(uid):
    return load_user(uid)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/book_server', methods=['GET', 'POST'])
@login_required
def book_server():
    os = request.args.get('os')
    comment = request.args.get('comment')
    end_time = request.args.get('end_time')
    if request.method == 'POST':
        try:
            cur.execute("INSERT INTO requests (user_id, os, user_comment, start_time, end_time)\
                        VALUES(%s, %s, CURRENT_TIMESTAMP, %s, %s)", (current_user.id, os, comment, end_time))
        except Exception as e:
            print(e)
            abort(500)
    return render_template('book_server.html')


@app.route('/booking_list', methods=['GET'])
@login_required
def booking_list():
    cur.execute("SELECT id, os, start_time - CURRENT_TIMESTAMP AS start_time, accepted\
                FROM requests WHERE id = %s", (current_user.id, ))
    data = cur.fetchall() or []
    return render_template('booking_list.html', data=data)


@app.route('/view_booking')
@login_required
def view_booking():
    booking_id = request.args.get('id')
    cur.execute("SELECT id, os, user_comment, start_time, end_time, accepted\
                FROM users WHERE id = %s AND user = %s", (booking_id, current_user.id))
    data = cur.fetchone()
    if data is None:
        return redirect(url_for('book_server'))
    return render_template('view_booking.html', data=data)


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
