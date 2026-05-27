# routes/qr.py
from flask import Blueprint, render_template, send_file, abort
from flask_login import login_required
import qrcode
import io
import time
import hashlib

# Import Session model from models package
from models.session import Session

qr_bp = Blueprint('qr', __name__)


def get_active_session(session_id=None):
    if session_id:
        return Session.query.get(session_id)
    return Session.query.filter_by(status=True).order_by(Session.tanggal.desc(), Session.jam_mulai.desc()).first()


@qr_bp.route('/qr')
@login_required
def qr_landing():
    session_data = get_active_session()
    if not session_data:
        return abort(404, "Tidak ada sesi aktif untuk menampilkan QR.")
    return render_template('qr.html', session=session_data)


@qr_bp.route('/qr/<int:session_id>')
@login_required
def display_qr(session_id):
    session_data = get_active_session(session_id)
    if not session_data:
        return abort(404, "Sesi tidak ditemukan.")
    return render_template('qr.html', session=session_data)


@qr_bp.route('/qr/generate/<int:session_id>')
@login_required
def generate_qr_image(session_id):
    session_data = Session.query.get_or_404(session_id)
    
    if not session_data.status:
        return abort(400, "Sesi absensi sudah ditutup.")

    # LOGIKA QR DINAMIS: Buat token unik yang berubah setiap 30 detik
    # Menggabungkan ID Sesi + Waktu Saat Ini (dibulatkan per 30 detik)
    timestamp_block = int(time.time() / 30)
    raw_payload = f"session_{session_id}_{timestamp_block}_secure_salt"
    
    # Enkripsi payload menjadi SHA256 agar tidak bisa dimanipulasi mahasiswa
    secure_token = hashlib.sha256(raw_payload.encode()).hexdigest()

    # Generate QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(secure_token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Simpan gambar ke memori sementara (BytesIO) agar tidak membebani penyimpanan server
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')