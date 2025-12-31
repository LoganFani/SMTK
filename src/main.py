from translator import Translator
from files import TempDirHandler
import json

lang_model = "Helsinki-NLP/opus-mt-es-en"

def main():
    spanish_to_english_translator = Translator(lang_model)

    sentences = []
    with open ("formatted_input.txt", "r", encoding="utf-8") as infile:
        for line in infile:
            sentences.append(line.strip())

    result_batch = spanish_to_english_translator.batch_generate_translation(sentences)

    with open ("outputs/translations.json", "w", encoding="utf-8") as outfile:
        json.dump(result_batch, outfile, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()