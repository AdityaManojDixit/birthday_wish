from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# -------------------- Zero-width emoji chars --------------------
ZWSP, ZWNJ, ZWJ, WJ = "\u200B", "\u200C", "\u200D", "\u2060"

# -------------------- Models --------------------
class Message(BaseModel):
    text: str

# -------------------- Helper Functions --------------------
def caesar(text, shift=3, encrypt=True):
    return "".join(
        chr((ord(c) - (ord('A') if c.isupper() else ord('a')) + (shift if encrypt else -shift)) % 26 +
            (ord('A') if c.isupper() else ord('a'))) if c.isalpha() else c
        for c in text
    )

def decode_hidden_emojis(text):
    out, i = "", 0
    while i < len(text):
        if text[i] == ZWSP:
            i += 1; bits = ""
            while text[i] != WJ:
                bits += "0" if text[i]==ZWNJ else "1"
                i += 1
            out += chr(int(bits, 2))
        else:
            out += text[i]
        i += 1
    return out

def decrypt_text(cipher_text):
    """Full decrypt: hidden emojis + Caesar"""
    return caesar(decode_hidden_emojis(cipher_text), encrypt=False)

# -------------------- API Endpoints --------------------
@app.post("/decode_emojis")
def api_decode_emojis(msg: Message):
    return {"decoded": decode_hidden_emojis(msg.text)}

@app.post("/decrypt")
def api_decrypt(msg: Message):
    return {"decrypted": decrypt_text(msg.text)}
