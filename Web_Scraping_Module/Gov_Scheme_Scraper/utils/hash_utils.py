import hashlib
from utils.helpers import process_scheme


def generate_hash(scheme):
    """Generate a stable hash for a scheme after normalizing key fields."""
    if not scheme:
        return None

    s = process_scheme(dict(scheme))

    parts = [
        s.get("title") or "",
        s.get("details") or "",
        s.get("eligibility") or "",
        s.get("benefits") or "",
        s.get("application_link") or "",
    ]

    data = "||".join(parts)
    return hashlib.md5(data.encode("utf-8")).hexdigest()

