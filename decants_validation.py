import re
from decimal import Decimal, InvalidOperation


def product_from_row(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "categoria": row["categoria"],
        "img": row["img"],
        "estoque": row["estoque"],
        "preco5": row["preco5"],
        "preco10": row["preco10"],
        "promocao": bool(row["promocao"]),
        "precoPromocional5": row["precoPromocional5"],
        "precoPromocional10": row["precoPromocional10"],
        "destaque": bool(row["destaque"]),
        "selo": row["selo"],
        "chamada": row["chamada"],
    }


def normalize_product(payload):
    product = {
        "nome": str(payload.get("nome", "")).strip(),
        "categoria": str(payload.get("categoria", "masculino")).strip(),
        "img": str(payload.get("img", "")).strip(),
        "estoque": max(0, int(payload.get("estoque") or 0)),
        "preco5": str(payload.get("preco5", "")).strip(),
        "preco10": str(payload.get("preco10", "")).strip(),
        "promocao": 1 if payload.get("promocao") else 0,
        "precoPromocional5": str(payload.get("precoPromocional5", "")).strip(),
        "precoPromocional10": str(payload.get("precoPromocional10", "")).strip(),
        "destaque": 1 if payload.get("destaque") else 0,
        "selo": str(payload.get("selo", "")).strip(),
        "chamada": str(payload.get("chamada", "")).strip(),
    }

    required = (product["nome"], product["img"], product["preco5"], product["preco10"])
    if not all(required):
        raise ValueError("Nome, imagem e precos sao obrigatorios.")
    if product["categoria"] not in {"masculino", "feminino"}:
        raise ValueError("Categoria invalida.")
    return product


def normalize_lead(payload):
    name = str(payload.get("nome", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    phone = re.sub(r"\D+", "", str(payload.get("telefone", "")))

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Informe um email valido.")
    if len(phone) < 10:
        raise ValueError("Informe um telefone com DDD.")
    return {"nome": name[:120], "email": email, "telefone": phone}


def parse_price(value):
    if isinstance(value, (int, float, Decimal)):
        try:
            return round(float(Decimal(str(value))), 2)
        except (InvalidOperation, ValueError):
            return 0.0

    clean = re.sub(r"[^\d,.\-]", "", str(value or "").strip())
    if not clean or clean in {"-", ".", ",", "-.", "-,"}:
        return 0.0

    comma = clean.rfind(",")
    dot = clean.rfind(".")
    if comma >= 0 and dot >= 0:
        decimal_separator = "," if comma > dot else "."
        thousands_separator = "." if decimal_separator == "," else ","
        clean = clean.replace(thousands_separator, "").replace(decimal_separator, ".")
    elif comma >= 0:
        decimal_digits = len(clean) - comma - 1
        clean = clean.replace(",", ".") if decimal_digits in {1, 2} else clean.replace(",", "")
    elif dot >= 0:
        decimal_digits = len(clean) - dot - 1
        if clean.count(".") > 1:
            if decimal_digits == 2:
                parts = clean.split(".")
                clean = "".join(parts[:-1]) + "." + parts[-1]
            else:
                clean = clean.replace(".", "")
        elif decimal_digits not in {1, 2}:
            clean = clean.replace(".", "")

    try:
        return round(float(Decimal(clean)), 2)
    except (InvalidOperation, ValueError):
        return 0.0


def money_to_brl(value):
    return f"{value:.2f}".replace(".", ",")


def valid_brazilian_document(value):
    digits = re.sub(r"\D+", "", str(value or ""))
    if len(digits) not in {11, 14} or len(set(digits)) == 1:
        return False
    if len(digits) == 11:
        total = sum(int(digits[index]) * (10 - index) for index in range(9))
        first = (total * 10 % 11) % 10
        total = sum(int(digits[index]) * (11 - index) for index in range(10))
        second = (total * 10 % 11) % 10
        return digits[-2:] == f"{first}{second}"

    weights = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    total = sum(int(digits[index]) * weights[index] for index in range(12))
    first = 0 if total % 11 < 2 else 11 - total % 11
    weights = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    total = sum(int((digits + str(first))[index]) * weights[index] for index in range(13))
    second = 0 if total % 11 < 2 else 11 - total % 11
    return digits[-2:] == f"{first}{second}"


def normalize_checkout(payload):
    customer = payload.get("customer") or {}
    name = str(customer.get("name", "")).strip()
    email = str(customer.get("email", "")).strip().lower()
    phone = re.sub(r"\D+", "", str(customer.get("phone", "")))
    address = str(customer.get("address", "")).strip()
    postal_code = re.sub(r"\D+", "", str(customer.get("postalCode", "")))
    document = re.sub(r"\D+", "", str(customer.get("document", "")))
    items = payload.get("items") or []
    coupon = str(payload.get("coupon", "")).strip().upper()
    payment_method = str(payload.get("paymentMethod", "mercado_pago")).strip()

    normalized_name = re.sub(r"\s+", " ", name)
    name_parts = normalized_name.split()
    inappropriate_names = {
        "admin", "administrador", "teste", "test", "null", "undefined",
        "palavrao", "xingamento", "porra", "caralho", "merda", "puta",
        "puto", "foda", "fdp",
    }
    if (
        len(normalized_name) < 5
        or len(name_parts) < 2
        or any(len(part) < 2 for part in name_parts)
        or not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ ]+", normalized_name)
        or any(part.lower() in inappropriate_names for part in name_parts)
    ):
        raise ValueError("Informe o nome completo.")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Informe um email valido.")
    if len(phone) not in {10, 11} or len(set(phone)) == 1:
        raise ValueError("Informe um WhatsApp com DDD.")
    if len(postal_code) != 8 or len(set(postal_code)) == 1:
        raise ValueError("Informe um CEP valido com 8 digitos.")
    if not valid_brazilian_document(document):
        raise ValueError("Informe um CPF ou CNPJ valido para a postagem.")
    if (
        len(address) < 10
        or not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9 ,.\/-]+", address)
        or not re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]", address)
        or not re.search(r"\d", address)
    ):
        raise ValueError("Informe endereco completo com rua, numero, bairro e cidade.")
    if not items:
        raise ValueError("Escolha ao menos um perfume.")

    normalized_items = []
    for item in items:
        product_id = int(item.get("productId") or 0)
        product_name = str(item.get("productName", "")).strip()
        volume = int(item.get("volume") or 0)
        quantity = max(1, min(20, int(item.get("quantity") or 1)))
        if (product_id <= 0 and not product_name) or volume not in {5, 10}:
            raise ValueError("Item invalido no carrinho.")
        normalized_items.append(
            {
                "product_id": product_id,
                "product_name": product_name,
                "volume": volume,
                "quantity": quantity,
            }
        )

    return {
        "customer": {
            "name": normalized_name,
            "email": email,
            "phone": phone,
            "address": re.sub(r"\s+", " ", address),
            "postal_code": postal_code,
            "document": document,
        },
        "items": normalized_items,
        "coupon": coupon if coupon == "DECANTS5" else "",
        "payment_method": (
            payment_method
            if payment_method in {"mercado_pago", "whatsapp"}
            else "mercado_pago"
        ),
    }
