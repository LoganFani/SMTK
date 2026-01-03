from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

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

    print("Fetched Cards:", cards)

    db_connection.close()

    return {"translations": [{"id": card[0], "source": card[1], "translation": card[2]} for card in cards]}


@app.get("/decks/")
async def decks():
    return FileResponse("../templates/decks.html")