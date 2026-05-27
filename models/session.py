# models/session.py
from . import db

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    mata_kuliah = db.Column(db.String(100), nullable=False)
    mode = db.Column(db.String(20), nullable=False) # 'online' atau 'offline'
    tanggal = db.Column(db.Date, nullable=False)
    jam_mulai = db.Column(db.Time, nullable=False)
    jam_selesai = db.Column(db.Time, nullable=False)
    status = db.Column(db.Boolean, default=True) # True = Aktif, False = Selesai
    
    # Koordinat untuk mode offline
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    radius = db.Column(db.Integer, default=50) # Toleransi jarak dalam meter

    # Relasi 1-ke-Banyak (1 Sesi -> Banyak Attendance)
    attendances = db.relationship('Attendance', backref='session_ref', lazy=True)

    def __repr__(self):
        return f"<Session {self.mata_kuliah} - {self.tanggal}>"