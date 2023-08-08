from flask import (
    Flask, render_template, request, url_for, redirect, flash, send_from_directory
)
from flask_login import (
    UserMixin, login_user, LoginManager, login_required, current_user, logout_user
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


def configure_app():
    app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


configure_app()

db = SQLAlchemy(app)
db.create_all()
login_manager = LoginManager(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return handle_registration()
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return handle_login()
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name=current_user.name)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/download')
@login_required
def download():
    return send_from_directory('static/files', "cheat_sheet.pdf")


def handle_registration():
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')

    if not email or not password:
        flash("Please fill out all fields")
        return redirect(url_for("register"))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("That email already exists, please login instead.")
        return redirect(url_for("register"))

    user = User(email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8),
                name=name)
    db.session.add(user)
    db.session.commit()

    flash("Account created successfully, please login.")
    return redirect(url_for("login"))


def handle_login():
    username = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=username).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        flash("Logged in successfully.")
        return redirect(url_for("secrets"))

    flash("Invalid credentials, please try again.")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
