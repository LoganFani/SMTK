import sqlite3

#TODO CHANGE ALL F STRINGS TO SAFE QUERIES

# Start
def get_db_connection(db_name:str ) -> sqlite3.Connection | None:
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None
    
def create_table (conn:sqlite3.Connection, deck_name:str) -> bool:
    try:
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {deck_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                translation TEXT NOT NULL
            );
        ''')
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        return False



def insert_translation(conn:sqlite3.Connection, deck_name:str, source_text:str, translated_text:str) -> bool:
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO (deck_name, source, translation)
            VALUES (?, ?, ?);
        ''', (deck_name, source_text, translated_text))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error inserting translation: {e}")
        return False
    

def fetch_all_translations(conn:sqlite3.Connection, deck_name:str) -> list[tuple[int, str, str]] | None:
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM (deck_name) VALUE (?);
        ''', (deck_name,))
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Error fetching translations: {e}")
        return None
    
def delete_translation(conn:sqlite3.Connection, deck_name:str, translation_id:int) -> bool:
    try:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM (deck_name) VALUE (?)
            WHERE id = ?;
        ''', (deck_name, translation_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error deleting translation: {e}")
        return False

def edit_translation(conn:sqlite3.Connection, deck_name:str, translation_id:int, new_source:str, new_translation:str) -> bool:
    try:
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE {deck_name}
            SET source = ?, translation = ?
            WHERE id = ?;
        ''', (new_source, new_translation, translation_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error editing translation: {e}")
        return False
    
def list_tables(conn:sqlite3.Connection) -> list[str] | None:
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table';
        ''')
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    except sqlite3.Error as e:
        print(f"Error listing tables: {e}")
        return None