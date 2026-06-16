from decants_validation import parse_price


def product_price(product, volume):
    promo_key = "precoPromocional10" if volume == 10 else "precoPromocional5"
    base_key = "preco10" if volume == 10 else "preco5"
    price = (
        product[promo_key]
        if product["promocao"] and product[promo_key]
        else product[base_key]
    )
    return parse_price(price)


def build_order_items(conn, checkout_items):
    order_items = []
    for item in checkout_items:
        if item["product_id"] > 0:
            row = conn.execute(
                "SELECT * FROM products WHERE id = ?", (item["product_id"],)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM products WHERE nome = ?", (item["product_name"],)
            ).fetchone()

        if not row:
            raise ValueError("Produto nao encontrado.")
        if row["estoque"] < item["quantity"]:
            raise ValueError(f"Estoque insuficiente para {row['nome']}.")

        unit_price = product_price(row, item["volume"])
        if unit_price <= 0:
            raise ValueError(f"Preco invalido para {row['nome']}.")
        order_items.append(
            {
                "product_id": row["id"],
                "product_name": row["nome"],
                "volume": item["volume"],
                "quantity": item["quantity"],
                "unit_price": unit_price,
                "subtotal": round(unit_price * item["quantity"], 2),
            }
        )
    return order_items


def reserve_order_stock(conn, order_id):
    order = conn.execute(
        "SELECT id, stock_reserved FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    if not order or order["stock_reserved"]:
        return

    items = conn.execute(
        """
        SELECT product_id, product_name, quantity
        FROM order_items WHERE order_id = ?
        """,
        (order_id,),
    ).fetchall()
    for item in items:
        result = conn.execute(
            """
            UPDATE products
            SET estoque = estoque - ?
            WHERE id = ? AND estoque >= ?
            """,
            (item["quantity"], item["product_id"], item["quantity"]),
        )
        if result.rowcount == 0:
            raise ValueError(f"Estoque insuficiente para {item['product_name']}.")
    conn.execute("UPDATE orders SET stock_reserved = 1 WHERE id = ?", (order_id,))


def release_order_stock(conn, order_id):
    result = conn.execute(
        """
        UPDATE orders SET stock_reserved = 0
        WHERE id = ? AND stock_reserved = 1
        """,
        (order_id,),
    )
    if result.rowcount == 0:
        return False

    items = conn.execute(
        "SELECT product_id, quantity FROM order_items WHERE order_id = ?",
        (order_id,),
    ).fetchall()
    for item in items:
        conn.execute(
            "UPDATE products SET estoque = estoque + ? WHERE id = ?",
            (item["quantity"], item["product_id"]),
        )
    return True


def release_expired_whatsapp_reservations(conn, max_age_minutes):
    max_age = int(max_age_minutes)
    query = """
        SELECT id, status
        FROM orders
        WHERE payment_method = 'WhatsApp'
          AND status = 'whatsapp_pending'
          AND stock_reserved = 1
          AND updated_at <= datetime('now', ?)
    """
    age_parameter = (f"-{max_age} minutes",)
    expired_orders = conn.execute(query, age_parameter).fetchall()
    if not expired_orders:
        return 0

    released = 0
    for order in expired_orders:
        if not release_order_stock(conn, order["id"]):
            continue
        conn.execute(
            """
            UPDATE orders SET status = 'expired', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (order["id"],),
        )
        conn.execute(
            """
            INSERT INTO order_history (
                order_id, old_status, new_status, note, admin_user
            ) VALUES (?, ?, 'expired', ?, '')
            """,
            (
                order["id"],
                order["status"],
                f"Reserva via WhatsApp expirada apos {max_age} minutos.",
            ),
        )
        released += 1
    return released


def apply_checkout_coupon(order_items, coupon):
    if coupon != "DECANTS5":
        return 0.0

    discount = 0.0
    for item in order_items:
        original_subtotal = item["subtotal"]
        item["unit_price"] = round(item["unit_price"] * 0.95, 2)
        item["subtotal"] = round(item["unit_price"] * item["quantity"], 2)
        discount += original_subtotal - item["subtotal"]
    return round(discount, 2)
