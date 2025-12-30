import hashlib


def fake_embedding(text: str) -> list[float]:
    """
    Generate deterministic fake embedding from text hash.
    Returns 1536-dim vector (same as OpenAI text-embedding-3-small).
    No network call required.
    """
    h = hashlib.md5(text.encode()).hexdigest()
    base = [int(h[i:i+2], 16) / 255.0 for i in range(0, 32, 2)]
    return base * 96  # 16 * 96 = 1536 dimensions
