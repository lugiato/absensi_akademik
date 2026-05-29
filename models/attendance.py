# models/attendance.py
from datetime import datetime
from . import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    
    waktu_absen = db.Column(db.DateTime, default=datetime.now)
    status_kehadiran = db.Column(db.String(20), nullable=False) # 'hadir', 'terlambat', 'izin', 'alpha'
    lokasi = db.Column(db.Text, nullable=True) # Untuk menyimpan log koordinat saat absen

    def __repr__(self):
        return f"<Attendance UserID:{self.user_id} - SesiID:{self.session_id}>"