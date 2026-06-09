# models/user.py
from datetime import datetime
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'mahasiswa' atau 'dosen'
    
    # Identitas Akademik
    nim = db.Column(db.String(20), nullable=True, unique=True)  # Untuk mahasiswa
    jurusan = db.Column(db.String(100), nullable=True)
    fakultas = db.Column(db.String(100), nullable=True)
    
    # Profil
    profile_picture = db.Column(db.String(200), nullable=True)
    device_id = db.Column(db.String(100), nullable=True)
    
    # Status & Timestamps
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi 1-ke-Banyak (1 User -> Banyak Attendance)
    attendances = db.relationship('Attendance', backref='user', lazy=True)
    
    # Relasi 1-ke-Banyak (1 Dosen -> Banyak Session yang dia buat)
    created_sessions = db.relationship('Session', backref='creator', lazy=True, foreign_keys='Session.created_by')

    def __repr__(self):
        return f"<User {self.nama} ({self.role})>"