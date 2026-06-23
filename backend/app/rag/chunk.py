"""Split markdown content into retrieval-sized chunks.

Splits on blank lines (paragraphs / table blocks / headings) and packs them up
to a target character budget, so headings stay attached to the text below them.
"""

from __future__ import annotations

TARGET_CHARS = 600
MAX_CHARS = 900


def chunk_markdown(text: str, target: int = TARGET_CHARS, hard_max: int = MAX_CHARS) -> list[str]:
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    chunks: list[str] = []
    buf = ""

    for block in blocks:
        if not buf:
            buf = block
        elif len(buf) + len(block) + 2 <= target:
            buf = f"{buf}\n\n{block}"
        else:
            chunks.append(buf)
            buf = block
        # A single very large block becomes its own chunk.
        if len(buf) >= hard_max:
            chunks.append(buf)
            buf = ""

    if buf:
        chunks.append(buf)
    return chunks
