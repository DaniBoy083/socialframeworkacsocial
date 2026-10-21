import re
import unicodedata


def normalize_identity(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    value = re.sub(r"\s+", " ", value).strip().upper()
    value = unicodedata.normalize("NFC", value)
    if any(unicodedata.category(char) in {"Cc", "Cf"} for char in value):
        raise ValueError("A identificação contém caracteres invisíveis inválidos.")
    return value
