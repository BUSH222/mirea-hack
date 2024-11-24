from flask import Blueprint, render_template, request, jsonify
from flask_login import LoginManager, login_required
from dbloader import connect_to_db
from logger import log_event
from login import check_isAdmin
import psutil
import random
import string
from settings_loader import get_processor_settings
admin_app = Blueprint('admin_app', __name__)
conn, cur = connect_to_db()

settings = get_processor_settings

login_manager = LoginManager(admin_app)
login_manager.login_view = 'app_login.login'


def generate_random_string():
    """Generates a random filler string when deleting accounts"""
    length = 32
    characters = string.ascii_letters + string.digits + '_' + ',' + '.'
    return ''.join(random.choices(characters, k=length))


@admin_app.route('/admin_panel')
@login_required
@check_isAdmin
def admin_panel():
    """Render the admin panel template."""
    return render_template('admin_panel.html')


@admin_app.route('/admin_panel/logs')
@login_required
@check_isAdmin
def admin_panel_logs():
    """Render the admin panel server logs page."""
    return render_template('admin_panel_logs.html')


@admin_app.route('/admin_panel/logs/get_logs')
@login_required
@check_isAdmin
def admin_panel_get_top100_logs():
    """
    Return top 100 latest server logs

    Returns:
        str: organised list of logs.
    """
    cur.execute("""SELECT CONCAT(id, '. [', TO_CHAR(log_time, 'YYYY-MM-DD HH24:MI:SS'), ']:  ', log_text)
                FROM logs
                ORDER BY id DESC
                LIMIT 100""")
    return jsonify(cur.fetchall())


@admin_app.route('/admin_panel/community')
@login_required
@check_isAdmin
def admin_panel_community():
    """
    Render the community management page within the admin panel."""
    return render_template('admin_panel_community.html')


@admin_app.route('/admin_panel/community/delete_account')
@login_required
@check_isAdmin
def admin_panel_community_delete_account():
    """
    Delete a user account based on the user id.
    Deleting the account changes its username to deleted_account[id], makes its password and email random

    Args:
        id (int): The id of the account to delete.

    Returns:
        bool: True if the account was successfully deleted, False otherwise.
    """
    user_id = request.args.get('id')
    try:
        cur.execute("UPDATE users SET name = %s, password = %s, isAdmin = False WHERE id = %s",
                    (f'deleted_user_{user_id}', generate_random_string(), user_id))
        conn.commit()
        if cur.rowcount == 0:
            return 'Something went wrong.'
        log_event("Deleted user account, id:", log_level=20, kwargs=user_id)
        return 'Success!'
    except Exception as e:
        conn.rollback()
        log_event("Error deleting account:", log_level=30, kwargs=e)
        return f'Error: {e}'


@admin_app.route('/admin_panel/requests')
@login_required
@check_isAdmin
def admin_panel_requests():
    cur.execute("SELECT r.id, u.name, r.email, r.user_comment,\
                r.start_time, r.end_time, r.accepted, r.requires_manual_approval\
                FROM requests r JOIN users u ON r.user_id = u.id")
    data = cur.fetchall()
    return render_template('requests.html', data=data)


@admin_app.route('/admin_panel/view_request', methods=['GET', 'POST'])
@login_required
@check_isAdmin
def admin_panel_view_request():
    id = request.args.get('id')
    if request.method == 'GET':
        cur.execute("SELECT r.id, u.name, r.email, r.os, r.user_comment, r.start_time, r.end_time, \
                    r.accepted, r.requires_manual_approval\
                    FROM requests r JOIN users u ON r.user_id = u.id WHERE r.id = %s", (id,))
        data = cur.fetchall()[0]
        return render_template("view_request.html", data=data)
    if request.method == 'POST':
        data = request.args
        action = data.get('action')
        _id = data.get('id')
        try:
            if action == 'accept':
                cur.execute('UPDATE requests SET accepted = true WHERE id = %s', (_id,))
                conn.commit()
                log_event("request approved:", log_level=20)

            elif action == 'decline':
                cur.execute('UPDATE requests SET accepted = false WHERE id = %s', (_id,))
                conn.commit()
                log_event("Request denied:", log_level=20)
            return 'Success'
        except Exception as e:
            print(e)
            conn.rollback()
            log_event("Error create account:", log_level=30, kwargs=e)
            return f'Error: {e}'


@admin_app.route('/admin_panel/community/view_account_info')
@login_required
@check_isAdmin
def admin_panel_community_view_account_info():
    """
    View the account info based on the user name.

    Args:
        user (str): The username of the account to view roles for.

    Returns:
        json array:
            id (int): User's id.
            name (str): User's name.
            password (str): User's password

        str: 'No results' if the search for the user returned nothing
             'Error: {error desciption}' if something went wrong.
    """
    user = request.args.get('user')
    try:
        cur.execute('SELECT id, name, password, isAdmin FROM users WHERE name = %s', (user, ))
        roles_raw = cur.fetchone()
        if not roles_raw:
            return jsonify('No results')
        log_event("User account info viewed, name:", log_level=10, kwargs=user)
        return jsonify(roles_raw)
    except Exception as e:
        conn.rollback()
        log_event("Error viewing account info:", log_level=30, kwargs=e)
        return f'Error: {e}'


@admin_app.route('/admin_panel/community/create_profile', methods=['GET', 'POST'])
@login_required
@check_isAdmin
def admin_panel_community_create_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        isAdmin = request.form.get('isAdmin')
        try:
            cur.execute("SELECT 1 FROM users WHERE name = %s", (name,))
            if cur.fetchone() is not None:
                return 'Логин занят'
            cur.execute('INSERT INTO users (name, password, isAdmin) VALUES(%s, %s, %s)',
                        (name, password, isAdmin))
            conn.commit()
            log_event("Create account:", log_level=20)
            return 'Success'
        except Exception as e:
            print(e)
            conn.rollback()
            log_event("Error create account:", log_level=30, kwargs=e)
            return f'Error: {e}'
    else:
        return render_template('create_profile.html')


@admin_app.route('/admin_panel/community/set_account_info')
@login_required
@check_isAdmin
def admin_panel_community_set_account_info():
    """
    Set account info for a user based on the user id.

    Args:
        id (int): User's id.
        name (str): User's name.
        password (str): User's password
    Returns:
        str: 'Success!' if everything went ok.
             'Error: {error desciption}' if something went wrong.
    """
    uid = request.args.get('user')
    name = request.args.get('name')
    password = request.args.get('password')
    isAdmin = request.args.get('isAdmin')
    try:
        cur.execute('UPDATE users SET name = %s, password = %s, isAdmin = %s WHERE id = %s',
                    (name, password, isAdmin, uid))
        conn.commit()
        log_event("Updated user account, id:", log_level=20, kwargs=uid)
    except Exception as e:
        conn.rollback()
        log_event("Error setting account info:", log_level=30, kwargs=e)
        return f'Error: {e}'
    return 'Success'


@admin_app.route('/admin_panel/community/prune_account')
@login_required
@check_isAdmin
def prune_account():
    uid = request.args.get('user')
    try:
        cur.execute("""DELETE FROM request_servers
WHERE request_id IN (
    SELECT id
    FROM requests
    WHERE user_id = %s
);
DELETE FROM requests
WHERE user_id = %s;""", (uid, uid))
        conn.commit()
        log_event(f"Pruned user account, id: {uid}", log_level=20)
        return 'Success!'
    except Exception as e:
        conn.rollback()
        log_event(f"Error pruning user account, id: {uid}", log_level=30)
        return f'Error: {e}'


@admin_app.route('/admin_panel/full_server_status', methods=['GET'])
@login_required
@check_isAdmin
def full_server_status():
    """Returns the server statuses for all microservices running except postgres database.

    Returns:
        json: status of every server in the format {"server_status": {"ram": number, "cpu": number, "rpm": number}}
    """
    master_server_status = {'ram': psutil.virtual_memory().percent,
                            'cpu': psutil.cpu_percent()}

    return jsonify(master_server_status)
