import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QWidget, QSizePolicy, QHBoxLayout, QVBoxLayout, QSlider
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import Qt, QRectF
import cv2

def resize_image(img, scale, center=None):
    
    imglen=len(img.shape)
    
    if scale<1:
            # Orjinal resmin boyutları
            height, width = img.shape[:2]
            # Yeni boyutları hesapla
            new_width = int(width * scale )
            new_height = int(height * scale )
            # Yeniden boyutlandır
            resized_image = cv2.resize(img, (new_width, new_height))
            # Siyah bir arka plan oluştur
            black_background = np.zeros((height, width, 3), np.uint8)
            # Yeniden boyutlandırılmış resmi siyah arka planın merkezine yerleştiriyoruz
            x_offset = (width - new_width) // 2
            y_offset = (height - new_height) // 2
            black_background[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized_image
            return black_background
        
    else:
            # Orjinal resmin boyutları
            height, width = img.shape[:2]
            # Yeni boyutları hesapla
            new_width = int(width * scale)
            new_height = int(height * scale)
            # Yeniden boyutlandırma işlemi
            resized_image = cv2.resize(img, (new_width, new_height))
            # Orta noktayı al
            center_x = new_width // 2
            center_y = new_height // 2
            # Yakınlaştırılmış resmi kesmek için sınırları hesapla
            start_x = max(center_x - width // 2, 0)
            end_x = min(center_x + width // 2, new_width)
            start_y = max(center_y - height // 2, 0)
            end_y = min(center_y + height // 2, new_height)
            # Yakınlaştırılmış resmi al
            zoomed_image = resized_image[start_y:end_y, start_x:end_x]
            return zoomed_image
        
        
        
    
        

class ImageProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Binary Dönüşüm')
        self.setFixedSize(1280, 720)

        # Orijinal resim ve işlenmiş resim değişkenleri
        self.original_image = np.zeros((500, 500, 3), dtype=np.uint8)
        self.processed_image = np.zeros((500, 500, 3), dtype=np.uint8)

        # Orijinal resim ve işlenmiş resim için etiketler oluştur
        self.label_original = QLabel(self)
        self.label_original.setText("Orijinal Resim")
        self.label_original.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.label_processed = QLabel(self)
        self.label_processed.setText("İşlenmiş Resim")
        self.label_processed.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        # Resim yükleme düğmesi oluştur
        self.button_load = QPushButton('Resim Yükle', self)
        self.button_load.clicked.connect(self.loadImage)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(50, 50, 1180, 20)
        self.slider.setRange(1, 500)  # Minimum ve maksimum değer aralığını belirle
        self.slider.setValue(100)  # Başlangıç değerini belirle
        self.slider.setSingleStep(1)  # Tek adımda kaydırma miktarını belirle
        self.slider.valueChanged.connect(self.on_slider_changed)  # Slider değeri değiştiğinde işlevi bağla

        # Resetleme düğmesini oluştur
        self.button_reset = QPushButton('Resetle', self)
        self.button_reset.setEnabled(False)
        self.button_reset.clicked.connect(self.reset)

        self.button_save_processed = QPushButton('İşlenmiş Resmi Kaydet', self)
        self.button_save_processed.setEnabled(False)
        self.button_save_processed.clicked.connect(self.saveProcessedImage)

        # Orijinal resim ve etiketini bir düzende topla
        layout_original_content = QVBoxLayout()
        layout_original_content.addWidget(self.label_original)

        # Orijinal resim ve etiketi düzene ekle
        layout_original = QHBoxLayout()
        layout_original.addLayout(layout_original_content)

        layout_processed = QVBoxLayout()
        layout_processed.addWidget(self.label_processed)

        layout_images = QHBoxLayout()
        layout_images.addLayout(layout_original)
        layout_images.addLayout(layout_processed)

        layout_buttons = QHBoxLayout()

        # Ana düzeni oluştur
        layout = QVBoxLayout()
        layout.addWidget(self.button_load)
        layout.addWidget(self.slider)
        layout.addLayout(layout_images)
        layout.addLayout(layout_buttons)
        layout.addWidget(self.button_reset)
        layout.addWidget(self.button_save_processed)

        self.setLayout(layout)
        self.show()

    # Resim yükleme işlevi
    def loadImage(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Resim Seç', '', 'JPEG Files (*.jpg;*.jpeg);;PNG Files (*.png)')
        if file_path:
            image = cv2.imread(file_path)
            if image is not None:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.original_image = image.copy()
                self.processed_image = image.copy()
                self.showOriginalImage()
                self.showProcessedImage()
                self.enableButtons()

    def showOriginalImage(self):
        label_width = self.label_original.width()
        label_height = self.label_original.height()
        height, width, channel = self.original_image.shape
        bytes_per_line = 3 * width

        # Orijinal resmi uygun boyuta ölçeklendir
        pixmap = QPixmap.fromImage(QImage(self.original_image.data, width, height, bytes_per_line, QImage.Format_RGB888))
        pixmap = pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Orijinal resmi göster
        self.label_original.setPixmap(pixmap)


    # İşlenmiş resmi gösterme işlevi
    def showProcessedImage(self):
        if self.processed_image is not None:
            scale_factor = self.slider.value() / 100.0

            # Ölçek faktörünü hesapla
            scale = scale_factor
            resize_img = resize_image(self.original_image, scale)
            self.processed_image = resize_img

            # NumPy dizisini uygun bir veri türüne dönüştür
            resize_img = resize_img.astype(np.uint8)

            # QImage oluştur
            q_image = QImage(resize_img.data, resize_img.shape[1], resize_img.shape[0], QImage.Format_RGB888)

            # QLabel'da resmi göster
            label_width = self.label_original.width()
            label_height = self.label_original.height()
            pixmap = QPixmap.fromImage(q_image)
            pixmap = pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label_processed.setPixmap(pixmap)
        else:
            print("İşlenmiş resim bulunamadi.")

 

    # Resetleme işlevi
    def reset(self):
        self.processed_image = None
        self.label_processed.clear()

    # Düğmeleri etkinleştirme işlevi
    def enableButtons(self):
        self.button_reset.setEnabled(True)
        self.button_save_processed.setEnabled(True)

    def disableButtons(self):
        self.button_reset.setEnabled(False)
        self.button_save_processed.setEnabled(False)

    # İşlenmiş resmi kaydetme işlevi
    def saveProcessedImage(self):
        if self.processed_image is not None and self.button_save_processed.isEnabled():
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getSaveFileName(self, 'İşlenmiş Resmi Kaydet', '', 'JPEG Files (*.jpg;*.jpeg);;PNG Files (*.png)')
            if file_path:
                # Dosya uzantısını kontrol et
                if not file_path.endswith(('.jpg', '.jpeg', '.png')):
                    file_path += '.jpg'  # Varsayılan olarak JPEG uzantısı ekleyin
                cv2.imwrite(file_path, cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR))

    # Slider değeri değiştiğinde çağrılan işlev
    def on_slider_changed(self):
        self.showProcessedImage()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageProcessor()
    window.show()
    sys.exit(app.exec_())

