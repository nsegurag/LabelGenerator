import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem
)

from src.utils import get_db_path

class HAWBViewer(QWidget):
    def __init__(self, master_id, mawb_number):
        super().__init__()

        self.master_id = master_id
        self.mawb_number = mawb_number

        self.setWindowTitle(f"HAWBs de la MAWB {mawb_number}")
        self.setGeometry(300, 200, 600, 400)

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Guías hijas asociadas a: {mawb_number}"))

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "ID", "HAWB", "Piezas"
        ])
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_hawbs()

    def load_hawbs(self):
        self.table.setRowCount(0)

        conn = sqlite3.connect("labels.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, hawb_number, pieces
            FROM houses
            WHERE master_id = ?
            ORDER BY id
        """, (self.master_id,))

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
