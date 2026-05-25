from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QMessageBox
import components.data_manager as dm

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        # Sedikit diperbesar tingginya (dari 150 ke 220) untuk memberi ruang fitur baru
        self.setFixedSize(300, 220) 
        self.setStyleSheet("""
            QDialog { background-color: #282a36; color: #fff; }
            QLabel { color: #fff; font-size: 12px; }
            QComboBox { background-color: #363b3f; color: #fff; border: 1px solid #555; padding: 5px; border-radius: 3px; }
            QPushButton { background-color: #55aaff; color: #fff; border: none; padding: 6px 15px; border-radius: 3px; }
            QPushButton:hover { background-color: #77bbff; }
            QPushButton#dangerBtn { background-color: #ff5555; }
            QPushButton#dangerBtn:hover { background-color: #ff6e6e; }
            QPushButton#secondaryBtn { background-color: #363b3f; }
            QPushButton#secondaryBtn:hover { background-color: #4f565c; }
        """)

        layout = QVBoxLayout()
        
        # --- Bagian Search Engine ---
        self.label = QLabel("Default Search Engine:")
        layout.addWidget(self.label)
        
        self.combo = QComboBox()
        self.combo.addItems(["DuckDuckGo", "Google", "Bing", "Yahoo"])
        
        # Load current settings
        settings = dm.get_settings()
        current_engine = settings.get("search_engine", "DuckDuckGo")
        index = self.combo.findText(current_engine)
        if index >= 0:
            self.combo.setCurrentIndex(index)
            
        layout.addWidget(self.combo)
        
        # Spacer antar section
        layout.addSpacing(15)
        
        # --- Bagian Privasi / Hapusan History ---
        self.privacy_label = QLabel("Privacy:")
        layout.addWidget(self.privacy_label)
        
        self.btn_clear_history = QPushButton("Clear Browsing History")
        self.btn_clear_history.setObjectName("dangerBtn") # Memakai style merah
        self.btn_clear_history.clicked.connect(self.clear_history)
        layout.addWidget(self.btn_clear_history)
        
        layout.addSpacing(15)
        
        # --- Bagian Tombol Aksi (Save / Cancel) ---
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")
        
        self.btn_save.setObjectName("secondaryBtn") # Memakai style abu-abu sesuai script awalmu
        
        self.btn_save.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def save(self):
        settings = dm.get_settings()
        settings["search_engine"] = self.combo.currentText()
        dm.save_settings(settings)
        self.accept()

    def clear_history(self):
        # Membuat pop-up konfirmasi agar user tidak sengaja menghapus
        reply = QMessageBox.question(
            self, 
            "Clear History", 
            "Are you sure you want to clear all browsing history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Memanggil fungsi hapus history dari data_manager
                dm.clear_history() 
                QMessageBox.information(self, "Success", "Browsing history cleared successfully.")
            except AttributeError:
                # Antisipasi jika fungsi clear_history() belum kamu buat di data_manager.py
                QMessageBox.critical(
                    self, 
                    "Error", 
                    "Fungsi dm.clear_history() belum diimplementasikan di data_manager.py!"
                )