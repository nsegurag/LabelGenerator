import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

# Importamos la ventana de Login desde la nueva ubicación
from src.ui.login_window import LoginWindow

# ===============================
#   ESTILO WINDOWS 11 FLUENT (CSS)
# ===============================
FLUENT_STYLE = """
/* --- FONDO Y GENERAL --- */
QWidget {
    background-color: #F3F3F3; /* Gris Mica suave (Global) */
    color: #1A1A1A;
    font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-size: 14px;
}

/* --- TARJETAS Y CONTENEDORES --- */
QFrame#Card, QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    border-radius: 8px; /* Bordes redondeados Win11 */
}

QGroupBox {
    margin-top: 22px;
    font-weight: 600;
    color: #1A1A1A;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #5C5C5C;
}

/* --- INPUTS MODERNOS --- */
QLineEdit, QSpinBox, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D1;
    border-bottom: 1px solid #8A8A8A; /* Borde inferior más oscuro */
    border-radius: 4px;
    padding: 6px 10px;
    selection-background-color: #0067C0;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-bottom: 2px solid #0067C0; /* Acento Azul al enfocar */
    background-color: #FDFDFD;
}

QLineEdit:hover, QSpinBox:hover, QComboBox:hover {
    background-color: #FBFBFB;
}

/* --- BOTONES ESTÁNDAR --- */
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D1;
    border-bottom: 1px solid #B0B0B0; /* Sutil efecto 3D plano */
    border-radius: 4px;
    padding: 6px 15px;
    color: #1A1A1A;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #FBFBFB;
    border-color: #D1D1D1;
}
QPushButton:pressed {
    background-color: #F0F0F0;
    color: #5C5C5C;
    margin-top: 1px; /* Efecto click */
}

/* --- BOTÓN PRIMARIO (AZUL WIN11) --- */
QPushButton#Primary {
    background-color: #0067C0;
    color: white;
    border: 1px solid #0067C0;
    border-bottom: 1px solid #005FB0;
    font-weight: 600;
}
QPushButton#Primary:hover {
    background-color: #1975C5; /* Azul más claro */
    border-color: #1975C5;
}
QPushButton#Primary:pressed {
    background-color: #005FB0;
    border-color: #005FB0;
    color: #D0E6F5;
}

/* --- BOTÓN PELIGRO (ROJO WIN11) --- */
QPushButton#Danger {
    background-color: #C42B1C;
    color: white;
    border: 1px solid #C42B1C;
    font-weight: 600;
}
QPushButton#Danger:hover {
    background-color: #D13F31;
}
QPushButton#Danger:pressed {
    background-color: #B02417;
}

/* --- TABLAS --- */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    gridline-color: #F0F0F0;
    selection-background-color: #E0EEF9; /* Selección azul muy suave */
    selection-color: #1A1A1A;
    outline: none;
}
QHeaderView::section {
    background-color: #FFFFFF;
    border: none;
    border-bottom: 1px solid #E5E5E5;
    padding: 6px;
    font-weight: 600;
    color: #5C5C5C;
}

/* --- SCROLLBARS FINOS --- */
QScrollBar:vertical {
    border: none;
    background: #F3F3F3;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #CDCDCD;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #A6A6A6;
}
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # APLICAR EL TEMA GLOBAL
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(FLUENT_STYLE)
    
    # Iniciar con la ventana de Login
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())