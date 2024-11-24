from flask import Flask, render_template, request, redirect, url_for
from login import app_login, load_user
from admin_app import admin_app
from flask_login import LoginManager, login_required, current_user
from dbloader import connect_to_db
from flask_apscheduler import APScheduler
from datetime import datetime
import random
import os
from settings_loader import get_processor_settings
from os_alloc_changer import change_os_on_pxe_server
from mail_sender import send_mail
from tcp_actions.reverse_shell_sender import send_command
from tcp_actions.reverse_shell_sender_tls import send_command_tls
settings = get_processor_settings()
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
    current_date = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT * FROM requests\
    WHERE accepted = true and start_time=%s and requires_manual_approval=false", (current_date, ))
    requests_accepted = list(cur.fetchall())
    for ticket in requests_accepted:
        cur.execute("SELECT id FROM servers WHERE os = %s", (ticket[3]))
        all_servers = list(cur.fetchall())
        cur.execute("SELECT id FROM request_servers")
        busy_servers = cur.fetchall()
        for serv in busy_servers:
            for i in range(len(all_servers), -1):
                if serv == all_servers[i]:
                    all_servers.pop(i)
        if all_servers != []:
            try:
                choosen_server = str(random.choice(requests_accepted)[0])
                username = cur.execute('SELECT name FROM users WHERE user_id = %s', (ticket[1]))
                password = cur.execute('SELECT password FROM users WHERE id = %s', (ticket[1]))
                if os.path.exists(os.path.join('certificates', settings["certificate_name"])):
                    keyfile = None
                    certificate = None
                    send_command_tls(f'sudo useradd -m "{username}" && echo "{username}:{password}" | sudo chpasswd',
                                     settings[choosen_server], settings["port"], keyfile, certificate)
                else:
                    send_command(f'sudo useradd -m "{username}" && echo "{username}:{password}" | sudo chpasswd',
                                 settings[choosen_server], settings["port"])
                cur.execute("INSERT INTO request_servers (request_id,server_id) VALUES (%s,%s)",
                            (ticket[0], choosen_server))
                conn.commit()
                send_mail(ticket[2], 'Доступ к машине предоставлен '+username+' '+password)
            except Exception:
                conn.rollback()
                raise Exception
        else:
            try:
                choosen_server = str(random.choice(requests_accepted)[0])
                change_os_on_pxe_server(choosen_server, ticket[3])
                send_command('sudo reboot')
                username = cur.execute('SELECT name FROM users WHERE id = %s', (ticket[1]))
                password = cur.execute('SELECT password FROM users WHERE id = %s', (ticket[1]))
                send_command(f'sudo useradd -m "{username}" && echo "{username}:{password}" | sudo chpasswd',
                             settings[choosen_server], settings["port"])
                cur.execute("INSERT INTO request_servers (request_id,server_id) VALUES (%s,%s)",
                            (ticket[0], choosen_server))
                conn.commit()
                send_mail(ticket[2], username+' '+password)
            except Exception:
                conn.rollback()
                raise Exception
    cur.execute("SELECT * FROM requests WHERE accepted = true and end_time < CAST(%s AS TIMESTAMP)", (current_date, ))
    tickets_overdue = list(cur.fetchall())
    for ticket in tickets_overdue:
        try:
            cur.execute('SELECT name FROM users WHERE id = %s', (ticket[1], ))
            username = cur.fetchone()
            cur.execute('SELECT server_id FROM request_servers WHERE request_id = %s', (ticket[0], ))
            serverid = str(cur.fetchone()[0])
            print(serverid)
            send_command(f'sudo userdel -r {username}', settings[serverid], settings["port"])
            cur.execute("DELETE FROM request_servers WHERE request_id = %s", (ticket[0], ))
            conn.commit()
            send_mail(ticket[2], "Доступ к машине завершен")
        except Exception:
            conn.rollback()
            raise Exception
    cur.execute(f"SELECT * FROM requests WHERE accepted = true and start_date - {current_date}<865")
    admin_alert_tickets = list(cur.fetchone)
    cur.execute("SELECT users.email, requests.user_id ")  # TODO
    for ticket in admin_alert_tickets:
        send_mail()


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
        # Check if servers reserved for this time slot
        cur.execute("""
SELECT COUNT(*) FROM public.requests
WHERE start_time < CAST(%s AS TIMESTAMP) AND end_time > CAST(%s AS TIMESTAMP);
""", (end_date, start_date))
        occupied = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM public.servers")
        total = cur.fetchone()[0]
        if total-occupied <= 0:
            return 'All servers reserved for this time slot.'

        # Check if start date is less than the end date
        if start_date >= end_date:
            return 'Start date is bigger than end date'

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
    fetch_data_from_database()
    # scheduler.init_app(app)
    # scheduler.start()
    # app.run(host='localhost', port=5000)
