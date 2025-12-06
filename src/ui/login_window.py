import sys
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, 
    QVBoxLayout, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QCursor

# IMPORTACIONES ACTUALIZADAS PARA LA NUEVA ESTRUCTURA
from src.utils import get_db_path
from src.ui.main_window import MainWindow

DB_PATH = get_db_path()

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenido")
        # Un poco más alto para que quepa la sombra sin cortarse
        self.setFixedSize(420, 480) 
        
        # SOLUCIÓN AL FONDO BLANCO Y BOTÓN AZUL:
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # SOLUCIÓN A LA CAJA RECORTADA:
        layout.setContentsMargins(50, 60, 50, 60)
        
        # Tarjeta de Login
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedSize(320, 360) 
        
        # Sombra profesional
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 50)) 
        card.setGraphicsEffect(shadow)

        # Estilo local de la tarjeta (Solo lo específico de la tarjeta)
        card.setStyleSheet("""
            QFrame#Card {
                background-color: white;
                border: 1px solid #F0F0F0;
                border-radius: 12px;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(30, 40, 30, 40)

        # Header
        lbl_icon = QLabel("📦")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 40px; background: transparent; border: none;")
        card_layout.addWidget(lbl_icon)

        lbl_title = QLabel("Iniciar Sesión")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #222; background: transparent; border: none;")
        card_layout.addWidget(lbl_title)

        # Inputs
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setMinimumHeight(35)
        self.user_input.setClearButtonEnabled(True)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setMinimumHeight(35)
        self.pass_input.setClearButtonEnabled(True)

        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.pass_input)
        
        card_layout.addSpacing(10)

        # Botón
        self.login_btn = QPushButton("Ingresar")
        self.login_btn.setObjectName("Primary")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setMinimumHeight(40)
        self.login_btn.setDefault(True) # Reacciona al Enter
        self.login_btn.clicked.connect(self.login)
        card_layout.addWidget(self.login_btn)

        card_layout.addStretch()
        layout.addWidget(card)
        self.setLayout(layout)

        # Lógica de teclado profesional
        QWidget.setTabOrder(self.user_input, self.pass_input)
        QWidget.setTabOrder(self.pass_input, self.login_btn)
        self.user_input.returnPressed.connect(self.pass_input.setFocus)
        self.pass_input.returnPressed.connect(self.login)
        
        self.user_input.setFocus()

    def login(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not username:
            self.user_input.setFocus()
            return
        
        if not password:
            self.pass_input.setFocus()
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error de conexión:\n{e}")
            return

        if user:
            self.main = MainWindow(username)
            self.main.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
            self.pass_input.clear()
            self.pass_input.setFocus()