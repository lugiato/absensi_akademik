# utils/token_generator.py
import time
import hashlib

def generate_dynamic_token(session_id, secret_salt="app_absensi_secure_salt", window_seconds=30):
    """
    Menghasilkan token dinamis berdasarkan waktu yang kedaluwarsa otomatis.
    """
    # Membagi waktu saat ini dengan window_seconds untuk mendapatkan 'blok' waktu
    timestamp_block = int(time.time() / window_seconds)
    raw_payload = f"session_{session_id}_{timestamp_block}_{secret_salt}"
    
    # Mengenkripsi payload agar tidak bisa ditebak/dimanipulasi
    return hashlib.sha256(raw_payload.encode()).hexdigest()

def validate_dynamic_token(session_id, scanned_token, secret_salt="app_absensi_secure_salt", window_seconds=30):
    """
    Memvalidasi token hasil scan mahasiswa.
    Mengecek blok waktu saat ini dan 1 blok sebelumnya (untuk toleransi delay jaringan).
    """
    current_time = time.time()
    
    # 1. Cek kecocokan di blok waktu saat ini
    current_block = int(current_time / window_seconds)
    token_current = hashlib.sha256(f"session_{session_id}_{current_block}_{secret_salt}".encode()).hexdigest()
    if scanned_token == token_current:
        return True
        
    # 2. Cek kecocokan di blok waktu sebelumnya (grace period toleransi keterlambatan)
    prev_block = current_block - 1
    token_prev = hashlib.sha256(f"session_{session_id}_{prev_block}_{secret_salt}".encode()).hexdigest()
    if scanned_token == token_prev:
        return True
        
    return False