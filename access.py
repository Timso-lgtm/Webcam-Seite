import socket
import qrcode
from PIL import Image


def show_access_info():
    """Show IP address and generate QR code for local access."""
    try:
        # Get local IP (works on Windows, Linux, macOS)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "127.0.0.1"
    
    url = f"http://{ip}:5000"
    
    # Generate QR code
    try:
        qr = qrcode.QRCode(version=1, box_size=6, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save("qrcode.png")
        print("✅ QR-Code generiert: qrcode.png")
    except Exception as e:
        print(f"⚠️  QR-Code konnte nicht generiert werden: {e}")
    
    print("📱 HANDY-ZUGRIFF:")
    print(f"🌐 URL: {url}")
    print("📷 QR-Code: qrcode.png (falls generiert)")
    print("📱 Handy muss im selben WLAN sein!")


if __name__ == '__main__':
    show_access_info()