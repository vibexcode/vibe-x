from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .metablock import InlineMetaBlock, MetaBlock, MetaBlockDecodingError, TokenSpan
from .tokenizer import Tokenizer
from .inline_encoder import InlineMarkerConfig


# ---------------------------------------------------------
# Output structure of the decoder
# ---------------------------------------------------------

@dataclass(frozen=True)
class DecodedInlineText:
    """
    Output of the inline decoder.

    clean_text   : text without metadata markers
    clean_tokens : list of tokens after stripping markers
    blocks       : list of InlineMetaBlock extracted from the text
    """

    clean_text: str
    clean_tokens: List[str]
    blocks: List[InlineMetaBlock]


# ---------------------------------------------------------
# Inline Decoder
# ---------------------------------------------------------

class InlineDecoder:
    """
    Extracts MetaBlocks embedded via inline markers.

    Pipeline:
        - Tokenize input text
        - For each token, remove zero or more inline markers
        - Convert marker payloads (hex) into MetaBlocks
        - Produce a list of InlineMetaBlock + clean text
    """

    def __init__(self, tokenizer: Tokenizer, marker_config: InlineMarkerConfig | None = None) -> None:
        self._tokenizer = tokenizer
        self._marker_config = marker_config or InlineMarkerConfig()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def decode(self, inline_text: str) -> DecodedInlineText:
        tokens = self._tokenizer.tokenize(inline_text)

        clean_tokens: List[str] = []
        blocks: List[InlineMetaBlock] = []

        prefix = self._marker_config.prefix
        suffix = self._marker_config.suffix

        for idx, token in enumerate(tokens):
            markers, clean_token = self._extract_markers(token, prefix, suffix)
            clean_tokens.append(clean_token)

            for payload in markers:
                try:
                    block = MetaBlock.from_hex(payload)
                except Exception as exc:
                    raise MetaBlockDecodingError(
                        f"Invalid MetaBlock marker payload '{payload}'"
                    ) from exc

                # Span length reconstruction:
                #   If span=N means total tokens = 1 + N
                span_length = 1 + (block.span or 0)

                inline_block = InlineMetaBlock(
                    block=block,
                    span=TokenSpan(anchor=idx, length=span_length),
                    marker=self._marker_config.format_marker(block.to_hex()),
                )
                blocks.append(inline_block)

        clean_text = self._tokenizer.detokenize(clean_tokens)
        return DecodedInlineText(clean_text=clean_text, clean_tokens=clean_tokens, blocks=blocks)

    # ---------------------------------------------------------
    # INTERNAL: Marker extraction
    # ---------------------------------------------------------

    @staticmethod
    def _extract_markers(token: str, prefix: str, suffix: str) -> tuple[List[str], str]:
        """
        Extract zero or more inline markers from the beginning of a token.

        A token may look like:
            <prefix><hex><suffix><prefix><hex><suffix>word

        We return:
            (["hex1", "hex2"], "word")
        """
        markers: List[str] = []
        current = token

        while current.startswith(prefix):
            end_idx = current.find(suffix, len(prefix))
            if end_idx == -1:
                raise MetaBlockDecodingError("Marker prefix found without matching suffix.")

            payload = current[len(prefix):end_idx]
            markers.append(payload)

            current = current[end_idx + len(suffix):]

        return markers, current
