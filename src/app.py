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

@app.get("/")
async def root():
    return FileResponse("../templates/index.html")


@app.post("/generate")
async def generate_translation(request: MineReq):
    from translator import Translator
    from formats import format_text

    translator = Translator(target_lang=request.target_lang, native_lang=request.native_lang, cache_dir="../models")
    
    input_lines = request.content.splitlines()
    formatted_lines = format_text(input_lines)
    
    translations = translator.batch_generate_translation(formatted_lines)
    
    return {"translations": [{"source": src, "translation": tgt} for src, tgt in translations]}