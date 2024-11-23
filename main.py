from flask import Flask, render_template, request, redirect, url_for, abort
from login import app_login, load_user
from admin_app import admin_app
from flask_login import LoginManager, login_required, current_user
from dbloader import connect_to_db
from flask_apscheduler import APScheduler
from tcp_actions.reverse_shell_sender import send_command
from keygen import generate_secure_key
import random


app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True  # Remove in final version
app.config['SECRET_KEY'] = 'bruh'
app.jinja_env.auto_reload = True  # Remove in final version
app.config['SCHEDULER_API_ENABLED'] = True

scheduler = APScheduler()

conn, cur = connect_to_db()

app.register_blueprint(app_login)
app.register_blueprint(admin_app)


login_manager = LoginManager(app)
login_manager.login_view = 'app_login.login'

def fetch_data_from_database():
    pass_gen = generate_secure_key()
    cur.execute("SELECT * FROM requests WHERE accepted = true and start_time={}")
    requests_accepted = list(cur.fetchall())
    for ticket in requests_accepted:
        cur.execute("SELECT id FROM servers WHERE os = %s",(ticket[3]))
        all_servers = cur.fetchall()
        cur.execute("SELECT id FROM request_servers")
        requests_accepted = cur.fetchall()
        for serv in all_servers:
            for i in range(len(requests_accepted)):
                pass

    if requests_accepted != []:
        choosen_server = random.choice(requests_accepted)[0]
        send_command(f'sudo useradd -m "{username}" && echo "{username}:{pass_gen}" | sudo chpasswd', settings[choosen_server], settings["port"])
    else:
        choosen_server = random.choice(all_servers)
        cur.execute("SELECT os from ser")
        change_os_on_pxe_server(choosen_server, os)
        send_command('sudo reboot')

@scheduler.task('interval', hours=1)
def scheduled_task():
    fetch_data_from_database()

@login_manager.user_loader
def _load_user(uid):
    return load_user(uid)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/book_server', methods=['GET', 'POST'])
@login_required
def book_server():
    if request.method == 'POST':
        email = request.args.get('email')
        os = request.args.get('operating_system')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        comment = request.args.get('comment')
        try:
            cur.execute("INSERT INTO requests (user_id, email, os, start_time, end_time, user_comment)\
                        VALUES(%s, %s, %s, %s, %s, %s)", (current_user.id, email, os, start_date, end_date, comment))
            conn.commit()
            return 'Success'
        except Exception as e:
            conn.rollback()
            return f'Error, {e}'
    return render_template('book_server.html')


@app.route('/booking_list', methods=['GET'])
@login_required
def booking_list():
    if current_user.isAdmin:
        return redirect(url_for('admin_app.admin_panel'))
    cur.execute(
        "SELECT id, os, start_time - CURRENT_TIMESTAMP AS start_time, accepted \
        FROM requests WHERE user_id = %s",
        (current_user.id,)
    )
    data = cur.fetchall() or []
    processed_data = [
        {
            "id": row[0],
            "os": row[1],
            "start_time": row[2],
            "accepted": row[3],
        }
        for row in data
    ]
    return render_template('booking_list.html', data=processed_data)


@app.route('/view_booking')
@login_required
def view_booking():
    booking_id = request.args.get('id')
    cur.execute("SELECT id, email, os, user_comment, start_time, end_time, accepted\
                FROM requests WHERE id = %s AND user_id = %s", (booking_id, current_user.id))
    data = cur.fetchone()

    if data is None:
        return redirect(url_for('book_server'))
    return render_template('view_booking.html', data=data)


if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='localhost', port=5000)
