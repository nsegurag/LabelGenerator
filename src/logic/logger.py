import sqlite3
import datetime
from src.utils import get_db_path

def log_action(user, action, mawb_number, details=""):
    """
    Guarda un evento en la bitácora (tabla logs) de forma robusta y segura.
    No permite que un error de log tumbe la aplicación.
    """
    try:
        # 1. Obtenemos la ruta segura (AppData)
        db_path = get_db_path()

        # 2. Usamos 'with' para garantizar que la conexión se cierre sola
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO logs (user, action, mawb_number, details)
                VALUES (?, ?, ?, ?)
            """, (user, action, mawb_number, details))
            
            conn.commit()

        # 3. Feedback en consola (Amigable para el desarrollador)
        # Esto te ayuda a ver qué pasa sin abrir la base de datos
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"📝 [{timestamp}] LOG: {user} -> {action} ({mawb_number}) | {details}")

    except Exception as e:
        # Si falla el log, solo lo imprimimos en consola, NO cerramos el programa
        print(f"❌ ERROR CRÍTICO EN LOGGER: {e}")