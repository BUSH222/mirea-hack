from flask import Flask, render_template, redirect, request

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True  # Remove in final version
app.jinja_env.auto_reload = True  # Remove in final version

@app.route('/')
def main():
    return render_template("main.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")


if __name__ == '__main__':
    app.run(host='localhost', port=5500, debug=True)