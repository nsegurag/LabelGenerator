# src/utils.py
import sys
import os
import shutil

def resource_path(relative_path):
    """Obtiene ruta absoluta para recursos (funciona en dev y PyInstaller)"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        # Al estar dentro de src/, subimos un nivel para ir a la raíz del proyecto
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def get_db_path(db_filename="labels.db"):
    # Ruta en AppData (Producción)
    app_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'LabelGenerator')
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
    
    target_path = os.path.join(app_data_dir, db_filename)

    # Si no existe en AppData, buscar en la carpeta 'data' del proyecto
    if not os.path.exists(target_path):
        # Buscamos en data/labels.db
        source_path = resource_path(os.path.join("data", db_filename))
        try:
            if os.path.exists(source_path):
                shutil.copy2(source_path, target_path)
        except Exception as e:
            print(f"Error copiando DB: {e}")

    return target_path