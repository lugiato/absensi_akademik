# models/user.py
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'mahasiswa' atau 'dosen'
    device_id = db.Column(db.String(100), nullable=True)

    # Relasi 1-ke-Banyak (1 User -> Banyak Attendance)
    attendances = db.relationship('Attendance', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.nama} ({self.role})>"