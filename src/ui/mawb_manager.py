import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QMessageBox, QHBoxLayout, QFileDialog, 
    QComboBox, QLineEdit, QListWidget, QDialog, QSpinBox, 
    QAbstractItemView, QAbstractSpinBox, QFrame, QFormLayout, 
    QSplitter, QHeaderView, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont

from src.utils import get_db_path
from src.logic.label_pdf import generate_labels_pdf
from src.logic.barcode_utils import generate_barcode_image
from src.logic.logger import log_action
from src.ui.logs_viewer import LogsViewer

DB_PATH = get_db_path()

# ===================== ESTILOS LOCALES (TARJETAS) =====================
CARD_STYLE = """
    QFrame#Card {
        background-color: white;
        border: 1px solid #E5E5E5;
        border-radius: 10px;
    }
    QLabel {
        background-color: transparent;
        color: #333;
    }
    QListWidget {
        border: 1px solid #F0F0F0;
        border-radius: 6px;
        background-color: #FAFAFA;
        padding: 5px;
    }
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #EEE;
    }
    QListWidget::item:selected {
        background-color: #E3F2FD;
        color: #0067C0;
        border-radius: 4px;
    }
"""

# ===================== DIALOGOS AUXILIARES =====================
class SimpleHAWBDialog(QDialog):
    def __init__(self, title, hawb_val="", pieces_val=0, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(350, 220)
        
        self.setStyleSheet("""
            QDialog { background-color: white; } 
            QLabel { background: transparent; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        header = QLabel(title)
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #0067C0;")
        layout.addWidget(header)

        form = QFormLayout()
        self.hawb_input = QLineEdit(hawb_val)
        self.hawb_input.setPlaceholderText("Ej: HAWB123")
        self.hawb_input.setMinimumHeight(35)
        
        self.pieces_input = QSpinBox()
        self.pieces_input.setMaximum(9999)
        self.pieces_input.setValue(pieces_val)
        self.pieces_input.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.pieces_input.setMinimumHeight(35)
        self.pieces_input.setSuffix(" pcs")

        form.addRow("Número:", self.hawb_input)
        form.addRow("Piezas:", self.pieces_input)
        layout.addLayout(form)

        btns = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancelar")
        self.add_btn = QPushButton("Guardar")
        self.add_btn.setObjectName("Primary") 

        self.add_btn.clicked.connect(self.accept_data)
        self.cancel_btn.clicked.connect(self.reject)

        btns.addStretch()
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.add_btn)
        layout.addLayout(btns)
        self.setLayout(layout)
        
        self.hawb = ""
        self.pieces = 0

    def accept_data(self):
        self.hawb = self.hawb_input.text().strip()
        self.pieces = self.pieces_input.value()
        if not self.hawb or self.pieces <= 0:
            return
        self.accept()

class EditMAWBDialog(QDialog):
    def __init__(self, master_id, username="admin"):
        super().__init__()
        self.master_id = master_id
        self.username = username
        self.setWindowTitle("Editar MAWB")
        self.setFixedSize(400, 350)
        
        self.setStyleSheet("""
            QDialog { background-color: white; } 
            QLabel { background: transparent; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        lbl = QLabel("Editar Guía Master")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(lbl)

        # Datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT origin, destination, service, total_pieces, mawb_number FROM masters WHERE id = ?", (master_id,))
        data = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM houses WHERE master_id = ?", (master_id,))
        self.has_hawbs = cursor.fetchone()[0] > 0
        conn.close()

        if not data:
            self.reject()
            return

        self.old_origin, self.old_dest, self.old_srv, self.old_total, self.mawb_num = data

        form = QFormLayout()
        form.setSpacing(10)

        self.origin_input = QLineEdit(self.old_origin)
        self.dest_input = QLineEdit(self.old_dest)
        
        self.service_combo = QComboBox()
        self.service_combo.addItems(["ACA", "ACP", "ACX", "BSA"])
        self.service_combo.setCurrentText(self.old_srv)
        self.service_combo.setMinimumHeight(30)
        
        self.total_spin = QSpinBox()
        self.total_spin.setMaximum(9999)
        self.total_spin.setValue(self.old_total)
        self.total_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.total_spin.setMinimumHeight(30)

        if self.has_hawbs:
            self.total_spin.setDisabled(True)
            self.total_spin.setToolTip("Calculado automáticamente por las HAWBs")

        form.addRow("Origen:", self.origin_input)
        form.addRow("Destino:", self.dest_input)
        form.addRow("Servicio:", self.service_combo)
        form.addRow("Total:", self.total_spin)
        
        layout.addLayout(form)
        layout.addStretch()

        btns = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_save = QPushButton("Guardar Cambios")
        btn_save.setObjectName("Primary")
        
        btn_save.clicked.connect(self.save_changes)
        btn_cancel.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)
        layout.addLayout(btns)
        self.setLayout(layout)

    def save_changes(self):
        new_org = self.origin_input.text().strip().upper()
        new_dest = self.dest_input.text().strip().upper()
        new_srv = self.service_combo.currentText()
        new_tot = self.total_spin.value()

        if not new_org or not new_dest or new_tot == 0:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE masters SET origin=?, destination=?, service=?, total_pieces=? WHERE id=?
        """, (new_org, new_dest, new_srv, new_tot, self.master_id))
        
        cursor.execute("DELETE FROM labels WHERE master_id=?", (self.master_id,))
        
        cursor.execute("SELECT id, hawb_number, pieces FROM houses WHERE master_id=?", (self.master_id,))
        houses = cursor.fetchall()
        
        if not houses:
            for i in range(1, new_tot + 1):
                code = f"{self.mawb_num}-{str(i).zfill(3)}"
                generate_barcode_image(code)
                cursor.execute("INSERT INTO labels (master_id, mawb_counter, barcode_data) VALUES (?,?,?)", 
                               (self.master_id, f"{i}/{new_tot}", code))
        else:
            m_counter = 1
            for hid, hnum, hpcs in houses:
                for i in range(1, hpcs + 1):
                    code = f"{self.mawb_num}-{hnum}-{str(i).zfill(3)}"
                    generate_barcode_image(code)
                    cursor.execute("INSERT INTO labels (master_id, house_id, mawb_counter, hawb_counter, barcode_data) VALUES (?,?,?,?,?)",
                                   (self.master_id, hid, f"{m_counter}/{new_tot}", f"{i}/{hpcs}", code))
                    m_counter += 1

        conn.commit()
        conn.close()
        log_action(self.username, "EDIT MAWB", self.mawb_num, "Datos actualizados y etiquetas regeneradas")
        self.accept()

# ===================== GESTOR DE MAWBs (MODERNO) =====================
class MAWBManager(QWidget):
    def __init__(self, username="admin"):
        super().__init__()
        self.username = username
        self.setWindowTitle("Gestor de Inventario")
        self.resize(1100, 750)
        
        self.setStyleSheet(CARD_STYLE + """
            QSplitter::handle {
                background-color: #E0E0E0;
            }
            QTableWidget {
                border: none;
                background-color: transparent;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- BARRA SUPERIOR ---
        header_layout = QHBoxLayout()
        
        title_lbl = QLabel("📦 Inventario de Guías")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #222;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por Número, Origen o Destino...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border-radius: 20px; 
                padding-left: 15px; 
                border: 1px solid #CCC;
                background: white;
            }
            QLineEdit:focus { border: 2px solid #0067C0; }
        """)
        self.search_input.textChanged.connect(self.load_data)

        self.btn_logs = QPushButton("📒 Bitácora")
        self.btn_logs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logs.setMinimumHeight(40)
        self.btn_logs.setStyleSheet("padding: 0 20px; font-weight: bold;")
        self.btn_logs.clicked.connect(self.open_logs)

        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.btn_logs)
        
        main_layout.addLayout(header_layout)

        # --- ÁREA DE CONTENIDO ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # 1. PANEL IZQUIERDO: TABLA MAESTRA
        left_frame = QFrame()
        left_frame.setObjectName("Card")
        shadow_l = QGraphicsDropShadowEffect(self)
        shadow_l.setBlurRadius(15); shadow_l.setColor(QColor(0,0,0,30)); shadow_l.setYOffset(2)
        left_frame.setGraphicsEffect(shadow_l)

        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "MAWB", "Ruta", "Servicio", "Total", "Tamaño"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #E9ECEF;
                font-weight: bold;
                color: #555;
            }
        """)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        
        left_layout.addWidget(self.table)
        
        # 2. PANEL DERECHO: DETALLES
        self.right_frame = QFrame()
        self.right_frame.setObjectName("Card")
        self.right_frame.setFixedWidth(400) 
        shadow_r = QGraphicsDropShadowEffect(self)
        shadow_r.setBlurRadius(15); shadow_r.setColor(QColor(0,0,0,30)); shadow_r.setYOffset(2)
        self.right_frame.setGraphicsEffect(shadow_r)

        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setContentsMargins(20, 25, 20, 25)
        self.right_layout.setSpacing(15)

        self.lbl_selected = QLabel("👈 Selecciona una Guía")
        self.lbl_selected.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_selected.setStyleSheet("color: #999; font-size: 16px; font-weight: bold;")
        self.right_layout.addWidget(self.lbl_selected)
        self.right_layout.addStretch()

        splitter.addWidget(left_frame)
        splitter.addWidget(self.right_frame)
        splitter.setStretchFactor(0, 3) 
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.table.itemSelectionChanged.connect(self.on_row_selected)
        self.load_data()

    # ===================== LÓGICA DE DATOS =====================
    def load_data(self):
        self.table.setRowCount(0)
        search = self.search_input.text().strip()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = "SELECT id, mawb_number, origin, destination, service, total_pieces, label_size FROM masters"
        params = []
        if search:
            query += " WHERE mawb_number LIKE ? OR origin LIKE ? OR destination LIKE ?"
            like_txt = f"%{search}%"
            params = [like_txt, like_txt, like_txt]
        
        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        for r_idx, row in enumerate(rows):
            self.table.insertRow(r_idx)
            self.table.setItem(r_idx, 0, QTableWidgetItem(str(row[0])))
            mawb_item = QTableWidgetItem(row[1])
            mawb_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            self.table.setItem(r_idx, 1, mawb_item)
            self.table.setItem(r_idx, 2, QTableWidgetItem(f"{row[2]} ➝ {row[3]}"))
            self.table.setItem(r_idx, 3, QTableWidgetItem(row[4]))
            self.table.setItem(r_idx, 4, QTableWidgetItem(f"{row[5]} pcs"))
            size_val = row[6] if row[6] else "4x6"
            self.table.setItem(r_idx, 5, QTableWidgetItem(size_val))

    def on_row_selected(self):
        row = self.table.currentRow()
        if row == -1: return

        self.clear_right_panel()

        master_id = int(self.table.item(row, 0).text())
        mawb_num = self.table.item(row, 1).text()
        current_size = self.table.item(row, 5).text()

        # --- PANEL DETALLES ---
        title = QLabel(mawb_num)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0067C0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_layout.addWidget(title)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Tamaño Etiqueta:"))
        self.combo_size = QComboBox()
        self.combo_size.addItems(["4x6", "4x4", "4x2"])
        self.combo_size.setCurrentText(current_size)
        self.combo_size.currentIndexChanged.connect(lambda: self.update_size(master_id, mawb_num))
        size_layout.addWidget(self.combo_size)
        self.right_layout.addLayout(size_layout)

        self.right_layout.addSpacing(10)

        lbl_hawbs = QLabel("📋 Desglose HAWBs:")
        lbl_hawbs.setStyleSheet("font-weight: bold; color: #555;")
        self.right_layout.addWidget(lbl_hawbs)

        self.list_hawbs = QListWidget()
        self.populate_hawbs_list(master_id)
        self.right_layout.addWidget(self.list_hawbs)

        h_btns = QHBoxLayout()
        btn_add_h = QPushButton("➕ Agregar")
        btn_add_h.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_h.clicked.connect(lambda: self.add_hawb(master_id, mawb_num))
        
        btn_edit_h = QPushButton("✏️ Editar")
        btn_edit_h.clicked.connect(lambda: self.edit_hawb(master_id, mawb_num))
        
        btn_del_h = QPushButton("🗑️")
        btn_del_h.setFixedWidth(40)
        btn_del_h.setObjectName("Danger")
        btn_del_h.clicked.connect(lambda: self.delete_hawb(master_id, mawb_num))

        h_btns.addWidget(btn_add_h)
        h_btns.addWidget(btn_edit_h)
        h_btns.addWidget(btn_del_h)
        self.right_layout.addLayout(h_btns)

        self.right_layout.addSpacing(15)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #EEE;")
        self.right_layout.addWidget(line)
        self.right_layout.addSpacing(15)

        btn_pdf = QPushButton("📄  Generar PDF")
        btn_pdf.setMinimumHeight(45)
        btn_pdf.setObjectName("Primary")
        btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pdf.setStyleSheet("font-size: 14px;")
        btn_pdf.clicked.connect(lambda: self.generate_pdf_action(master_id, mawb_num))
        self.right_layout.addWidget(btn_pdf)

        m_btns = QHBoxLayout()
        btn_edit_m = QPushButton("Editar Master")
        btn_edit_m.clicked.connect(lambda: self.edit_mawb_action(master_id))
        
        btn_del_m = QPushButton("Eliminar Todo")
        btn_del_m.setObjectName("Danger")
        btn_del_m.clicked.connect(lambda: self.delete_mawb_action(master_id, mawb_num))

        m_btns.addWidget(btn_edit_m)
        m_btns.addWidget(btn_del_m)
        self.right_layout.addLayout(m_btns)

    def clear_right_panel(self):
        while self.right_layout.count():
            child = self.right_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                for i in range(child.layout().count()):
                    w = child.layout().itemAt(i).widget()
                    if w: w.deleteLater()

    def populate_hawbs_list(self, master_id):
        self.list_hawbs.clear()
        self.current_hawbs_data = [] 
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, hawb_number, pieces FROM houses WHERE master_id=?", (master_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.list_hawbs.addItem("ℹ️ Sin HAWBs (Consolidado puro)")
            self.list_hawbs.item(0).setForeground(QColor("#888"))
        else:
            for hid, num, pcs in rows:
                self.list_hawbs.addItem(f"📄 {num}  —  {pcs} pcs")
                self.current_hawbs_data.append((hid, num, pcs))

    # ===================== ACCIONES =====================
    def update_size(self, master_id, mawb_num):
        new_size = self.combo_size.currentText()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE masters SET label_size=? WHERE id=?", (new_size, master_id))
        conn.commit()
        conn.close()
        
        row = self.table.currentRow()
        self.table.setItem(row, 5, QTableWidgetItem(new_size))
        log_action(self.username, "CHANGE SIZE", mawb_num, f"To {new_size}")

    def generate_pdf_action(self, master_id, mawb_num):
        size = self.combo_size.currentText()
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", f"{mawb_num}.pdf", "PDF Files (*.pdf)")
        
        if file_path:
            try:
                generate_labels_pdf(master_id, file_path, size)
                QMessageBox.information(self, "Listo", "PDF generado exitosamente.")
                log_action(self.username, "GENERATE PDF", mawb_num, f"Size: {size}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def add_hawb(self, master_id, mawb_num):
        dialog = SimpleHAWBDialog("Agregar HAWB", parent=self)
        if dialog.exec():
            new_hawb = dialog.hawb.strip().upper()
            
            # VALIDACIÓN DUPLICADOS (HAWB)
            for _, existing_h, _ in self.current_hawbs_data:
                if existing_h.strip().upper() == new_hawb:
                    QMessageBox.warning(self, "Duplicado", f"La HAWB '{new_hawb}' ya existe en esta guía Master.")
                    return 

            try:
                current_row = self.table.currentRow()

                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO houses (master_id, hawb_number, pieces) VALUES (?,?,?)", 
                               (master_id, dialog.hawb, dialog.pieces))
                
                cursor.execute("SELECT SUM(pieces) FROM houses WHERE master_id=?", (master_id,))
                new_total = cursor.fetchone()[0]
                cursor.execute("UPDATE masters SET total_pieces=? WHERE id=?", (new_total, master_id))
                
                self.regenerate_labels_db(cursor, master_id, mawb_num, new_total)
                
                conn.commit()
                conn.close()
                
                self.load_data() 
                self.table.selectRow(current_row)
                self.on_row_selected() 
                
                log_action(self.username, "ADD HAWB", mawb_num, f"{dialog.hawb} ({dialog.pieces})")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def edit_hawb(self, master_id, mawb_num):
        if not self.current_hawbs_data: return
        row = self.list_hawbs.currentRow()
        if row == -1: 
            QMessageBox.warning(self, "Aviso", "Selecciona una HAWB de la lista.")
            return

        hid, hnum, hpcs = self.current_hawbs_data[row]
        dialog = SimpleHAWBDialog("Editar HAWB", hnum, hpcs, self)
        
        if dialog.exec():
            try:
                current_row = self.table.currentRow() 

                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE houses SET hawb_number=?, pieces=? WHERE id=?", (dialog.hawb, dialog.pieces, hid))
                
                cursor.execute("SELECT SUM(pieces) FROM houses WHERE master_id=?", (master_id,))
                new_total = cursor.fetchone()[0]
                cursor.execute("UPDATE masters SET total_pieces=? WHERE id=?", (new_total, master_id))
                
                self.regenerate_labels_db(cursor, master_id, mawb_num, new_total)
                
                conn.commit()
                conn.close()
                
                self.load_data()
                self.table.selectRow(current_row)
                self.on_row_selected() 
                
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_hawb(self, master_id, mawb_num):
        if not self.current_hawbs_data: return
        row = self.list_hawbs.currentRow()
        if row == -1: 
            QMessageBox.warning(self, "Aviso", "Selecciona una HAWB de la lista.")
            return

        hid, hnum, hpcs = self.current_hawbs_data[row]
        confirm = QMessageBox.question(self, "Eliminar", f"¿Borrar HAWB {hnum}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            current_row = self.table.currentRow() 

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM houses WHERE id=?", (hid,))
            
            cursor.execute("SELECT SUM(pieces) FROM houses WHERE master_id=?", (master_id,))
            res = cursor.fetchone()[0]
            new_total = res if res else 0
            
            cursor.execute("UPDATE masters SET total_pieces=? WHERE id=?", (new_total, master_id))
            self.regenerate_labels_db(cursor, master_id, mawb_num, new_total)
            
            conn.commit()
            conn.close()
            
            self.load_data()
            self.table.selectRow(current_row) 
            self.on_row_selected() 

    def regenerate_labels_db(self, cursor, master_id, mawb_num, total_pieces):
        cursor.execute("DELETE FROM labels WHERE master_id=?", (master_id,))
        
        if total_pieces == 0: return

        cursor.execute("SELECT id, hawb_number, pieces FROM houses WHERE master_id=?", (master_id,))
        houses = cursor.fetchall()
        
        if not houses:
            for i in range(1, total_pieces + 1):
                code = f"{mawb_num}-{str(i).zfill(3)}"
                generate_barcode_image(code)
                cursor.execute("INSERT INTO labels (master_id, mawb_counter, barcode_data) VALUES (?,?,?)", 
                               (master_id, f"{i}/{total_pieces}", code))
        else:
            m_counter = 1
            for hid, hnum, hpcs in houses:
                for i in range(1, hpcs + 1):
                    code = f"{mawb_num}-{hnum}-{str(i).zfill(3)}"
                    generate_barcode_image(code)
                    cursor.execute("INSERT INTO labels (master_id, house_id, mawb_counter, hawb_counter, barcode_data) VALUES (?,?,?,?,?)",
                                   (master_id, hid, f"{m_counter}/{total_pieces}", f"{i}/{hpcs}", code))
                    m_counter += 1

    def edit_mawb_action(self, master_id):
        dialog = EditMAWBDialog(master_id, self.username)
        if dialog.exec():
            curr = self.table.currentRow()
            self.load_data()
            self.table.selectRow(curr)
            self.on_row_selected()

    def delete_mawb_action(self, master_id, mawb_num):
        confirm = QMessageBox.question(self, "Eliminar Todo", 
                                       f"¿Estás seguro de eliminar la MAWB {mawb_num}?\nSe borrarán todas sus HAWBs y etiquetas.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM labels WHERE master_id=?", (master_id,))
            cursor.execute("DELETE FROM houses WHERE master_id=?", (master_id,))
            cursor.execute("DELETE FROM masters WHERE id=?", (master_id,))
            conn.commit()
            conn.close()
            
            log_action(self.username, "DELETE MAWB", mawb_num, "Full deletion")
            self.load_data()
            
            # [CORRECCIÓN CRASH] Limpiamos y creamos un nuevo label seguro
            self.clear_right_panel()
            lbl_deleted = QLabel("Guía Eliminada 🗑️")
            lbl_deleted.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_deleted.setStyleSheet("color: #D32F2F; font-size: 18px; font-weight: bold;")
            
            self.right_layout.addWidget(lbl_deleted)
            self.right_layout.addStretch()

    def open_logs(self):
        self.logs = LogsViewer()
        self.logs.show()