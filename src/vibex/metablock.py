from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from .exceptions import MetaBlockEncodingError, MetaBlockDecodingError


@dataclass(frozen=True)
class MetaBlock:
    """
    Represents a 14-bit SPICE-R emotional metadata block.

    Fields:
        has_span  : 1 bit (bool)
        span      : 0–7 (3 bits)
        polarity  : 2 bits
        intensity : 3 bits
        context   : 1 bit
        emotion   : 3 bits
        reserved  : 1 bit (emergency / future use)
    """

    has_span: bool
    span: Optional[int]
    polarity: int
    intensity: int
    context: int
    emotion: int
    reserved: int

    # ---------------------------------------------------------
    # Encoding to hex
    # ---------------------------------------------------------

    def to_int(self) -> int:
        """Pack the MetaBlock fields into a 14-bit integer."""
        if self.has_span and (self.span is None or not (0 <= self.span <= 7)):
            raise MetaBlockEncodingError("Span must be between 0 and 7 when has_span is True.")

        if not self.has_span and self.span is not None:
            raise MetaBlockEncodingError("Span must be None when has_span is False.")

        value = 0
        value |= (1 if self.has_span else 0) << 13
        value |= (self.span or 0) << 10
        value |= (self.polarity & 0b11) << 8
        value |= (self.intensity & 0b111) << 5
        value |= (self.context & 0b1) << 4
        value |= (self.emotion & 0b111) << 1
        value |= (self.reserved & 0b1)

        return value

    def to_hex(self) -> str:
        """Return the compact hexadecimal representation."""
        return f"{self.to_int():04x}"

    # ---------------------------------------------------------
    # Decoding from hex
    # ---------------------------------------------------------

    @classmethod
    def from_hex(cls, hex_str: str) -> MetaBlock:
        """Create a MetaBlock from a compact hex string."""
        try:
            value = int(hex_str, 16)
        except ValueError as exc:
            raise MetaBlockDecodingError(f"Invalid hex payload: {hex_str}") from exc

        has_span = (value >> 13) & 0b1
        span = (value >> 10) & 0b111
        polarity = (value >> 8) & 0b11
        intensity = (value >> 5) & 0b111
        context = (value >> 4) & 0b1
        emotion = (value >> 1) & 0b111
        reserved = value & 0b1

        # Convert has_span bit to boolean
        has_span = bool(has_span)

        # If has_span is False → span must be None
        if not has_span:
            span = None

        return cls(
            has_span=has_span,
            span=span,
            polarity=polarity,
            intensity=intensity,
            context=context,
            emotion=emotion,
            reserved=reserved,
        )


# ---------------------------------------------------------
# A helper class used by encoder/decoder
# ---------------------------------------------------------

@dataclass(frozen=True)
class TokenSpan:
    anchor: int
    length: int  # number of tokens covered

    def __repr__(self) -> str:
        return f"TokenSpan(anchor={self.anchor}, length={self.length})"


@dataclass(frozen=True)
class InlineMetaBlock:
    block: MetaBlock
    span: TokenSpan
    marker: str  # actual inline marker string

    def as_marker_payload(self) -> str:
        return self.marker
