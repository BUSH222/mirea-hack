from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, login_required
from dbloader import connect_to_db
from logger import log_event
from secrets import token_urlsafe
from login import check_isAdmin
from collections import deque
import time
import requests
import requests.exceptions
import psutil
import random
import string


app = Flask(__name__)
app.config['SECRET_KEY'] = token_urlsafe(16)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

conn, cur = connect_to_db()

request_timestamps = deque()


@app.before_request
def track_requests():
    """Track the timestamp of each request. Update"""
    global request_timestamps
    current_time = time.time()
    request_timestamps.append(current_time)
    while request_timestamps and request_timestamps[0] < current_time - 60:
        request_timestamps.popleft()


def generate_random_string():
    """Generates a random filler string when deleting accounts"""
    length = 32
    characters = string.ascii_letters + string.digits + '_' + ',' + '.'
    return ''.join(random.choices(characters, k=length))


@app.route('/admin_panel')
@login_required
@check_isAdmin
def admin_panel():
    """Render the admin panel template."""
    return render_template('admin_panel.html')


@app.route('/admin_panel/logs')
@login_required
@check_isAdmin
def admin_panel_logs():
    """Render the admin panel server logs page."""
    return render_template('admin_panel_logs.html')


@app.route('/admin_panel/logs/get_logs')
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


@app.route('/admin_panel/community')
@login_required
@check_isAdmin
def admin_panel_community():
    """
    Render the community management page within the admin panel."""
    return render_template('admin_panel_community.html')


@app.route('/admin_panel/community/delete_account')
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


@app.route('/admin_panel/community/view_account_info')
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


@app.route('/admin_panel/community/set_account_info')
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


@app.route('/admin_panel/full_server_status', methods=['GET'])
@login_required
@check_isAdmin
def full_server_status():  # TODO
    """Returns the server statuses for all microservices running except postgres database.

    Returns:
        json: status of every server in the format {"server_status": {"ram": number, "cpu": number, "rpm": number}}
    """
    try:
        main_status_response = requests.get('https://127.0.0.1:5000/main_server_status', verify=False, timeout=1)
        main_status = main_status_response.json()
    except (requests.exceptions.Timeout, requests.exceptions.JSONDecodeError, requests.exceptions.ConnectionError):
        main_status = {'ram': 0, 'cpu': 0, "rpm": 0}

    try:
        asset_delivery_status_response = requests.get('http://127.0.0.1:5001/asset_delivery_server_status', timeout=1)
        asset_delivery_status = asset_delivery_status_response.json()
    except (requests.exceptions.Timeout, requests.exceptions.JSONDecodeError, requests.exceptions.ConnectionError):
        asset_delivery_status = {'ram': 0, 'cpu': 0, "rpm": 0}
    admin_panel_status = {'ram': psutil.virtual_memory().percent,
                          'cpu': psutil.cpu_percent(),
                          'rpm': len(request_timestamps)}

    return jsonify({"Main server": main_status,
                    "Asset delivery": asset_delivery_status,
                    "Admin panel": admin_panel_status})


@app.route('/admin_panel/help')
@login_required
@check_isAdmin
def admin_help():
    """Render the template for the admin help page."""
    return render_template("admin_help.html")


if __name__ == "__main__":
    app.run(port=5002, debug=True)
    cur.close()
    conn.close()
