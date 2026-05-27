# utils/gps_validator.py
from geopy.distance import geodesic

def calculate_distance(coord_user, coord_target):
    """
    Menghitung jarak aktual antara dua titik koordinat.
    Format parameter: tuple (latitude, longitude)
    """
    try:
        return geodesic(coord_user, coord_target).meters
    except ValueError:
        # Menghindari error jika koordinat yang dimasukkan tidak valid (misal: None atau format salah)
        return float('inf')

def is_within_radius(user_lat, user_lng, class_lat, class_lng, radius_meters=50):
    """
    Memvalidasi apakah posisi mahasiswa berada di dalam radius kelas.
    Mengembalikan (Boolean_Status, Jarak_Aktual).
    """
    # Pengecekan jika ada data yang kosong
    if not all([user_lat, user_lng, class_lat, class_lng]):
        return False, 0
        
    user_coords = (float(user_lat), float(user_lng))
    class_coords = (float(class_lat), float(class_lng))
    
    # Hitung jarak
    jarak_aktual = calculate_distance(user_coords, class_coords)
    
    # Validasi
    is_valid = jarak_aktual <= radius_meters
    
    return is_valid, int(jarak_aktual)