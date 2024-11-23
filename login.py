from flask import redirect, render_template, request, url_for, Blueprint, jsonify
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user
from dbloader import connect_to_db


app_login = Blueprint('app_login', __name__)
conn, cur = connect_to_db()

login_manager = LoginManager(app_login)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, password, isAdmin):
        self.id = id
        self.username = username
        self.password = password
        self.isAdmin = isAdmin


@login_manager.user_loader
def load_user(user_id):
    cur.execute("SELECT id, name, password, isAdmin FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    if user_data:
        return User(*user_data)
    return None


def check_isAdmin(f):
    """Decorator which lets the function run only if the user is an admin."""
    def wrapper(*args, **kwargs):
        cur.execute("SELECT id, name, password, isAdmin FROM users WHERE id = %s", (current_user.id, ))
        user_data = cur.fetchone()
        if user_data[3]:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Access denied. a is not True"}), 403
    wrapper.__name__ = f.__name__
    return wrapper


@app_login.route('/login', methods=['GET', 'POST'])
def login():
    """Choosing an entry method and logging in
        Redirects to account or google sign in"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur.execute("SELECT id, name, password, isAdmin FROM users WHERE name = %s", (username, ))
        user_data = cur.fetchone()

        if user_data:
            if user_data[2] == password and len(password) < 32:
                user = User(*user_data)
                login_user(user)
                return 'OK'
            else:
                return "Invalid username or password"
        else:
            return 'User does not exist '
    return render_template('login.html')


@app_login.route('/logout')
@login_required
def logout():
    """Logs the user out and redirects them to the login page."""
    logout_user()
    return redirect(url_for('app_login.login'))


if __name__ == '__main__':
    app_login.run(host='0.0.0.0', port=5000)
