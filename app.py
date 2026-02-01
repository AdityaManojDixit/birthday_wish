from fastapi import FastAPI
from pydantic import BaseModel
from cryptography.fernet import Fernet
import os

app = FastAPI()

# -------------------- Encryption Setup --------------------
# Generate a key once, store as ENV variable in Render
# For testing, you can generate a key locally:
#   from cryptography.fernet import Fernet
#   key = Fernet.generate_key()
#   print(key)
SECRET_KEY = os.environ.get("SECRET_KEY", Fernet.generate_key())
fernet = Fernet(SECRET_KEY)

ZWSP, ZWNJ, ZWJ, WJ = "\u200B", "\u200C", "\u200D", "\u2060"

# -------------------- Hidden Emoji Functions --------------------
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

# -------------------- Encryption / Decryption --------------------
def encrypt_text(plain_text: str) -> str:
    return fernet.encrypt(plain_text.encode()).decode()

def decrypt_text(cipher_text: str) -> str:
    # First decode emojis, then decrypt
    decoded = decode_hidden_emojis(cipher_text)
    return fernet.decrypt(decoded.encode()).decode()

# -------------------- API --------------------
class Message(BaseModel):
    text: str

@app.post("/encrypt")
def api_encrypt(msg: Message):
    return {"encrypted": encrypt_text(msg.text)}

@app.post("/decrypt")
def api_decrypt(msg: Message):
    return {"decrypted": decrypt_text(msg.text)}
