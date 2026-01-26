import csv
import io
import json
import os
import genanki

class ExportManager:
    def __init__(self, settings_path="../settings.json"):
        self.settings_path = settings_path
        # Fallback defaults if the file doesn't exist yet
        self.defaults = {
            "model_dir": "../models",
            "default_name": "Mined_Cards",
            "anki_url": "http://localhost:8765",
            "anki_deck": "SMTK_Mining",
            "anki_key": ""
        }

    def _get_settings(self):
        """Helper to get the latest user settings."""
        if not os.path.exists(self.settings_path):
            return self.defaults
        try:
            with open(self.settings_path, "r") as f:
                return {**self.defaults, **json.load(f)}
        except:
            return self.defaults

    def export(self, cards, deck_name, export_format):
        # Always fetch fresh settings before an export
        settings = self._get_settings()
        
        # If the user didn't provide a deck_name in the prompt, use the one from settings
        final_deck_name = deck_name or settings["anki_deck"]

        format_map = {
            'csv': self._to_csv,
            'anki_apkg': self._to_anki_apkg,
        }

        handler = format_map.get(export_format)
        if not handler:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        return handler(cards, final_deck_name, settings)

    def _to_csv(self, cards, deck_name, settings):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Source", "Translation"])
        for card in cards:
            writer.writerow([card.get('source', ''), card.get('translation', '')])
        
        return {"data": output.getvalue(), "mime": "text/csv", "ext": "csv"}

    def _to_anki_apkg(self, cards, deck_name, settings):
        # Use random but consistent IDs for the model and deck
        model = genanki.Model(
            1607392319,
            'SMTK_Standard',
            fields=[{'name': 'Front'}, {'name': 'Back'}],
            templates=[{
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
            }]
        )
        
        # We generate a unique ID based on the deck name to avoid collisions
        deck_id = hash(deck_name) & 0xffffffff 
        deck = genanki.Deck(deck_id, deck_name)
        
        for card in cards:
            note = genanki.Note(model=model, fields=[card.get('source', ''), card.get('translation', '')])
            deck.add_note(note)

        output = io.BytesIO()
        genanki.Package(deck).write_to_file(output)
        return {"data": output.getvalue(), "mime": "application/octet-stream", "ext": "apkg"}