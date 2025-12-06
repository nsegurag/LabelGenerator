import os
from barcode import Code128
from barcode.writer import ImageWriter
# Importamos la función centralizada (No la redefinimos aquí)
from src.utils import resource_path 

# =================================
# CONFIGURACIÓN
# =================================
# Usamos resource_path para que funcione en la carpeta 'data' tanto en DEV como EXE
BARCODE_FOLDER = resource_path(os.path.join("data", "barcodes"))

def generate_barcode_image(text):
    """
    Genera imagen PNG del código de barras en la carpeta data/barcodes.
    Retorna la ruta completa del archivo generado.
    """
    try:
        # 1. Crear carpeta si no existe (Seguridad)
        if not os.path.exists(BARCODE_FOLDER):
            os.makedirs(BARCODE_FOLDER)

        # 2. Definir rutas
        # python-barcode añade la extensión automáticamente, así que en 'file_path' NO ponemos .png
        base_filename = os.path.join(BARCODE_FOLDER, text) 
        
        # 3. Generar y guardar
        # writer_options permite controlar el tamaño si lo necesitas después
        writer_options = {
            'module_width': 0.4, 
            'module_height': 15.0, 
            'quiet_zone': 1.0, 
            'font_size': 10, 
            'text_distance': 5.0, 
            'background': 'white', 
            'foreground': 'black'
        }
        
        code = Code128(text, writer=ImageWriter())
        saved_path = code.save(base_filename, options=writer_options)

        # 4. Verificación final
        if not os.path.exists(saved_path):
            print(f"⚠️ Alerta: La librería dice que guardó, pero el archivo no está: {saved_path}")
            return None

        return saved_path

    except Exception as e:
        print(f"❌ ERROR generando barcode ({text}): {e}")
        return None