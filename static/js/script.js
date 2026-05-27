// static/js/main.js

const modeSelection = document.getElementById('mode-selection');
const offlineArea = document.getElementById('offline-area');
const onlineArea = document.getElementById('online-area');
const statusGps = document.getElementById('status-gps');

function showOfflineMode() {
    modeSelection.classList.add('hidden');
    offlineArea.classList.remove('hidden');
    
    // Minta izin GPS saat mode offline dipilih
    getLocation();
    // Jika ada pemindai QR tersedia, mulai pemindaian webcam
    try {
        if (typeof initQrScanner === 'function' && window.CURRENT_SESSION_ID) {
            initQrScanner(window.CURRENT_SESSION_ID);
        }
    } catch (e) {
        console.warn('QR scanner init skipped', e);
    }
}

function showOnlineMode() {
    modeSelection.classList.add('hidden');
    onlineArea.classList.remove('hidden');
    // stop scanner if switching to online upload
    try { if (typeof stopScanner === 'function') stopScanner(); } catch (e) { /* ignore */ }
}

function resetView() {
    offlineArea.classList.add('hidden');
    onlineArea.classList.add('hidden');
    modeSelection.classList.remove('hidden');
    // stop camera scanner when leaving
    try { if (typeof stopScanner === 'function') stopScanner(); } catch (e) { /* ignore */ }
}

// Fungsi mendapatkan lokasi Geolocation API
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError, {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        });
    } else {
        statusGps.innerHTML = "<span style='color: red;'>Browser Anda tidak mendukung Geolocation.</span>";
    }
}

// Jika lokasi berhasil didapat, masukkan ke input hidden di form
function showPosition(position) {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    
    document.getElementById('lat').value = lat;
    document.getElementById('lng').value = lng;
    
    statusGps.innerHTML = `<span style='color: green;'>✓ Lokasi ditemukan. Silakan scan QR.</span>`;
}

// Handling error saat mengambil GPS
function showError(error) {
    let msg = "";
    switch(error.code) {
        case error.PERMISSION_DENIED:
            msg = "Anda menolak akses lokasi. Absensi offline dibatalkan.";
            break;
        case error.POSITION_UNAVAILABLE:
            msg = "Informasi lokasi tidak tersedia.";
            break;
        case error.TIMEOUT:
            msg = "Waktu permintaan lokasi habis.";
            break;
        default:
            msg = "Terjadi kesalahan yang tidak diketahui.";
            break;
    }
    statusGps.innerHTML = `<span style='color: red;'>${msg}</span>`;
}