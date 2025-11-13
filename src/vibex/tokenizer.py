from __future__ import annotations
from typing import List


class Tokenizer:
    """
    A minimal whitespace tokenizer compatible with the VIBE-X encoder/decoder.

    - Tokenizes by simple whitespace split.
    - Preserves clean detokenization with single spaces.
    - Inline markers (PUA characters) remain attached to the token they precede.
    """

    def tokenize(self, text: str) -> List[str]:
        """
        Convert text into a list of tokens.
        Inline markers are kept as part of the next token.
        """
        return text.split()

    def detokenize(self, tokens: List[str]) -> str:
        """
        Convert token list back to text.
        Joins tokens with a single space, which is sufficient because
        inline markers do not affect spacing.
        """
        return " ".join(tokens)
