import flet as ft
import cv2
import numpy as np
import random
import pathlib
import os
import locale

# Sistem yerel ayarlarını kullan
locale.setlocale(locale.LC_ALL, '')

def decrypt_image(input_image_path, output_image_path, key):
    """Şifrelenmiş resmi çözer."""
    # Türkçe karakterleri içeren dosya yollarını düzgün işlemek için
    try:
        # OpenCV'nin Türkçe karakter sorunu için alternatif yöntem
        with open(input_image_path, 'rb') as f:
            image_data = f.read()
        
        # Numpy array'e çevir ve OpenCV ile decode et
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            print(f"Hata: Resim yüklenemedi: {input_image_path}")
            return False
            
        height, width, channels = image.shape

        key_bytes = [ord(k) for k in key]
        seed = sum(key_bytes)
        random.seed(seed)

        pixel_indices = list(range(height * width))
        random.shuffle(pixel_indices)  # Önemli: Şifreleme ile aynı sırayı elde etmek için tekrar çağırıyoruz

        flat_image = image.reshape(-1, 3)
        decrypted_flat_image = np.zeros_like(flat_image)

        # Düzeltme:
        for i, pos in enumerate(pixel_indices):
            decrypted_flat_image[pos] = flat_image[i]

        decrypted_image = decrypted_flat_image.reshape(height, width, channels)
        
        # Türkçe karakterli dosya yolları için alternatif kaydetme yöntemi
        # PNG formatı kullanarak kayıpsız sıkıştırma
        result, encoded_img = cv2.imencode('.png', decrypted_image)
        if result:
            with open(output_image_path, 'wb') as f:
                f.write(encoded_img.tobytes())
            return True
        else:
            return False
    except Exception as e:
        print(f"Şifre çözme işlemi sırasında hata oluştu: {e}")
        return False

def main(page: ft.Page):
    """Ana uygulama fonksiyonu."""
    page.title = "Resim Şifre Çözme"
    page.window_width = 400
    page.window_height = 200
    page.window_center()
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    image_path = ""
    key_text = ft.TextField(label="Şifre Çözme Anahtarı", password=True)
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    def pick_image(e):
        """Dosya seçme diyaloğunu açar."""
        file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg", "bmp", "gif"]
        )

    def image_selected(e):
        """Seçilen resmi işler."""
        nonlocal image_path
        if e.files:
            selected_file = e.files[0]
            image_path = selected_file.path
            page.snack_bar = ft.SnackBar(content=ft.Text("Resim seçildi: " + image_path))
            page.snack_bar.open = True
            page.update()

    def decrypt_and_save(e):
        """Resmi çözer ve kaydetme diyaloğunu açar."""
        nonlocal image_path
        if image_path and key_text.value:
            save_file_dialog.save_file(
                file_name="decrypted_image.jpg",
                initial_directory=str(pathlib.Path.home()),
                allowed_extensions=["jpg", "jpeg", "png"],
            )
        else:
            page.snack_bar = ft.SnackBar(content=ft.Text("Resim ve şifre girin!"))
            page.snack_bar.open = True
            page.update()

    def save_decrypted_image(e):
        """Çözülen resmi kaydeder."""
        nonlocal image_path
        if e.path:
            success = decrypt_image(image_path, e.path, key_text.value)
            if success:
                page.snack_bar = ft.SnackBar(content=ft.Text(f"Resim çözüldü ve {e.path} konumuna kaydedildi!"))
            else:
                page.snack_bar = ft.SnackBar(content=ft.Text("Resim çözme işlemi başarısız oldu!"))
            page.snack_bar.open = True
            page.update()

    save_file_dialog = ft.FilePicker()
    save_file_dialog.on_result = save_decrypted_image
    page.overlay.append(save_file_dialog)

    # FilePicker olaylarını bağla
    file_picker.on_result = image_selected
    
    page.add(
        ft.Column(
            [
                ft.ElevatedButton("Resim Seç", on_click=pick_image),
                key_text,
                ft.ElevatedButton("Şifreyi Çöz ve Kaydet", on_click=decrypt_and_save),
            ],
            alignment="center",
            horizontal_alignment="center",
        )
    )

ft.app(target=main)