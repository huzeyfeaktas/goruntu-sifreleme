import flet as ft
import base64
import cv2
import numpy as np
import random
import pathlib
import os
import locale

# Sistem yerel ayarlarını kullan
locale.setlocale(locale.LC_ALL, '')

def encrypt_image(input_image_path, output_image_path, key):
    """Resmi şifreler."""
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
        random.shuffle(pixel_indices)

        flat_image = image.reshape(-1, 3)
        encrypted_flat_image = np.zeros_like(flat_image)

        for i in range(len(pixel_indices)):
            encrypted_flat_image[i] = flat_image[pixel_indices[i]]

        encrypted_image = encrypted_flat_image.reshape(height, width, channels)
        
        # Türkçe karakterli dosya yolları için alternatif kaydetme yöntemi
        # PNG formatı kullanarak kayıpsız sıkıştırma
        result, encoded_img = cv2.imencode('.png', encrypted_image)
        if result:
            with open(output_image_path, 'wb') as f:
                f.write(encoded_img.tobytes())
            return True
        else:
            return False
    except Exception as e:
        print(f"Şifreleme işlemi sırasında hata oluştu: {e}")
        return False

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
    page.title = "Resim Şifreleme ve Çözme Uygulaması"
    page.window_width = 700
    page.window_height = 900
    page.window_resizable = True
    page.theme_mode = "light"
    page.padding = 20

    # Şifreleme sekmesi için değişkenler
    encrypt_input_file = ft.Ref[ft.Text]()
    encrypt_output_file = ft.Ref[ft.Text]()
    encrypt_key_field = ft.Ref[ft.TextField]()
    encrypt_input_image = ft.Ref[ft.Image]()
    encrypt_output_image = ft.Ref[ft.Image]()
    
    # Şifre çözme sekmesi için değişkenler
    decrypt_input_file = ft.Ref[ft.Text]()
    decrypt_output_file = ft.Ref[ft.Text]()
    decrypt_key_field = ft.Ref[ft.TextField]()
    decrypt_input_image = ft.Ref[ft.Image]()
    decrypt_output_image = ft.Ref[ft.Image]()
    
    # Global FilePicker'lar
    encrypt_input_picker = ft.FilePicker()
    encrypt_output_picker = ft.FilePicker()
    decrypt_input_picker = ft.FilePicker()
    decrypt_output_picker = ft.FilePicker()
    
    # FilePicker'ları overlay'e ekle
    page.overlay.extend([encrypt_input_picker, encrypt_output_picker, decrypt_input_picker, decrypt_output_picker])
    page.update()

    def pick_encrypt_input_file(e):
        """Şifrelenecek dosya seçimi."""
        def file_picker_result(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0 and e.files[0].path:
                file_path = e.files[0].path
                encrypt_input_file.current.value = file_path
                # Şifrelenmiş görseli temizle
                encrypt_output_image.current.src = None
                # Görseli göster (base64 ile)
                with open(file_path, "rb") as f:
                    encoded_string = base64.b64encode(f.read()).decode("utf-8")
                encrypt_input_image.current.src = None
                encrypt_input_image.current.src_base64 = encoded_string
            else:
                encrypt_input_file.current.value = "Henüz dosya seçilmedi"
                encrypt_input_image.current.src = None
                encrypt_input_image.current.src_base64 = None
            page.update()
        
        encrypt_input_picker.on_result = file_picker_result
        encrypt_input_picker.pick_files(
            dialog_title="Şifrelenecek resmi seçin",
            allowed_extensions=["jpg", "jpeg", "png", "bmp"]
        )

    def pick_encrypt_output_file(e):
        """Şifrelenmiş dosyanın kaydedileceği yer."""
        def file_picker_result(e: ft.FilePickerResultEvent):
            if e.path:
                encrypt_output_file.current.value = e.path
                page.update()
        
        encrypt_output_picker.on_result = file_picker_result
        encrypt_output_picker.save_file(
            dialog_title="Şifrelenmiş resmi kaydet",
            file_name="sifreli_resim.png"
        )

    def pick_decrypt_input_file(e):
        """Çözülecek dosya seçimi."""
        def file_picker_result(e: ft.FilePickerResultEvent):
            if e.files and e.files[0].path:
                file_path = e.files[0].path
                decrypt_input_file.current.value = file_path
                decrypt_output_image.current.src = None
                decrypt_output_image.current.src_base64 = None
                try:
                    with open(file_path, "rb") as f:
                        encoded_string = base64.b64encode(f.read()).decode("utf-8")
                    decrypt_input_image.current.src = None
                    decrypt_input_image.current.src_base64 = encoded_string
                except Exception as ex:
                    snack_bar = ft.SnackBar(
                        content=ft.Text(f"Görsel yüklenirken hata oluştu: {ex}"),
                        bgcolor=ft.colors.RED
                    )
                    page.overlay.append(snack_bar)
                    snack_bar.open = True
            else:
                decrypt_input_file.current.value = "Henüz dosya seçilmedi"
                decrypt_input_image.current.src = None
                decrypt_input_image.current.src_base64 = None
            page.update()

        decrypt_input_picker.on_result = file_picker_result
        decrypt_input_picker.pick_files(
            dialog_title="Çözülecek şifrelenmiş resmi seçin",
            allowed_extensions=["jpg", "jpeg", "png", "bmp"]
        )

    def pick_decrypt_output_file(e):
        """Çözülmüş dosyanın kaydedileceği yer."""
        def file_picker_result(e: ft.FilePickerResultEvent):
            if e.path:
                decrypt_output_file.current.value = e.path
                page.update()
        
        decrypt_output_picker.on_result = file_picker_result
        decrypt_output_picker.save_file(
            dialog_title="Çözülmüş resmi kaydet",
            file_name="cozulmus_resim.png"
        )

    def save_encrypted_image(e):
        """Şifrelenmiş resmi kaydet."""
        if not encrypt_input_file.current.value or encrypt_input_file.current.value == "Henüz dosya seçilmedi":
            snack_bar = ft.SnackBar(
                content=ft.Text("Lütfen şifrelenecek bir resim seçin!"),
                bgcolor=ft.colors.RED
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()
            return
        
        if not encrypt_output_file.current.value or encrypt_output_file.current.value == "Henüz konum seçilmedi":
            snack_bar = ft.SnackBar(
                content=ft.Text("Lütfen kayıt konumu seçin!"),
                bgcolor=ft.colors.RED
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()
            return
        
        if not encrypt_key_field.current.value:
            snack_bar = ft.SnackBar(
                content=ft.Text("Lütfen bir şifre girin!"),
                bgcolor=ft.colors.RED
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()
            return
        
        success = encrypt_image(
            encrypt_input_file.current.value,
            encrypt_output_file.current.value,
            encrypt_key_field.current.value
        )
        
        if success:
            # Şifrelenmiş görseli göster (base64 ile)
            output_path = encrypt_output_file.current.value
            with open(output_path, "rb") as f:
                encoded_string = base64.b64encode(f.read()).decode("utf-8")
            encrypt_output_image.current.src = None
            encrypt_output_image.current.src_base64 = encoded_string
            
            snack_bar = ft.SnackBar(
                content=ft.Text("Resim başarıyla şifrelendi!"),
                bgcolor=ft.colors.GREEN
            )
        else:
            snack_bar = ft.SnackBar(
                content=ft.Text("Resim şifreleme işlemi başarısız oldu!"),
                bgcolor=ft.colors.RED
            )
        
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    def save_decrypted_image(e):
        """Çözülmüş resmi kaydet."""
        if not decrypt_input_file.current.value or decrypt_input_file.current.value == "Henüz dosya seçilmedi":
            snack_bar = ft.SnackBar(
                content=ft.Text("Lütfen çözülecek bir resim seçin!"),
                bgcolor=ft.colors.RED
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()
            return
        
        if not decrypt_output_file.current.value or decrypt_output_file.current.value == "Henüz konum seçilmedi":
            snack_bar = ft.SnackBar(
                content=ft.Text("Lütfen kayıt konumu seçin!"),
                bgcolor=ft.colors.RED
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()
            return
        
        if not decrypt_key_field.current.value:
            snack_bar = ft.SnackBar(
                content=ft.Text("Lütfen şifreyi girin!"),
                bgcolor=ft.colors.RED
            )
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()
            return
        
        success = decrypt_image(
            decrypt_input_file.current.value,
            decrypt_output_file.current.value,
            decrypt_key_field.current.value
        )
        
        if success:
            # Çözülen görseli göster (base64 ile)
            output_path = decrypt_output_file.current.value
            with open(output_path, "rb") as f:
                encoded_string = base64.b64encode(f.read()).decode("utf-8")
            decrypt_output_image.current.src = None
            decrypt_output_image.current.src_base64 = encoded_string
            
            snack_bar = ft.SnackBar(
                content=ft.Text("Resim başarıyla çözüldü!"),
                bgcolor=ft.colors.GREEN
            )
        else:
            snack_bar = ft.SnackBar(
                content=ft.Text("Resim çözme işlemi başarısız oldu!"),
                bgcolor=ft.colors.RED
            )
        
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    def reset_encrypt_tab(e):
        """Şifreleme sekmesini sıfırla."""
        encrypt_input_file.current.value = "Henüz dosya seçilmedi"
        encrypt_output_file.current.value = "Henüz konum seçilmedi"
        encrypt_key_field.current.value = ""
        encrypt_input_image.current.src = None
        encrypt_input_image.current.src_base64 = None
        encrypt_output_image.current.src = None
        encrypt_output_image.current.src_base64 = None
        page.update()

    def reset_decrypt_tab(e):
        """Şifre çözme sekmesini sıfırla."""
        decrypt_input_file.current.value = "Henüz dosya seçilmedi"
        decrypt_output_file.current.value = "Henüz konum seçilmedi"
        decrypt_key_field.current.value = ""
        decrypt_input_image.current.src = None
        decrypt_input_image.current.src_base64 = None
        decrypt_output_image.current.src = None
        decrypt_output_image.current.src_base64 = None
        page.update()

    # Şifreleme sekmesi
    encrypt_tab = ft.Tab(
        text="Şifreleme",
        icon=ft.icons.LOCK,
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    "Resim Şifreleme",
                    size=24,
                    weight="bold",
                    text_align="center",
                    color="#DC143C"
                ),
                ft.Divider(),
                
                # Ana yatay düzen
                ft.Row([
                    # Sol taraf - Kontroller
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Şifrelenecek Resim:", size=16, weight="w500"),
                            ft.ElevatedButton(
                                "Resim Seç",
                                icon=ft.icons.FOLDER_OPEN,
                                on_click=pick_encrypt_input_file,
                                color=ft.colors.RED
                            ),
                            ft.Text(
                                ref=encrypt_input_file,
                                value="Henüz dosya seçilmedi",
                                size=12,
                                color="#666666"
                            ),
                            
                            ft.Text("Kayıt Konumu:", size=16, weight="w500"),
                            ft.ElevatedButton(
                                "Kayıt Yeri Seç",
                                icon=ft.icons.SAVE,
                                on_click=pick_encrypt_output_file,
                                color=ft.colors.RED
                            ),
                            ft.Text(
                                ref=encrypt_output_file,
                                value="Henüz konum seçilmedi",
                                size=12,
                                color="#666666"
                            ),
                            
                            ft.TextField(
                                ref=encrypt_key_field,
                                label="Şifre",
                                hint_text="Şifrenizi girin",
                                password=True,
                                can_reveal_password=True,
                                width=300
                            ),
                            
                            ft.ElevatedButton(
                                "Şifrele",
                                icon=ft.icons.LOCK,
                                on_click=save_encrypted_image,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.RED,
                                    color=ft.colors.WHITE
                                )
                            ),
                            
                            ft.ElevatedButton(
                                "Sıfırla",
                                icon=ft.icons.REFRESH,
                                on_click=reset_encrypt_tab,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.ORANGE,
                                    color=ft.colors.WHITE
                                )
                            ),
                        ], spacing=10),
                        width=350,
                        padding=10
                    ),
                    
                    # Sağ taraf - Görseller
                    ft.Container(
                        content=ft.Column([
                            # Seçilen görsel
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Seçilen Görsel:", size=14, weight="w500"),
                                    ft.Image(
                                        ref=encrypt_input_image,
                                        src=None,
                                        width=150,
                                        height=150,
                                        fit="contain",
                                        border_radius=10
                                    )
                                ], horizontal_alignment="center"),
                                bgcolor="#f5f5f5",
                                padding=10,
                                border_radius=10,
                                margin=ft.margin.only(bottom=10)
                            ),
                            
                            # Şifrelenmiş görsel
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Şifrelenmiş Görsel:", size=14, weight="w500"),
                                    ft.Image(
                                        ref=encrypt_output_image,
                                        src=None,
                                        width=150,
                                        height=150,
                                        fit="contain",
                                        border_radius=10
                                    )
                                ], horizontal_alignment="center"),
                                bgcolor="#f5f5f5",
                                padding=10,
                                border_radius=10
                            ),
                        ], spacing=10),
                        width=200,
                        padding=10
                    )
                ], spacing=20, alignment="start")
            ], spacing=15),
            padding=20
        )
    )

    # Şifre çözme sekmesi
    decrypt_tab = ft.Tab(
        text="Şifre Çözme",
        icon=ft.icons.LOCK_OPEN,
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    "Resim Şifre Çözme",
                    size=24,
                    weight="bold",
                    text_align="center",
                    color="#228B22"
                ),
                ft.Divider(),
                
                # Ana yatay düzen
                ft.Row([
                    # Sol taraf - Kontroller
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Çözülecek Şifrelenmiş Resim:", size=16, weight="w500"),
                            ft.ElevatedButton(
                                "Resim Seç",
                                icon=ft.icons.FOLDER_OPEN,
                                on_click=pick_decrypt_input_file,
                                color=ft.colors.GREEN
                            ),
                            ft.Text(
                                ref=decrypt_input_file,
                                value="Henüz dosya seçilmedi",
                                size=12,
                                color="#666666"
                            ),
                            
                            ft.Text("Kayıt Konumu:", size=16, weight="w500"),
                            ft.ElevatedButton(
                                "Kayıt Yeri Seç",
                                icon=ft.icons.SAVE,
                                on_click=pick_decrypt_output_file,
                                color=ft.colors.GREEN
                            ),
                            ft.Text(
                                ref=decrypt_output_file,
                                value="Henüz konum seçilmedi",
                                size=12,
                                color="#666666"
                            ),
                            
                            ft.TextField(
                                ref=decrypt_key_field,
                                label="Şifre",
                                hint_text="Şifrenizi girin",
                                password=True,
                                can_reveal_password=True,
                                width=300
                            ),
                            
                            ft.ElevatedButton(
                                "Şifreyi Çöz",
                                icon=ft.icons.LOCK_OPEN,
                                on_click=save_decrypted_image,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.GREEN,
                                    color=ft.colors.WHITE
                                )
                            ),
                            
                            ft.ElevatedButton(
                                "Sıfırla",
                                icon=ft.icons.REFRESH,
                                on_click=reset_decrypt_tab,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.ORANGE,
                                    color=ft.colors.WHITE
                                )
                            ),
                        ], spacing=10),
                        width=350,
                        padding=10
                    ),
                    
                    # Sağ taraf - Görseller
                    ft.Container(
                        content=ft.Column([
                            # Seçilen şifrelenmiş görsel
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Seçilen Şifrelenmiş Görsel:", size=14, weight="w500"),
                                    ft.Image(
                                        ref=decrypt_input_image,
                                        src=False,
                                        width=150,
                                        height=150,
                                        fit="contain",
                                        border_radius=10
                                    )
                                ], horizontal_alignment="center"),
                                bgcolor="#f5f5f5",
                                padding=10,
                                border_radius=10,
                                margin=ft.margin.only(bottom=10)
                            ),
                            
                            # Çözülen görsel
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Çözülen Görsel:", size=14, weight="w500"),
                                    ft.Image(
                                        ref=decrypt_output_image,
                                        src=False,
                                        width=150,
                                        height=150,
                                        fit="contain",
                                        border_radius=10
                                    )
                                ], horizontal_alignment="center"),
                                bgcolor="#f5f5f5",
                                padding=10,
                                border_radius=10
                            ),
                        ], spacing=10),
                        width=200,
                        padding=10
                    )
                ], spacing=20, alignment="start")
            ], spacing=15),
            padding=20
        )
    )

    # Ana tab görünümü
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[encrypt_tab, decrypt_tab],
        expand=1
    )

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text(
                    "🔮 Görsel Şifreleme Uygulaması 🔮",
                    size=30,
                    weight="bold",
                    text_align="center",
                    color="#8A2BE2"
                ),
                tabs
            ], spacing=20),
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)