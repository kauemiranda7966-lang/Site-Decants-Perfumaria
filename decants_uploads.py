import re
import secrets
import time
from email import policy
from email.parser import BytesParser
from pathlib import Path


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def safe_upload_name(filename):
    stem = Path(filename or "produto").stem
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        suffix = ".png"
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-").lower() or "produto"
    return f"{int(time.time())}-{secrets.token_hex(4)}-{stem}{suffix}"


def parse_multipart_image(headers, body):
    content_type = headers.get("Content-Type", "")
    message_bytes = (
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("utf-8")
        + body
    )
    message = BytesParser(policy=policy.default).parsebytes(message_bytes)
    if not message.is_multipart():
        raise ValueError("Envie uma imagem em multipart/form-data.")

    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue
        params = dict(part.get_params(header="content-disposition") or [])
        if params.get("name") != "image":
            continue
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if not filename or not payload:
            raise ValueError("Imagem obrigatoria.")
        return filename, payload

    raise ValueError("Imagem obrigatoria.")
