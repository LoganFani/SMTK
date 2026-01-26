from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import time
import shutil

import json

from exports import ExportManager
import io

from settings import get_default_settings

from database import (
    get_db_connection, 
    fetch_all_translations, 
    edit_translation, 
    delete_translation
)

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

@app.get("/view_deck")
async def view_deck_page():
    return FileResponse("../templates/view_deck.html")

@app.get("/decks/get_cards/{deck_name}")
async def get_deck_cards(deck_name: str):
    conn = get_db_connection("../decks.db")
    if conn is None:
        return {"error": "Database connection failed."}
    
    # fetch_all_translations returns list[tuple[int, str, str]] -> (id, source, translation)
    rows = fetch_all_translations(conn, deck_name)
    conn.close()

    if rows is None:
        return []

    # Map tuples to dictionaries so the frontend can use card.source and card.id
    cards = [
        {"id": row[0], "source": row[1], "translation": row[2]} 
        for row in rows
    ]
    return cards

@app.post("/decks/update_batch")
async def update_batch(data: dict):
    deck_name = data.get("deck")
    cards = data.get("cards") # Expecting list of {id, source, translation}
    
    conn = get_db_connection("../decks.db")
    if conn is None:
        return {"error": "Database connection failed."}

    success_count = 0
    for card in cards:
        # Uses your database.py edit_translation function
        success = edit_translation(
            conn, 
            deck_name, 
            card['id'], 
            card['source'], 
            card['translation']
        )
        if success:
            success_count += 1
    
    conn.close()
    return {"status": "success", "updated": success_count}

@app.delete("/decks/{deck_name}/cards/{card_id}")
async def delete_card_from_deck(deck_name: str, card_id: int):
    conn = get_db_connection("../decks.db")
    success = delete_translation(conn, deck_name, card_id)
    conn.close()
    
    if success:
        return {"message": "Card deleted"}
    return {"error": "Failed to delete card"}, 500

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

@app.delete("/models/delete/{repo_id:path}")
async def delete_model(repo_id: str):
    # Convert Repo ID back to folder name
    # Helsinki-NLP/opus-mt-en-es -> models--Helsinki-NLP--opus-mt-en-es
    folder_name = f"models--{repo_id.replace('/', '--')}"
    model_path = os.path.join("../models", folder_name)

    try:
        if os.path.exists(model_path):
            shutil.rmtree(model_path)
            return {"message": f"Deleted {repo_id}"}
        return {"error": "Model folder not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

# --- EXPORT OPTIONS ---

# Initialize the manager
exporter = ExportManager()

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
import io
import database  # Assuming your file is named database.py

@app.get("/export")
async def export_cards(
    format: str = Query(...), 
    name: str = Query(...)
):
    # 1. Connect to your database (replace 'smtk.db' with your actual db name)
    conn = database.get_db_connection("../decks.db")
    if not conn:
        raise HTTPException(status_code=500, detail="DATABASE_CONNECTION_FAILED")

    try:
        # 2. Fetch cards using the new dictionary helper
        cards = database.fetch_all_translations_dict(conn, name)
        conn.close() # Clean up the connection

        if not cards:
            raise HTTPException(status_code=404, detail="DECK_EMPTY_OR_NOT_FOUND")

        # 3. Use your existing exporter (switchboard) logic
        # This part assumes 'exporter' is initialized in your app.py
        result = exporter.export(cards, name, format)
        
        data = result["data"]
        processed_data = io.BytesIO(data.encode('utf-8') if isinstance(data, str) else data)

        return StreamingResponse(
            processed_data,
            media_type=result["mime"],
            headers={
                "Content-Disposition": f"attachment; filename={name}.{result['ext']}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        if conn: conn.close()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/push_confirmation")
async def push_confirmation():
    return FileResponse("../templates/push_confirmation.html")


# --- SETTINGS PAGE ---
SETTINGS_FILE = "../settings.json"

@app.get("/api/settings")
async def get_settings():
    if not os.path.exists(SETTINGS_FILE):
        return get_default_settings()
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

@app.post("/api/settings")
async def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)
    return {"status": "success"}

# Add this route to serve the page
@app.get("/settings")
async def settings_page():
    return FileResponse("../templates/settings.html")
