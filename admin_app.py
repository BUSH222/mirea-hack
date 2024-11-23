from flask import Blueprint, render_template, request, jsonify
from flask_login import LoginManager, login_required
from dbloader import connect_to_db
from logger import log_event
from login import check_isAdmin
import psutil
import random
import string

admin_app = Blueprint('admin_app', __name__)
conn, cur = connect_to_db()

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
        cur.execute("UPDATE users SET name = %s, password = %s, email = %s, role = '' WHERE id = %s",
                    (f'deleted_user_{user_id}', generate_random_string(), generate_random_string(), user_id))
        conn.commit()
        if cur.rowcount == 0:
            return 'Something went wrong.'
        log_event("Deleted user account, id:", log_level=20, kwargs=user_id)
        return 'Success!'
    except Exception as e:
        conn.rollback()
        log_event("Error deleting account:", log_level=30, kwargs=e)
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
            email (str): User's email.
            password (str): User's password
            points (int): User's activity points.
            role (str): User's roles.
                Organised as a sorted string of values 0-5, each of them being a unique role identifier.

        str: 'No results' if the search for the user returned nothing
             'Error: {error desciption}' if something went wrong.
    """
    user = request.args.get('user')
    try:
        cur.execute('SELECT id, name, email, password, points, role FROM users WHERE name = %s', (user, ))
        roles_raw = cur.fetchone()
        if not roles_raw:
            return jsonify('No results')
        log_event("User account info viewed, name:", log_level=10, kwargs=user)
        return jsonify(roles_raw)
    except Exception as e:
        conn.rollback()
        log_event("Error viewing account info:", log_level=30, kwargs=e)
        return f'Error: {e}'


@admin_app.route('/admin_panel/community/create_profile')
@login_required
@check_isAdmin
def admin_panel_community_create_profile():
    name = request.args.get('name')
    password = request.args.get('password')
    isAdmin = request.args.get('isAdmin')
    try:
        cur.execute('INSERT INTO users  (name, password, isAdmin) VALUES(%s, %s, %s)',
                    (name, password, isAdmin))
        conn.commit()
        log_event("Create account:", log_level=20)
    except Exception as e:
        conn.rollback()
        log_event("Error create account:", log_level=30, kwargs=e)
        return f'Error: {e}'


@admin_app.route('/admin_panel/community/set_account_info')
@login_required
@check_isAdmin
def admin_panel_community_set_account_info():
    """
    Set account info for a user based on the user id.

    Args:
        id (int): User's id.
        name (str): User's name.
        email (str): User's email.
        password (str): User's password
        points (int): User's activity points.
        role (str): User's roles.
            Organised as a sorted string of values 0-5, each of them being a unique role identifier.

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


@admin_app.route('/admin_panel/full_server_status', methods=['GET'])
@login_required
@check_isAdmin
def full_server_status():  # TODO
    """Returns the server statuses for all microservices running except postgres database.

    Returns:
        json: status of every server in the format {"server_status": {"ram": number, "cpu": number, "rpm": number}}
    """
    master_server_status = {'ram': psutil.virtual_memory().percent,
                            'cpu': psutil.cpu_percent()}

    return jsonify(master_server_status)
