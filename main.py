from flask import Flask, render_template, request
from login import app_login, load_user
from flask_login import LoginManager, login_required, current_user
from dbloader import connect_to_db

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True  # Remove in final version
app.config['SECRET_KEY'] = 'bruh'
app.jinja_env.auto_reload = True  # Remove in final version

conn, cur = connect_to_db()

app.register_blueprint(app_login)

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
    if request.method == 'GET':
        return render_template('book_server.html')
    if request.method == 'POST':
        return render_template('book_server.html')
    return render_template('index.html')


@app.route('/view_server', methods=['GET'])
def view_server():
    pass


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
