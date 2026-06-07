# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

# Import models and db from models package to avoid circular imports
from models import db
from models.user import User
from models.session import Session
from models.attendance import Attendance

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        user = User.query.filter_by(email=email, role=role).first()

        # Validasi user dan password
        if user and check_password_hash(user.password_hash, password):
            session.clear()
            session.modified = True
            login_user(user)
            flash(f"Selamat datang kembali, {user.nama}!", "success")
            return redirect(url_for('auth.dashboard'))
        
        flash("Email, password, atau role tidak sesuai.", "danger")
        
    return render_template('login.html')

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get_or_404(current_user.get_id())

    if user.role == 'dosen':
        return redirect(url_for('session.admin_panel'))

    active_session = Session.query.filter_by(status=True).order_by(Session.tanggal.desc(), Session.jam_mulai.desc()).first()
    attendance_history = Attendance.query.filter_by(user_id=user.id).order_by(Attendance.waktu_absen.desc()).limit(5).all()
    return render_template('dashboard.html', active_session=active_session, attendance_history=attendance_history)

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get_or_404(current_user.get_id())
    
    if request.method == 'POST':
        nama = request.form.get('nama')
        email = request.form.get('email')
        password = request.form.get('password')
        profile_picture = request.files.get('profile_picture')
        
        # Check if email is being changed and if it already exists
        if email != user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email tersebut sudah digunakan oleh pengguna lain.", "danger")
                return redirect(url_for('auth.profile'))
                
        user.nama = nama
        user.email = email
        
        if password:
            user.password_hash = generate_password_hash(password)
            
        if profile_picture and profile_picture.filename != '':
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            filename = secure_filename(profile_picture.filename)
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
            unique_filename = f"{uuid.uuid4().hex}.{ext}"
            
            # Using absolute path starting from app static folder or relative
            # It's better to use current working directory or app root path, assuming the script runs from root
            upload_folder = os.path.join('static', 'uploads', 'profiles')
            os.makedirs(upload_folder, exist_ok=True)
            
            filepath = os.path.join(upload_folder, unique_filename)
            profile_picture.save(filepath)
            
            user.profile_picture = unique_filename
            
        try:
            db.session.commit()
            flash("Profil berhasil diperbarui!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Terjadi kesalahan saat memperbarui profil.", "danger")
            
        return redirect(url_for('auth.profile'))
        
    return render_template('profile.html', user=user)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    session.modified = True
    return redirect(url_for('auth.login'))