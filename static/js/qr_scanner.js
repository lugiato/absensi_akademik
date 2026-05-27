// static/js/qr_scanner.js
// Requires jsQR via CDN in the template: <script src="https://unpkg.com/jsqr/dist/jsQR.js"></script>

let videoStream = null;
let scanActive = false;

async function startScanner(sessionId) {
    // ensure any previous scanner is stopped before creating new elements
    try { if (typeof stopScanner === 'function') stopScanner(); } catch (e) { /* ignore */ }

    const video = document.createElement('video');
    video.setAttribute('id', 'qr-video');
    video.style.width = '100%';
    video.style.borderRadius = '8px';
    const area = document.querySelector('#offline-area');
    // remove placeholder box if exists
    const placeholder = area.querySelector('[data-placeholder]');
    if (placeholder) placeholder.remove();
    area.prepend(video);

    const canvas = document.createElement('canvas');
    canvas.setAttribute('id', 'qr-canvas');
    canvas.style.display = 'none';
    area.appendChild(canvas);

    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
        video.srcObject = videoStream;
        await video.play();
        scanActive = true;
        requestAnimationFrame(() => tickScan(video, canvas, sessionId));
    } catch (e) {
        console.error('Camera error', e);
        area.insertAdjacentHTML('afterbegin', '<p style="color:red;">Gagal mengakses kamera. Izinkan akses kamera di browser Anda.</p>');
    }
}

function stopScanner() {
    scanActive = false;
    if (videoStream) {
        const tracks = videoStream.getTracks();
        tracks.forEach(t => t.stop());
        videoStream = null;
    }
    const video = document.getElementById('qr-video');
    if (video) video.remove();
    const canvas = document.getElementById('qr-canvas');
    if (canvas) canvas.remove();
}

// Ensure camera is stopped when user leaves or reloads the page
try {
    window.addEventListener('beforeunload', function () {
        if (typeof stopScanner === 'function') stopScanner();
    });
} catch (e) {
    // ignore environments without window
}

function tickScan(video, canvas, sessionId) {
    if (!scanActive) return;
    const width = video.videoWidth;
    const height = video.videoHeight;
    if (width === 0 || height === 0) {
        requestAnimationFrame(() => tickScan(video, canvas, sessionId));
        return;
    }
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, width, height);
    const imageData = ctx.getImageData(0, 0, width, height);
    const code = jsQR(imageData.data, imageData.width, imageData.height);
    if (code && code.data) {
        // Found QR token
        stopScanner();
        sendToken(code.data, sessionId);
        return;
    }
    requestAnimationFrame(() => tickScan(video, canvas, sessionId));
}

async function sendToken(token, sessionId) {
    try {
        const res = await fetch('/absen/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ token: token, session_id: sessionId })
        });
        const data = await res.json();
        if (res.ok && data.success) {
            alert('Absensi berhasil: ' + data.message);
            window.location.href = '/';
        } else {
            alert('Gagal absen: ' + (data.message || 'Unknown error'));
            // allow retry
            startScanner(sessionId);
        }
    } catch (e) {
        console.error(e);
        alert('Terjadi kesalahan saat mengirim token ke server.');
    }
}

// Helper to be triggered from attendance.html when offline mode is shown
function initQrScanner(sessionId) {
    if (!('mediaDevices' in navigator) || !navigator.mediaDevices.getUserMedia) {
        const area = document.querySelector('#offline-area');
        area.insertAdjacentHTML('afterbegin', '<p style="color:red;">Browser tidak mendukung kamera.</p>');
        return;
    }
    startScanner(sessionId);
}
