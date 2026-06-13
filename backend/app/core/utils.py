"""Shared utility functions."""


def escape_like_pattern(value: str) -> str:
    """Escape special characters in LIKE/ILIKE patterns to prevent wildcard injection.

    Escapes backslash, then % and _ which are wildcards in SQL LIKE/ILIKE.
    """
    if not value:
        return value
    result = value.replace("\\", "\\\\")
    result = result.replace("%", "\\%")
    result = result.replace("_", "\\_")
    return result
