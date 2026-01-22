from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import time

app = FastAPI()

app.mount("/static", StaticFiles(directory="../static"), name="static")

class MineReq(BaseModel):
    content: str
    model_id: str

@app.get("/")
async def root():
    return FileResponse("../templates/index.html")


@app.post("/generate")
async def generate_translation(request: MineReq):
    from translator import Translator
    from formats import format_text
    
    translator = Translator(request.model_id, cache_dir="../models")
    
    input_lines = request.content.splitlines()
    formatted_lines = format_text(input_lines)
    
    translations = translator.batch_generate_translation(formatted_lines)
    
    # Just return the data to the frontend, don't save to DB yet
    return {
        "translations": [{"source": t[0], "translation": t[1]} for t in translations]
    }

@app.post("/decks/insert_batch")
async def insert_batch(data: dict):
    from database import get_db_connection, create_table, insert_translation
    
    deck_name = data.get("deck")
    cards = data.get("cards")
    
    conn = get_db_connection("../decks.db")
    create_table(conn, deck_name)
    
    for card in cards:
        insert_translation(conn, deck_name, card['source'], card['translation'])
    
    conn.close()
    return {"status": "success"}

# --- DECKS ---
@app.get("/decks")
async def decks():
    return FileResponse("../templates/decks.html")


@app.post("/decks/create")
async def create_deck(deck: dict):
    from database import get_db_connection, create_table

    deck_name = deck.get("deck_name")
    if not deck_name:
        return {"error": "Deck name is required."}

    db_connection = get_db_connection("../decks.db")
    if db_connection is None:
        return {"error": "Database connection failed."}

    success = create_table(db_connection, deck_name)
    db_connection.close()

    if success:
        return {"message": f"Deck '{deck_name}' created successfully."}
    else:
        return {"error": "Failed to create deck."}
    

@app.get("/decks/list")
async def list_decks():
    from database import get_db_connection, list_tables

    connection = get_db_connection("../decks.db")
    if connection is None:
        return {"error": "Database connection failed."}
    
    decks = list_tables(connection)
    connection.close()

    return {"decks": decks}

@app.delete("/decks/delete/{deck_name}")
async def delete_deck(deck_name: str):
    from database import get_db_connection, delete_table

    connection = get_db_connection("../decks.db")
    if connection is None:
        return {"error": "Database connection failed."}
    
    success = delete_table(connection, deck_name)
    connection.close()

    if success:
        return {"message": f"Deck '{deck_name}' deleted successfully."}
    else:
        return {"error": "Failed to delete deck."}
    
# --- END DECKS ---

# --- DECK VIEW --- (view/edit specific deck)

# --- GENERATED CARDS --- (cards to be reviewed/edited before adding to deck)
@app.get("/review")
async def review_cards():
    return FileResponse("../templates/review.html")

# --- MODELS --- (manage/download translation models)
@app.get("/models")
async def models_page():
    return FileResponse("../templates/models.html")
import os

@app.get("/models/list")
async def list_available_models():
    # A dictionary of models you want to support
    # The key is the Hugging Face path, the value is a friendly name
    available = {
        "Helsinki-NLP/opus-mt-en-es": "English to Spanish",
        "Helsinki-NLP/opus-mt-es-en": "Spanish to English",
        "Helsinki-NLP/opus-mt-en-de": "English to German",
        "Helsinki-NLP/opus-mt-de-en": "German to English",            
        "Helsinki-NLP/opus-mt-ru-en": "Russian to English",             
        "Helsinki-NLP/opus-mt-en-ru": "English to Russian",          
        "Helsinki-NLP/opus-mt-en-hi": "English to Hindi",                
        "Helsinki-NLP/opus-mt-hi-en": "Hindi to English",           
        "Helsinki-NLP/opus-mt-en-ur": "English to Urdu", 
        "Helsinki-NLP/opus-mt-ur-en": "Urdu to English",
        "Helsinki-NLP/opus-mt-en-fr": "English to French",
        "Helsinki-NLP/opus-mt-fr-en": "French to English",
        "Helsinki-NLP/opus-mt-en-it": "English to Italian",
        "Helsinki-NLP/opus-mt-it-en": "Italian to English",
        "Helsinki-NLP/opus-mt-en-zh": "English to Chinese",
        "Helsinki-NLP/opus-mt-zh-en": "Chinese to English",
        "Helsinki-NLP/opus-mt-en-tl": "English to Tagalog/Filipino",
        "Helsinki-NLP/opus-mt-tl-en": "Tagalog/Filipino to English"
    }
    
    # Check what is already in your cache folder
    model_dir = "../models"
    downloaded = []
    if os.path.exists(model_dir):
        # HuggingFace saves models in a specific format, we check for folder presence
        downloaded = os.listdir(model_dir)

    status_list = []
    for path, name in available.items():
        # Simple check: does the path name appear in the downloaded folders?
        is_downloaded = any(path.replace("/", "--") in folder for folder in downloaded)
        status_list.append({
            "path": path,
            "name": name,
            "downloaded": is_downloaded
        })
    
    return {"models": status_list}

@app.post("/models/download")
async def download_model(model: dict):
    from translator import Translator
    model_path = model.get("path")
    try:
        translator = Translator(lang_model=model_path, cache_dir="../models")
        translator.generate_translation(["This is a test."])  # Trigger download
        return {"message": "Model downloaded successfully"}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/models/downloaded")
async def get_downloaded_models():
    # Keys now match the "repo_id" format (e.g., Helsinki-NLP/opus-mt-en-es)
    model_map = {
        "Helsinki-NLP/opus-mt-en-es": "English to Spanish",
        "Helsinki-NLP/opus-mt-es-en": "Spanish to English",
        "Helsinki-NLP/opus-mt-en-de": "English to German",
        "Helsinki-NLP/opus-mt-de-en": "German to English",            
        "Helsinki-NLP/opus-mt-ru-en": "Russian to English",             
        "Helsinki-NLP/opus-mt-en-ru": "English to Russian",          
        "Helsinki-NLP/opus-mt-en-hi": "English to Hindi",                
        "Helsinki-NLP/opus-mt-hi-en": "Hindi to English",           
        "Helsinki-NLP/opus-mt-en-ur": "English to Urdu", 
        "Helsinki-NLP/opus-mt-ur-en": "Urdu to English",
        "Helsinki-NLP/opus-mt-en-fr": "English to French",
        "Helsinki-NLP/opus-mt-fr-en": "French to English",
        "Helsinki-NLP/opus-mt-en-it": "English to Italian",
        "Helsinki-NLP/opus-mt-it-en": "Italian to English",
        "Helsinki-NLP/opus-mt-en-zh": "English to Chinese",
        "Helsinki-NLP/opus-mt-zh-en": "Chinese to English",
        "Helsinki-NLP/opus-mt-en-tl": "English to Tagalog/Filipino",
        "Helsinki-NLP/opus-mt-tl-en": "Tagalog/Filipino to English"
    }
    
    model_dir = "../models"
    downloaded = []
    
    if os.path.exists(model_dir):
        for folder in os.listdir(model_dir):
            if folder.startswith("models--"):
                # STEP A: Convert folder name to repo_id format
                # models--Helsinki-NLP--opus-mt-en-es -> Helsinki-NLP/opus-mt-en-es
                repo_id = folder.replace("models--", "").replace("--", "/", 1).replace("--", "-")
                
                # STEP B: Look up the friendly name using the clean repo_id
                display_name = model_map.get(repo_id, repo_id)
                
                downloaded.append({
                    "repo_id": repo_id,
                    "name": display_name
                })
            
    return {"downloaded_models": downloaded}

# --- OPTIONAL (Settings, pull transcript from websites)
