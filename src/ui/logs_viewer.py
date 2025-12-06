import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QLabel
)
from PyQt6.QtCore import Qt

# ✅ Importación correcta desde la nueva estructura
from src.utils import get_db_path

class LogsViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("📒 Bitácora del sistema")
        self.setGeometry(300, 150, 900, 500)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("📒 Bitácora de acciones realizadas:"))

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Usuario",
            "Acción",
            "MAWB",
            "Detalles",
            "Fecha"
        ])

        # Configuración visual para que se vea bien y no sea editable
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_logs()

    def load_logs(self):
        self.table.setRowCount(0)

        # Usar ruta segura
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                id, 
                user, 
                action, 
                mawb_number, 
                details, 
                created_at
            FROM logs
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        for row_index, row_data in enumerate(rows):
            self.table.insertRow(row_index)

            for col_index, value in enumerate(row_data):
                self.table.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(value))
                )