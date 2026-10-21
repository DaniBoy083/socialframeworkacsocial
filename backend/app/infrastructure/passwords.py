import hashlib
import hmac
import re


def verify_password(password: str, stored: str) -> bool:
    """Node scrypt defaults (N=16384,r=8,p=1), UTF-8 salt, 64-byte output.

    ACS contract specifies salt:hash_hex. Parameters checked against the source ABA adapter;
    real credentials still require institutional acceptance; never normalize passwords or fall back to plaintext.
    """
    try:
        salt, expected_hex = stored.split(":", 1) if ":" in stored else ("", "")
        valid_format = bool(
            salt and len(salt) <= 512 and re.fullmatch(r"[0-9a-fA-F]{128}", expected_hex)
        )
        if not valid_format:
            salt, expected_hex = "unconfigured-account", "0" * 128
        derived = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt.encode("utf-8"),
            n=16384,
            r=8,
            p=1,
            dklen=64,
            maxmem=64 * 1024 * 1024,
        )
        matches = hmac.compare_digest(derived, bytes.fromhex(expected_hex))
        return valid_format and matches
    except (ValueError, TypeError, AttributeError):
        return False
