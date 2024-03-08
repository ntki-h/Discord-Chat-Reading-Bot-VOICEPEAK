import json

class WordDictionary:
    
    def __init__(self, dictionary=None):
        self.dictionary = dictionary if dictionary else {}
        self.file_path = 'config/word_dictionary.json'
        self.load_from_json()

    def register_word(self, word, reading):
        self.dictionary[word] = reading
        self.save_to_json()

    def convert_text(self, text):
        for word, reading in self.dictionary.items():
            text = text.replace(word, reading)
        return text

    def save_to_json(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.dictionary, f, ensure_ascii=False, indent=4)

    def load_from_json(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.dictionary = json.load(f)
        except FileNotFoundError:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
            self.dictionary = {}