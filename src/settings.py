
'''Terrible way to do this change later (seperate config files)'''
from src.files import db_path
DB_PATH = str(db_path())

def get_default_settings():
    return {
        "model_dir": DB_PATH,
        "default_name": "SMTK_CARDS",
        "anki_url": "http://localhost:8765",
        "anki_deck": "SMTK_DEFAULT",
        "anki_key": ""
    }

#TODO MAKE SENTENCE MANAGER