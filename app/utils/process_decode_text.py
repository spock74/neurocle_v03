import re
import html
import unicodedata

def process_text(input_text):
    # Decode HTML entities
    text = html.unescape(input_text)
    
    # Function to replace accented characters with their non-accented equivalents
    def remove_accents(input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    # Replace common Unicode characters with their Portuguese equivalents
    replacements = {
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u2026': '...',  # Horizontal ellipsis
        '\u2013': '-',  # En dash
        '\u2014': '—',  # Em dash
        '\u00a0': ' ',  # Non-breaking space
    }
    
    # Add all Portuguese characters (uppercase, lowercase, and with diacritics)
    portuguese_chars = 'áàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ'
    for char in portuguese_chars:
        replacements[char] = remove_accents(char)
    
    # Apply replacements
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    
    # Remove any remaining non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    return text


