from __future__ import annotations

import random
import string

from captcha.image import ImageCaptcha

from app.config import settings

# Drop visually ambiguous characters (O/0, I/1/L) to reduce false failures.
_ALPHABET = "".join(
    c for c in (string.ascii_uppercase + string.digits) if c not in "O0I1L"
)

_GENERATOR = ImageCaptcha(width=280, height=100)


def new_code() -> str:
    return "".join(random.choices(_ALPHABET, k=settings.captcha_length))


def render(code: str) -> bytes:
    buffer = _GENERATOR.generate(code)
    return buffer.getvalue()


def matches(expected: str, given: str | None) -> bool:
    return (given or "").strip().upper() == expected.upper()
