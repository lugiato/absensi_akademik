from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash

# Import db and models from models package
from models import db
from models.user import User
from models.session import Session
from models.attendance import Attendance

# Blueprints
from routes.auth import auth_bp
from routes.attendance import attendance_bp
from routes.session import session_bp
from routes.qr import qr_bp


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'kunci_rahasia_super_aman_123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inisialisasi db terkait app
    db.init_app(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(qr_bp)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            # arahkan ke dashboard yang di-handle blueprint auth
            return redirect(url_for('auth.dashboard'))
        return redirect(url_for('auth.login'))

    return app


def seed_default_users(app):
    with app.app_context():
        if User.query.count() == 0:
            mahasiswa = User(
                nama='Mahasiswa Default',
                email='mahasiswa@example.com',
                password_hash=generate_password_hash('mahasiswa123'),
                role='mahasiswa'
            )
            dosen = User(
                nama='Dosen Default',
                email='dosen@example.com',
                password_hash=generate_password_hash('dosen123'),
                role='dosen'
            )
            db.session.add(mahasiswa)
            db.session.add(dosen)
            db.session.commit()
            print('Default users ditambahkan: mahasiswa@example.com / dosen@example.com')


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Pastikan semua model telah diimport agar tabel dibuat
        db.create_all()
        seed_default_users(app)
    app.run(debug=True)
