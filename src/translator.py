from transformers import MarianTokenizer, MarianMTModel

lang_model = "Helsinki-NLP/opus-mt-es-en"

class Translator:
    def __init__(self, target_lang: str, native_lang: str):
        self.lang_model = f"Helsinki-NLP/opus-mt-{target_lang}-{native_lang}"
        self.tokenizer = MarianTokenizer.from_pretrained(self.lang_model)
        self.model = MarianMTModel.from_pretrained(self.lang_model)

    def generate_translation(self, input_text: list[str]) -> list[tuple[str, str]]:
        
        # TODO look into padding and truncation options
        inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=256)

        # TODO look into num_beams parameter for better quality
        translated = self.model.generate(**inputs, num_beams = 1)

        translated_text = self.tokenizer.batch_decode(translated, skip_special_tokens=True)
        
        return list(zip(input_text, translated_text))

    def batch_generate_translation(self, input_text: list[str], batch_size: int = 8) -> list[tuple[str, str]]:
        result = []
        for i in range(0, len(input_text), batch_size):
            batch = input_text[i:i + batch_size]
            batch_result = self.generate_translation(batch)
            result.extend(batch_result)
        return result


