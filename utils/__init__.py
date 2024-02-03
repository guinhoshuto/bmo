from utils.openai import *
from utils.discord import *
from utils.google_custom_search import *
from utils.pushcut import *
from utils.mistral import *
from utils.gemini import *
from utils.http import *

def split_text(text, max_length=2000):
    # Check if the text is shorter than the max_length
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        # Find the last whitespace within the max_length
        cut_off = text.rfind(' ', 0, max_length)
        special_char_index = text.rfind('```', 0, max_length)

        # If '```' is found and there's no closing '```' in the range, adjust the cut_off
        if special_char_index != -1 and text.count('```', 0, max_length) % 2 != 0:
            cut_off = special_char_index

        # If we cannot cut at a whitespace (happens if a very long word is present), force cut at max_length
        if cut_off == -1:
            cut_off = max_length

        # Split the text and prepare for the next iteration
        chunk = text[:cut_off].strip()
        text = text[cut_off:].strip()

        chunks.append(chunk)

    return chunks
