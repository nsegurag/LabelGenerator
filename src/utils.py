import sys
import os
import shutil

def resource_path(relative_path):
    """
    Obtiene ruta absoluta para recursos estáticos (imágenes fijas, iconos, DB original)
    que están EMPAQUETADOS dentro del .exe (solo lectura).
    """
    try:
        # PyInstaller crea una carpeta temporal _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # En desarrollo (src/utils.py), subimos un nivel para ir a la raíz del proyecto
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def get_user_data_dir():
    """
    Retorna la ruta segura y escribible en AppData del usuario.
    Aquí es donde guardaremos cosas nuevas (Barcodes, Logs, DB actualizada).
    Ruta: C:/Users/Usuario/AppData/Local/LabelGenerator
    """
    path = os.path.join(os.getenv('LOCALAPPDATA'), 'LabelGenerator')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_db_path(db_filename="labels.db"):
    """
    Gestiona la base de datos.
    1. Verifica si ya existe en AppData (datos del usuario).
    2. Si no existe (primera vez), copia la DB vacía desde el .exe a AppData.
    3. Retorna la ruta de AppData.
    """
    app_data_dir = get_user_data_dir()
    target_path = os.path.join(app_data_dir, db_filename)

    # Si no existe en AppData, copiamos la plantilla original
    if not os.path.exists(target_path):
        source_path = resource_path(os.path.join("data", db_filename))
        try:
            if os.path.exists(source_path):
                shutil.copy2(source_path, target_path)
        except Exception as e:
            print(f"Error copiando DB inicial: {e}")

    return target_path