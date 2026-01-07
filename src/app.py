from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import time

app = FastAPI()

app.mount("/static", StaticFiles(directory="../static"), name="static")

class MineReq(BaseModel):
    content: str
    target_lang: str
    native_lang: str
    deck: str

@app.get("/")
async def root():
    return FileResponse("../templates/index.html")


@app.post("/generate")
async def generate_translation(request: MineReq):
    from translator import Translator
    from formats import format_text
    from database import get_db_connection, create_table, insert_translation, fetch_all_translations, delete_translation

    translator = Translator(target_lang=request.target_lang, native_lang=request.native_lang, cache_dir="../models")

    input_lines = request.content.splitlines()
    formatted_lines = format_text(input_lines)
    
    start_time = time.perf_counter()
    translations = translator.batch_generate_translation(formatted_lines)

    db_connection = get_db_connection("../decks.db")
    if db_connection is None:
        return {"error": "Database connection failed."}


    success = create_table(db_connection, request.deck)

    if not success:
        return {"error": "Failed to create or access the specified deck."}
    

    for source_text, translated_text in translations:
        insert_translation(db_connection, request.deck, source_text, translated_text)

    cards = fetch_all_translations(db_connection, request.deck)

    db_connection.close()

    end_time = time.perf_counter()

    processing_time = end_time - start_time

    return {"status": "success", "processing_time": processing_time}

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

# --- OPTIONAL (Settings, pull transcript from websites)
