class MetaBlockEncodingError(Exception):
    """Raised when an error occurs during MetaBlock encoding."""
    pass


class MetaBlockDecodingError(Exception):
    """Raised when a marker or MetaBlock cannot be parsed correctly."""
    pass
