# routes/session.py
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from datetime import datetime

# Import models and db from models package to avoid circular imports
from models import db
from models.session import Session
from models.attendance import Attendance
from models.user import User

session_bp = Blueprint('session', __name__)

@session_bp.route('/admin')
@login_required
def admin_panel():
    # Proteksi: Hanya dosen yang bisa masuk ke panel admin
    if current_user.role != 'dosen':
        flash("Akses ditolak! Halaman ini khusus untuk Dosen.", "danger")
        return redirect(url_for('auth.dashboard'))
        
    # Ambil semua sesi hari ini untuk ditampilkan di tabel manajemen
    today = datetime.today().date()
    sessions = Session.query.filter_by(tanggal=today).all()
    return render_template('admin.html', sessions=sessions)

@session_bp.route('/admin/create_session', methods=['POST'])
@login_required
def create_session():
    if current_user.role != 'dosen':
        return "Unauthorized", 403

    mata_kuliah = request.form.get('mata_kuliah')
    mode = request.form.get('mode')
    jam_mulai_str = request.form.get('jam_mulai')
    jam_selesai_str = request.form.get('jam_selesai')

    # Konversi string input HTML time ke objek python time
    jam_mulai = datetime.strptime(jam_mulai_str, '%H:%M').time()
    jam_selesai = datetime.strptime(jam_selesai_str, '%H:%M').time()

    # Contoh Koordinat Default Kampus (Bisa dinamis dari GPS Dosen jika dikembangkan)
    default_lat = -6.200000 
    default_lng = 106.816666

    new_session = Session(
        mata_kuliah=mata_kuliah,
        mode=mode,
        tanggal=datetime.today().date(),
        jam_mulai=jam_mulai,
        jam_selesai=jam_selesai,
        status=True,
        latitude=default_lat if mode == 'offline' else None,
        longitude=default_lng if mode == 'offline' else None,
        radius=50 # radius toleransi 50 meter
    )

    db.session.add(new_session)
    db.session.commit()

    flash(f"Sesi kelas {mata_kuliah} berhasil dibuka!", "success")
    return redirect(url_for('session.admin_panel'))


@session_bp.route('/admin/close_session/<int:session_id>', methods=['POST'])
@login_required
def close_session(session_id):
    if current_user.role != 'dosen':
        flash("Akses ditolak! Hanya Dosen yang dapat menutup sesi.", "danger")
        return redirect(url_for('session.admin_panel'))

    session_data = Session.query.get_or_404(session_id)
    if not session_data.status:
        flash("Sesi sudah ditutup.", "info")
        return redirect(url_for('session.admin_panel'))

    session_data.status = False
    db.session.commit()
    flash(f"Sesi {session_data.mata_kuliah} berhasil ditutup.", "success")
    return redirect(url_for('session.admin_panel'))


@session_bp.route('/admin/delete_session/<int:session_id>', methods=['POST'])
@login_required
def delete_session(session_id):
    if current_user.role != 'dosen':
        flash("Akses ditolak! Hanya Dosen yang dapat menghapus sesi.", "danger")
        return redirect(url_for('session.admin_panel'))

    session_data = Session.query.get_or_404(session_id)
    db.session.delete(session_data)
    db.session.commit()
    flash(f"Sesi {session_data.mata_kuliah} telah dihapus.", "success")
    return redirect(url_for('session.admin_panel'))


@session_bp.route('/admin/session/<int:session_id>')
@login_required
def session_detail(session_id):
    if current_user.role != 'dosen':
        flash("Akses ditolak!", "danger")
        return redirect(url_for('auth.dashboard'))
        
    session_data = Session.query.get_or_404(session_id)
    
    attendance_list = db.session.query(Attendance, User).\
        join(User, Attendance.user_id == User.id).\
        filter(Attendance.session_id == session_id).\
        order_by(Attendance.waktu_absen.desc()).all()
        
    return render_template('session_detail.html', session=session_data, attendance_list=attendance_list)