from translator import Translator
from files import TempDirHandler
from formats import is_noise
import argparse

def main(argv=None):
    parser = argparse.ArgumentParser(description="Translate Spanish text to English.")
    parser.add_argument("--list", action="store_true", help="List available translation models.")
    parser.add_argument("--input", type=str, required=False, help="Path to the input text file.")
    parser.add_argument("--paste", type=str, required=False, help="Direct text input to translate.")
    parser.add_argument("--target_lang", type=str, help="Target language code for learning")
    parser.add_argument("--native_lang", type=str, help="Native language code for learning")
    args = parser.parse_args(argv)
    
    if args.list:
        print("Available translation models:")
        with open("../config/lang_codes.txt", "r", encoding="utf-8") as f:
            for line in f:
                print(line)
        return

    target_lang = args.target_lang
    native_lang = args.native_lang
    translator = Translator(target_lang=target_lang, native_lang=native_lang)

    sentences = []
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            for line in f:
                if not is_noise(line):
                    sentences.append(line.strip())
    
    elif args.paste:
        print("\nPaste Text Input:\n")

        text = input()

        for line in text.splitlines():
            if not is_noise(line):
                sentences.append(line.strip())

    else:
        print("No input provided. Please use --input or --paste to provide text for translation.")
        return


    result_batch = translator.batch_generate_translation(sentences)

    with open ("translation_output.txt", "w", encoding="utf-8") as out_file:
        for original, translated in result_batch:
            out_file.write(f"{original},{translated}\n")
    

if __name__ == "__main__":
    main()