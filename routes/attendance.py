# routes/attendance.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from geopy.distance import geodesic
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from datetime import datetime

# Import models and db from models package to avoid circular imports
from models import db
from models.session import Session
from models.attendance import Attendance
import time
import hashlib
import qrcode


import routes.qr

attendance_bp = Blueprint('attendance', __name__)


def get_active_session(session_id=None):
    if session_id:
        try:
            session_id = int(session_id)
        except (TypeError, ValueError):
            session_id = None

    if session_id:
        return Session.query.get(session_id)
    return Session.query.filter_by(status=True).order_by(Session.tanggal.desc(), Session.jam_mulai.desc()).first()


def validate_qr_token(qr_data, session_data):
    if not qr_data or not session_data:
        return False

    for delta in (0, -1):
        timestamp_block = int(time.time() / 30) + delta
        raw_payload = f"session_{session_data.id}_{timestamp_block}_secure_salt"
        secure_token = hashlib.sha256(raw_payload.encode()).hexdigest()
        if secure_token == qr_data:
            return True
    return False


def require_mahasiswa_or_redirect():
    if current_user.role != 'mahasiswa':
        flash("Akses ditolak! Hanya mahasiswa yang dapat melakukan absensi.", "danger")
        return redirect(url_for('auth.dashboard'))
    return None


@attendance_bp.route('/attendance')
@login_required
def attendance_page():
    session_data = get_active_session()
    if not session_data:
        flash("Tidak ada sesi aktif saat ini.", "warning")
    return render_template('attendance.html', session=session_data)


# MODE OFFLINE: Validasi Koordinat GPS
@attendance_bp.route('/absen/offline', methods=['POST'])
@attendance_bp.route('/absen/offline/<int:session_id>', methods=['POST'])
@login_required
def absen_offline(session_id=None):
    redirect_response = require_mahasiswa_or_redirect()
    if redirect_response:
        return redirect_response

    session_data = get_active_session(session_id or request.form.get('session_id'))
    if not session_data:
        flash("Tidak ada sesi aktif untuk absen offline.", "danger")
        return redirect(url_for('attendance.attendance_page'))

    if session_data.mode != 'offline':
        flash("Sesi saat ini bukan sesi offline.", "danger")
        return redirect(url_for('attendance.attendance_page'))
    
    # Ambil data GPS dari form yang dikirim JavaScript frontend
    mhs_lat = request.form.get('latitude')
    mhs_lng = request.form.get('longitude')
    
    if not mhs_lat or not mhs_lng:
        flash("Gagal mendapatkan lokasi GPS. Pastikan izin lokasi aktif.", "danger")
        return redirect(url_for('attendance.attendance_page'))

    coords_mahasiswa = (float(mhs_lat), float(mhs_lng))
    coords_kelas = (session_data.latitude, session_data.longitude)

    # Hitung Jarak dengan Geopy (Haversine)
    jarak_meter = geodesic(coords_mahasiswa, coords_kelas).meters

    if jarak_meter > session_data.radius:
        flash(f"Absen gagal! Anda berada di luar radius kelas ({int(jarak_meter)} meter).", "danger")
        return redirect(url_for('attendance.attendance_page'))

    # Jika lolos validasi, simpan ke database kehadiran
    new_attendance = Attendance(
        user_id=current_user.id,
        session_id=session_data.id,
        status_kehadiran="hadir",
        lokasi=f"Lat: {mhs_lat}, Lng: {mhs_lng}"
    )
    db.session.add(new_attendance)
    db.session.commit()
    
    flash("Absen offline berhasil dicatat! Anda berada di dalam kelas.", "success")
    return redirect(url_for('auth.dashboard'))


# MODE ONLINE: Validasi Upload Gambar Screenshot QR
@attendance_bp.route('/absen/online', methods=['POST'])
@attendance_bp.route('/absen/online/<int:session_id>', methods=['POST'])
@login_required
def absen_online(session_id=None):
    redirect_response = require_mahasiswa_or_redirect()
    if redirect_response:
        return redirect_response

    session_data = get_active_session(session_id or request.form.get('session_id'))
    if not session_data:
        flash("Tidak ada sesi aktif untuk absen online.", "danger")
        return redirect(url_for('attendance.attendance_page'))

    if session_data.mode != 'online':
        flash("Sesi saat ini bukan sesi online.", "danger")
        return redirect(url_for('attendance.attendance_page'))

    if 'qr_image' not in request.files:
        flash("File gambar tidak ditemukan.", "danger")
        return redirect(url_for('attendance.attendance_page'))
        
    file = request.files['qr_image']
    if file.filename == '':
        flash("Tidak ada gambar yang dipilih.", "danger")
        return redirect(url_for('attendance.attendance_page'))

    try:
        # Baca gambar menggunakan OpenCV & PyZbar tanpa menyimpan file ke disk
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Decode isi QR Code
        detected_qr = decode(image)
        
        if not detected_qr:
            flash("QR Code tidak terdeteksi pada gambar. Pastikan gambar jelas.", "danger")
            return redirect(url_for('attendance.attendance_page'))
            
        qr_data = detected_qr[0].data.decode('utf-8')
        
        # Validasi token QR berdasarkan algoritma server
        if not validate_qr_token(qr_data, session_data):
            flash("Token QR tidak valid atau sudah kadaluarsa.", "danger")
            return redirect(url_for('attendance.attendance_page'))

        existing = Attendance.query.filter_by(user_id=current_user.id, session_id=session_data.id).first()
        if existing:
            flash("Anda sudah melakukan absensi pada sesi ini.", "info")
            return redirect(url_for('auth.dashboard'))

        new_attendance = Attendance(
            user_id=current_user.id,
            session_id=session_data.id,
            status_kehadiran='hadir',
            lokasi='upload_qr'
        )
        db.session.add(new_attendance)
        db.session.commit()

        flash("Absen online berhasil dicatat!", "success")
    except Exception as e:
        flash(f"Terjadi kesalahan sistem pengolah gambar: {str(e)}", "danger")
        
    return redirect(url_for('auth.dashboard'))


@attendance_bp.route('/attendance/history')
@login_required
def attendance_history():
    history = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.waktu_absen.desc()).all()
    return render_template('attendance_history.html', attendance_history=history)


@attendance_bp.route('/absen/scan', methods=['POST'])
@login_required
def absen_scan():
    if current_user.role != 'mahasiswa':
        return {"success": False, "message": "Akses ditolak. Hanya mahasiswa yang dapat melakukan absensi."}, 403

    # menerima JSON { token, session_id }
    try:
        data = request.get_json(force=True)
    except Exception:
        data = None

    if not data:
        return {"success": False, "message": "Payload JSON tidak ditemukan."}, 400

    token = data.get('token')
    session_id = data.get('session_id')
    if not token or not session_id:
        return {"success": False, "message": "Token atau session_id kosong."}, 400

    session_data = get_active_session(session_id)
    if not session_data:
        return {"success": False, "message": "Sesi tidak ditemukan."}, 404

    if not session_data.status:
        return {"success": False, "message": "Sesi sudah ditutup."}, 400

    # Validasi token: cocokkan dengan token server (blok waktu sekarang dan satu blok sebelumnya)
    valid = False
    for delta in (0, -1):
        timestamp_block = int(time.time() / 30) + delta
        raw_payload = f"session_{session_data.id}_{timestamp_block}_secure_salt"
        secure_token = hashlib.sha256(raw_payload.encode()).hexdigest()
        if secure_token == token:
            valid = True
            break

    if not valid:
        return {"success": False, "message": "Token QR tidak valid."}, 400

    # Cek duplikat
    existing = Attendance.query.filter_by(user_id=current_user.id, session_id=session_data.id).first()
    if existing:
        return {"success": False, "message": "Anda sudah melakukan absensi pada sesi ini."}, 409

    qr_img = qrcode.QRCode(version=1, box_size=10, border=4)
    qr_img.add_data(token)
    qr_img.make(fit=True)
    img = qr_img.make_image(fill_color="black", back_color="white")
    routes.qr.save_qr_image(img, session_data.id, prefix='used')

    # Simpan ke DB
    new_attendance = Attendance(
        user_id=current_user.id,
        session_id=session_data.id,
        status_kehadiran='hadir',
        lokasi='webcam_scan'
    )
    db.session.add(new_attendance)
    db.session.commit()

    return {"success": True, "message": "Absensi berhasil dicatat via scan."}, 200