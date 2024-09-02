from googletrans import Translator

translator = Translator()

def translate_text (segment, source_lang, dest_language):
    translated = translator.translate(
        segment['text'], 
        src=source_lang,
        dest=dest_language
        )
        
    return translated.text.replace(".", "")
