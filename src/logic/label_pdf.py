import sys
import os
import sqlite3
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Importamos desde src.utils
from src.utils import get_db_path, resource_path

# ------------------ TAMAÑOS DE ETIQUETA ------------------
def get_page_size(size):
    if size == "4x6":
        return (4 * inch, 6 * inch)
    elif size == "4x4":
        return (4 * inch, 4 * inch)
    elif size == "4x2":  
        return (4 * inch, 2 * inch) 
    else:
        return (4 * inch, 6 * inch)

# ------------------ MOTOR DE DIBUJO ADAPTATIVO ------------------
def draw_flexible_label(c, w, h, data):
    """
    Dibuja una etiqueta estilo IATA profesional.
    Se adapta inteligentemente si la etiqueta es muy bajita (ej. 4x2).
    """
    # Detectamos si es una etiqueta "chaparra" (menos de 3 pulgadas de alto)
    is_compact = h < (3 * inch)

    # Márgenes: Si es compacta, usamos menos margen para aprovechar espacio
    margin = 4 if is_compact else 10
    safe_w = w - (2 * margin)
    safe_h = h - (2 * margin)
    
    # --- FUENTE INTELIGENTE ---
    # Si es compacta, la fuente base depende de la altura, no del ancho
    if is_compact:
        font_s = h / 14 
    else:
        font_s = w / 24

    c.setLineWidth(1.0 if is_compact else 1.2)      
    
    # ==================== GRID (PORCENTAJES) ====================
    # En 4x2 necesitamos darle más aire al barcode, reducimos un poco el resto
    if is_compact:
        pct_header = 0.16
        pct_route = 0.22
        pct_details = 0.18
        pct_total = 0.12 # Un poco más alto para que quepa el texto horizontal
    else:
        pct_header = 0.18   
        pct_route = 0.24    
        pct_details = 0.18  
        pct_total = 0.10    
    
    # Coordenadas Y (Calculadas de arriba hacia abajo)
    y_top = h - margin
    
    h_header = safe_h * pct_header
    y_header = y_top - h_header
    
    h_route = safe_h * pct_route
    y_route = y_header - h_route
    
    h_details = safe_h * pct_details
    y_details = y_route - h_details
    
    # Nueva sección Total
    h_total = safe_h * pct_total
    y_total = y_details - h_total
    
    # Barcode ocupa el resto hasta el margen
    h_barcode = y_total - margin 
    y_barcode = margin

    # ==================== 1. HEADER (MAWB) ====================
    c.rect(margin, y_header, safe_w, h_header)
    
    c.setFont("Helvetica", font_s * 0.6)
    c.drawString(margin + 5, y_top - (5 if is_compact else 10), "MAWB No.")
    
    c.setFont("Helvetica-Bold", font_s * (1.5 if is_compact else 1.8))
    # Ajuste fino vertical para centrar mejor
    offset_mawb = h_header * 0.25
    c.drawCentredString(w / 2, y_header + offset_mawb, data['mawb'])

    # ==================== 2. RUTA (50% / 50%) ====================
    c.rect(margin, y_route, safe_w, h_route)
    
    mid_x = w / 2
    c.line(mid_x, y_route, mid_x, y_route + h_route)
    
    offset_lbl = 5 if is_compact else 10
    
    # -- Origen --
    c.setFont("Helvetica", font_s * 0.6)
    c.drawString(margin + 5, y_header - offset_lbl, "Origin / Origen")
    
    c.setFont("Helvetica-Bold", font_s * 2.0) 
    center_left = margin + (safe_w / 4)
    c.drawCentredString(center_left, y_route + (h_route * 0.30), data['origin'])
    
    # -- Destino --
    c.setFont("Helvetica", font_s * 0.6)
    c.drawString(mid_x + 5, y_header - offset_lbl, "Destination / Destino")
    
    c.setFont("Helvetica-Bold", font_s * 2.0) 
    center_right = mid_x + (safe_w / 4)
    c.drawCentredString(center_right, y_route + (h_route * 0.30), data['dest'])

    # ==================== 3. DETALLES (HAWB + CONTEO) ====================
    c.rect(margin, y_details, safe_w, h_details)
    
    if data['hawb']:
        # División: 60% HAWB | 40% Conteo
        split_x = margin + (safe_w * 0.6)
        c.line(split_x, y_details, split_x, y_details + h_details)
        
        # HAWB
        c.setFont("Helvetica", font_s * 0.6)
        c.drawString(margin + 5, y_route - offset_lbl, "HAWB No.")
        c.setFont("Helvetica-Bold", font_s * 1.1)
        c.drawCentredString(margin + (safe_w * 0.3), y_details + (h_details * 0.30), data['hawb'])
        
        # Piezas
        c.setFont("Helvetica", font_s * 0.6)
        c.drawString(split_x + 5, y_route - offset_lbl, "Piece No.")
        c.setFont("Helvetica-Bold", font_s * 1.1)
        c.drawCentredString(split_x + (safe_w * 0.2), y_details + (h_details * 0.30), data['counter_str'])
        
    else:
        c.setFont("Helvetica", font_s * 0.6)
        c.drawString(margin + 5, y_route - offset_lbl, "Piece Number")
        c.setFont("Helvetica-Bold", font_s * 1.4)
        c.drawCentredString(w / 2, y_details + (h_details * 0.30), data['counter_str'])

    # ==================== 3.5 TOTAL SHIPMENT (LÓGICA HÍBRIDA) ====================
    c.rect(margin, y_total, safe_w, h_total)
    
    if is_compact:
        # --- ESTILO 4x2: Horizontal (Todo en una línea) ---
        c.setFont("Helvetica-Bold", font_s * 0.9)
        # Dibujamos centrado verticalmente en esa franja
        texto_completo = f"TOTAL SHIPMENT: {data['total_pcs']} PCS"
        c.drawCentredString(w / 2, y_total + (h_total * 0.3), texto_completo)
    else:
        # --- ESTILO 4x6 / 4x4: Vertical (Titulo arriba, valor abajo) ---
        c.setFont("Helvetica", font_s * 0.5)
        c.drawString(margin + 4, y_details - 8, "Total Shipment Pieces / Total Piezas Embarque")
        
        c.setFont("Helvetica-Bold", font_s * 1.3) 
        c.drawCentredString(w / 2, y_total + 5, f"{data['total_pcs']} PCS")

    # ==================== 4. BARCODE ====================
    barcode_filename = f"{data['barcode_text']}.png"
    barcode_path = resource_path(os.path.join("data", "barcodes", barcode_filename))
    
    if os.path.exists(barcode_path):
        try:
            img = ImageReader(barcode_path)
            iw, ih = img.getSize()
            aspect = ih / float(iw)
            
            draw_w = safe_w * 0.90
            draw_h = draw_w * aspect
            
            # Ajustar altura si excede el área disponible
            max_h = h_barcode * 0.90 # Usamos 90% del espacio disponible
            if draw_h > max_h:
                draw_h = max_h
                draw_w = draw_h / aspect
            
            x_img = (w - draw_w) / 2
            # Centrado mejorado
            y_img = margin + (h_barcode - draw_h) / 2 
            
            c.drawImage(img, x_img, y_img, width=draw_w, height=draw_h, mask='auto')
            
            # Texto del código (solo si no es compacta o si sobra espacio)
            if not is_compact:
                c.setFont("Helvetica", font_s * 0.5)
                c.drawCentredString(w/2, margin - 2, data['barcode_text'])
            
        except Exception as e:
            print(f"Error dibujando barcode: {e}")

# ------------------ FUNCIÓN PRINCIPAL ------------------
def generate_labels_pdf(master_id, file_path, size="4x6"):

    w, h = get_page_size(size)

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute("SELECT mawb_number, origin, destination, total_pieces FROM masters WHERE id=?", (master_id,))
    master = cursor.fetchone()
    if not master:
        conn.close()
        return
    mawb, org, dest, total_pcs = master

    cursor.execute("""
        SELECT l.mawb_counter, l.hawb_counter, l.barcode_data, h.hawb_number
        FROM labels l
        LEFT JOIN houses h ON l.house_id = h.id
        WHERE l.master_id = ?
    """, (master_id,))
    
    labels = cursor.fetchall()
    conn.close()

    if not labels:
        return

    c = canvas.Canvas(file_path, pagesize=(w, h))

    for lbl in labels:
        m_cnt, h_cnt, b_code, h_num = lbl
        
        if h_num:
            counter_display = h_cnt.replace("/", " of ")
        else:
            counter_display = m_cnt.replace("/", " of ")

        data = {
            "mawb": mawb,
            "origin": org,
            "dest": dest,
            "total_pcs": total_pcs,
            "counter_str": counter_display,
            "barcode_text": b_code,
            "hawb": h_num if h_num else ""
        }

        draw_flexible_label(c, w, h, data)
        c.showPage()

    c.save()
    print(f"✅ PDF Generado: {file_path}")