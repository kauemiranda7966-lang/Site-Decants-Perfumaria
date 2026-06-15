def _escape_pdf_text(value):
    return (
        str(value or "")
        .encode("latin-1", errors="replace")
        .decode("latin-1")
        .replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def _assemble_pdf(objects):
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF"
        ).encode("ascii")
    )
    return bytes(pdf)


def build_pdf_pages(pages):
    streams = []
    for lines in pages:
        commands = ["BT", "/F1 12 Tf", "42 800 Td"]
        for index, (text, size) in enumerate(lines):
            if index:
                commands.append("0 -24 Td")
            commands.extend([f"/F1 {size} Tf", f"({_escape_pdf_text(text)}) Tj"])
        commands.append("ET")
        streams.append("\n".join(commands).encode("latin-1"))

    page_ids = [3 + index * 2 for index in range(len(streams))]
    font_id = 3 + len(streams) * 2
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        (
            f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] "
            f"/Count {len(page_ids)} >>"
        ).encode("ascii"),
    ]
    for index, stream in enumerate(streams):
        content_id = page_ids[index] + 1
        objects.extend(
            [
                (
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                    f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
                    f"/Contents {content_id} 0 R >>"
                ).encode("ascii"),
                (
                    b"<< /Length "
                    + str(len(stream)).encode("ascii")
                    + b" >>\nstream\n"
                    + stream
                    + b"\nendstream"
                ),
            ]
        )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    return _assemble_pdf(objects)


def build_simple_pdf(lines):
    commands = ["BT", "/F1 12 Tf", "48 790 Td"]
    for index, (text, size) in enumerate(lines):
        if index:
            commands.append("0 -28 Td")
        commands.extend([f"/F1 {size} Tf", f"({_escape_pdf_text(text)}) Tj"])
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ),
        (
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    return _assemble_pdf(objects)
