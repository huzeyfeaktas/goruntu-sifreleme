from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import random
import io
import os
from PIL import Image
import tempfile
import locale

# Sistem yerel ayarlarını kullan
locale.setlocale(locale.LC_ALL, '')

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Serve the main HTML file
@app.route('/')
def index():
    return send_file('index.html')

def encrypt_image_data(image_data, key):
    """Resim verisini şifreler."""
    try:
        # Numpy array'e çevir ve OpenCV ile decode et
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Resim yüklenemedi")
            
        height, width, channels = image.shape

        key_bytes = [ord(k) for k in key]
        seed = sum(key_bytes)
        random.seed(seed)

        pixel_indices = list(range(height * width))
        random.shuffle(pixel_indices)

        flat_image = image.reshape(-1, 3)
        encrypted_flat_image = np.zeros_like(flat_image)

        for i in range(len(pixel_indices)):
            encrypted_flat_image[i] = flat_image[pixel_indices[i]]

        encrypted_image = encrypted_flat_image.reshape(height, width, channels)
        
        # PNG formatı kullanarak kayıpsız sıkıştırma
        result, encoded_img = cv2.imencode('.png', encrypted_image)
        if result:
            return encoded_img.tobytes()
        else:
            raise ValueError("Şifreleme işlemi başarısız")
            
    except Exception as e:
        raise Exception(f"Şifreleme işlemi sırasında hata oluştu: {e}")

def decrypt_image_data(image_data, key):
    """Şifrelenmiş resim verisini çözer."""
    try:
        # Numpy array'e çevir ve OpenCV ile decode et
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Resim yüklenemedi")
            
        height, width, channels = image.shape

        key_bytes = [ord(k) for k in key]
        seed = sum(key_bytes)
        random.seed(seed)

        pixel_indices = list(range(height * width))
        random.shuffle(pixel_indices)  # Şifreleme ile aynı sırayı elde etmek için

        flat_image = image.reshape(-1, 3)
        decrypted_flat_image = np.zeros_like(flat_image)

        # Şifre çözme işlemi
        for i, pos in enumerate(pixel_indices):
            decrypted_flat_image[pos] = flat_image[i]

        decrypted_image = decrypted_flat_image.reshape(height, width, channels)
        
        # PNG formatı kullanarak kayıpsız sıkıştırma
        result, encoded_img = cv2.imencode('.png', decrypted_image)
        if result:
            return encoded_img.tobytes()
        else:
            raise ValueError("Şifre çözme işlemi başarısız")
            
    except Exception as e:
        raise Exception(f"Şifre çözme işlemi sırasında hata oluştu: {e}")

@app.route('/api/encrypt', methods=['POST'])
def encrypt_endpoint():
    """Resim şifreleme API endpoint'i."""
    try:
        # Form verilerini kontrol et
        if 'image' not in request.files:
            return jsonify({'error': 'Resim dosyası bulunamadı'}), 400
        
        if 'password' not in request.form:
            return jsonify({'error': 'Şifre bulunamadı'}), 400
        
        image_file = request.files['image']
        password = request.form['password']
        
        if image_file.filename == '':
            return jsonify({'error': 'Dosya seçilmedi'}), 400
        
        if not password.strip():
            return jsonify({'error': 'Şifre boş olamaz'}), 400
        
        # Dosya türünü kontrol et
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        file_ext = os.path.splitext(image_file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Desteklenmeyen dosya türü'}), 400
        
        # Resim verisini oku
        image_data = image_file.read()
        
        # Şifreleme işlemini gerçekleştir
        encrypted_data = encrypt_image_data(image_data, password)
        
        # Şifrelenmiş resmi döndür
        return send_file(
            io.BytesIO(encrypted_data),
            mimetype='image/png',
            as_attachment=True,
            download_name='sifreli_resim.png'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/decrypt', methods=['POST'])
def decrypt_endpoint():
    """Resim şifre çözme API endpoint'i."""
    try:
        # Form verilerini kontrol et
        if 'image' not in request.files:
            return jsonify({'error': 'Resim dosyası bulunamadı'}), 400
        
        if 'password' not in request.form:
            return jsonify({'error': 'Şifre bulunamadı'}), 400
        
        image_file = request.files['image']
        password = request.form['password']
        
        if image_file.filename == '':
            return jsonify({'error': 'Dosya seçilmedi'}), 400
        
        if not password.strip():
            return jsonify({'error': 'Şifre boş olamaz'}), 400
        
        # Dosya türünü kontrol et
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        file_ext = os.path.splitext(image_file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Desteklenmeyen dosya türü'}), 400
        
        # Resim verisini oku
        image_data = image_file.read()
        
        # Şifre çözme işlemini gerçekleştir
        decrypted_data = decrypt_image_data(image_data, password)
        
        # Çözülmüş resmi döndür
        return send_file(
            io.BytesIO(decrypted_data),
            mimetype='image/png',
            as_attachment=True,
            download_name='cozulmus_resim.png'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Sunucu durumu kontrolü."""
    return jsonify({
        'status': 'healthy',
        'message': 'Görüntü şifreleme servisi çalışıyor'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint bulunamadı'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Sunucu hatası'}), 500

if __name__ == '__main__':
    print("🚀 Görüntü Şifreleme Web Uygulaması Başlatılıyor...")
    print("📱 Uygulama: http://localhost:8080")
    print("🔧 API Durumu: http://localhost:8080/api/health")
    print("⚡ Geliştirme modu aktif")
    
    app.run(
        host='127.0.0.1',
        port=8080,
        debug=True,
        threaded=True
    )