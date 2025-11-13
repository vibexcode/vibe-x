from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .metablock import InlineMetaBlock, MetaBlock, TokenSpan
from .exceptions import MetaBlockEncodingError
from .tokenizer import Tokenizer


# ---------------------------------------------------------
# Marker configuration (prefix/suffix)
# ---------------------------------------------------------

@dataclass(frozen=True)
class InlineMarkerConfig:
    """
    Configuration for inline marker delimiters.

    By default:
        prefix = U+E000
        suffix = U+E001

    These belong to the Unicode Private Use Area (PUA) and never collide
    with natural language text.
    """

    prefix: str = "\uE000"
    suffix: str = "\uE001"

    def format_marker(self, hex_payload: str) -> str:
        return f"{self.prefix}{hex_payload}{self.suffix}"


# ---------------------------------------------------------
# User-facing structured annotation
# ---------------------------------------------------------

@dataclass(frozen=True)
class SentimentAnnotation:
    """
    Structured metadata produced by the Master Analyzer.

    anchor     : token index
    length     : number of tokens covered (1 = single token)
    polarity   : 0–3 (2 bits)
    intensity  : 0–7 (3 bits)
    context    : 0/1
    emotion    : 0–7 (3 bits)
    reserved   : typically 0 (future extension)
    """

    anchor: int
    length: int
    polarity: int
    intensity: int
    context: int
    emotion: int
    reserved: int = 0

    def to_metablock(self) -> MetaBlock:
        """Convert annotation to its compact MetaBlock representation."""
        has_span = self.length > 1
        span_value = (self.length - 1) if has_span else None

        return MetaBlock(
            has_span=has_span,
            span=span_value,
            polarity=self.polarity,
            intensity=self.intensity,
            context=self.context,
            emotion=self.emotion,
            reserved=self.reserved,
        )

    def to_inline_block(self, marker_config: InlineMarkerConfig) -> InlineMetaBlock:
        """Wrap MetaBlock in its inline representation."""
        block = self.to_metablock()
        span = TokenSpan(anchor=self.anchor, length=self.length)
        marker = marker_config.format_marker(block.to_hex())
        return InlineMetaBlock(block=block, span=span, marker=marker)


# ---------------------------------------------------------
# Inline Encoder
# ---------------------------------------------------------

class InlineEncoder:
    """
    Injects MetaBlocks into the token stream using inline marker syntax.

    Executes the following:
        - Tokenizes text
        - Converts annotations into InlineMetaBlocks
        - Validates anchor indices
        - Injects inline markers at anchors
        - Produces encoded text safely
    """

    def __init__(self, tokenizer: Tokenizer, marker_config: InlineMarkerConfig | None = None) -> None:
        self._tokenizer = tokenizer
        self._marker_config = marker_config or InlineMarkerConfig()

    def encode(self, text: str, annotations: Iterable[SentimentAnnotation]) -> str:
        tokens = self._tokenizer.tokenize(text)
        inline_blocks = [annotation.to_inline_block(self._marker_config) for annotation in annotations]

        # Basic validation: anchor must exist
        for block in inline_blocks:
            if block.span.anchor >= len(tokens):
                raise MetaBlockEncodingError(
                    f"Anchor index {block.span.anchor} is out of bounds for {len(tokens)} tokens."
                )

        # Sort blocks by anchor descending (so injection won't shift later anchors)
        inline_blocks.sort(key=lambda b: b.span.anchor, reverse=True)

        tokens_copy: List[str] = tokens[:]
        for block in inline_blocks:
            idx = block.span.anchor
            tokens_copy[idx] = block.as_marker_payload() + tokens_copy[idx]

        return self._tokenizer.detokenize(tokens_copy)
