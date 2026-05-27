# utils/qr_generator.py
import qrcode
import io

def create_qr_image(data_teks):
    """
    Membuat gambar QR Code dari data teks dan mengembalikannya
    sebagai objek BytesIO agar bisa langsung dikirim via Flask send_file().
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data_teks)
    qr.make(fit=True)
    
    # Membuat gambar QR
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Menyimpan ke memori buffer (BytesIO)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0) # Kembalikan kursor baca ke awal file
    
    return img_io