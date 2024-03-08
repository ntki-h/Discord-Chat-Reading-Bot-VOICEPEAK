import json
import logging

class WordDictionary:
    def __init__(self, dictionary=None):
        self.dictionary = dictionary if dictionary else {}
        self.file_path = 'config/word_dictionary.json'
        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler('word_dictionary.log')
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.load_from_json()

    def register_word(self, word, reading):
        self.dictionary[word] = reading
        self.save_to_json()

    def convert_text(self, text):
        for word, reading in self.dictionary.items():
            text = text.replace(word, reading)
        return text

    def save_to_json(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.dictionary, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save dictionary to JSON: {e}")
            raise

    def load_from_json(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.dictionary = json.load(f)
        except FileNotFoundError:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
            self.dictionary = {}
        except Exception as e:
            self.logger.error(f"Failed to load dictionary from JSON: {e}")
            raise