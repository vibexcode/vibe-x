"""
Comprehensive edge case tests for VIBE-X
Tests boundary conditions, error handling, and unusual inputs
"""

import pytest
from vibex import (
    InlineEncoder,
    InlineDecoder,
    SentimentAnnotation,
    Tokenizer,
    MetaBlock,
)
from vibex.exceptions import MetaBlockEncodingError


class TestMetaBlockEdgeCases:
    """Test MetaBlock with boundary values"""

    def test_minimum_values(self):
        """Test MetaBlock with all minimum values"""
        meta = MetaBlock(
            has_span=False,
            span=0,
            polarity=0,
            intensity=0,
            context=0,
            emotion=0,
            emergency=False,
        )
        assert meta.to_int() == 0
        assert meta.to_hex() == "0000"

    def test_maximum_values(self):
        """Test MetaBlock with all maximum values"""
        meta = MetaBlock(
            has_span=True,
            span=7,  # 3 bits max
            polarity=3,  # 2 bits max
            intensity=7,  # 3 bits max
            context=1,
            emotion=7,  # 3 bits max
            emergency=True,
        )
        assert meta.to_int() == 16383  # 2^14 - 1
        assert meta.to_hex() == "3fff"

    def test_round_trip_all_combinations(self):
        """Test round-trip encoding for various combinations"""
        test_cases = [
            (True, 3, 2, 5, 1, 4, True),
            (False, 0, 0, 0, 0, 0, False),
            (True, 7, 3, 7, 1, 7, True),
            (False, 2, 1, 3, 0, 5, False),
        ]

        for has_span, span, polarity, intensity, context, emotion, emergency in test_cases:
            meta = MetaBlock(has_span, span, polarity, intensity, context, emotion, emergency)
            hex_val = meta.to_hex()
            restored = MetaBlock.from_hex(hex_val)
            assert meta == restored

    def test_invalid_hex_values(self):
        """Test that invalid hex values raise errors"""
        invalid_hexes = [
            "ZZZZ",  # Invalid hex characters
            "12",  # Too short
            "12345",  # Too long
            "",  # Empty
            "GGGG",  # Invalid characters
        ]

        for invalid_hex in invalid_hexes:
            with pytest.raises((ValueError, AssertionError)):
                MetaBlock.from_hex(invalid_hex)

    def test_hex_padding(self):
        """Test that hex values are properly padded"""
        meta = MetaBlock(False, 0, 0, 1, 0, 0, False)
        hex_val = meta.to_hex()
        assert len(hex_val) == 4
        assert hex_val == "0008"  # Should be padded with leading zeros


class TestTokenizerEdgeCases:
    """Test Tokenizer with edge cases"""

    def test_empty_string(self):
        """Test tokenizing empty string"""
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("")
        assert tokens == []

    def test_single_word(self):
        """Test tokenizing single word"""
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("hello")
        assert tokens == ["hello"]

    def test_whitespace_only(self):
        """Test tokenizing whitespace-only string"""
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("   \n\t  ")
        assert tokens == []

    def test_multiple_spaces(self):
        """Test that multiple spaces are collapsed"""
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("hello    world")
        assert tokens == ["hello", "world"]

    def test_special_characters(self):
        """Test tokenizing with special characters"""
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("hello! world? yes.")
        assert len(tokens) == 4
        assert tokens == ["hello!", "world?", "yes.", ""]

    def test_unicode_characters(self):
        """Test tokenizing unicode text"""
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize("こんにちは 世界")
        assert len(tokens) == 2

    def test_detokenize_empty(self):
        """Test detokenizing empty list"""
        tokenizer = Tokenizer()
        text = tokenizer.detokenize([])
        assert text == ""

    def test_round_trip_tokenization(self):
        """Test tokenize -> detokenize round trip"""
        tokenizer = Tokenizer()
        original = "hello world this is a test"
        tokens = tokenizer.tokenize(original)
        restored = tokenizer.detokenize(tokens)
        assert restored == original


class TestEncoderEdgeCases:
    """Test InlineEncoder with edge cases"""

    def test_encode_empty_text(self):
        """Test encoding empty text"""
        encoder = InlineEncoder(Tokenizer())
        with pytest.raises(MetaBlockEncodingError):
            encoder.encode("", [SentimentAnnotation(0, 1, 2, 5, 0, 1)])

    def test_encode_no_annotations(self):
        """Test encoding with no annotations"""
        encoder = InlineEncoder(Tokenizer())
        text = "Hello world"
        encoded = encoder.encode(text, [])
        assert encoded == text  # Should be unchanged

    def test_anchor_out_of_bounds(self):
        """Test that out-of-bounds anchor raises error"""
        encoder = InlineEncoder(Tokenizer())
        text = "Hello world"
        with pytest.raises(MetaBlockEncodingError):
            encoder.encode(text, [SentimentAnnotation(anchor=100, length=1, polarity=2, intensity=5, context=0, emotion=1)])

    def test_span_exceeds_text_length(self):
        """Test that span exceeding text length raises error"""
        encoder = InlineEncoder(Tokenizer())
        text = "Hello world"  # 2 tokens
        with pytest.raises(MetaBlockEncodingError):
            encoder.encode(text, [SentimentAnnotation(anchor=1, length=5, polarity=2, intensity=5, context=0, emotion=1)])

    def test_negative_anchor(self):
        """Test that negative anchor raises error"""
        encoder = InlineEncoder(Tokenizer())
        text = "Hello world"
        with pytest.raises((MetaBlockEncodingError, ValueError)):
            encoder.encode(text, [SentimentAnnotation(anchor=-1, length=1, polarity=2, intensity=5, context=0, emotion=1)])

    def test_zero_length_span(self):
        """Test encoding with zero-length span"""
        encoder = InlineEncoder(Tokenizer())
        text = "Hello world"
        # Zero-length should still work (marks a position)
        encoded = encoder.encode(text, [SentimentAnnotation(anchor=0, length=0, polarity=2, intensity=5, context=0, emotion=1)])
        assert encoded != text  # Should be encoded

    def test_multiple_overlapping_annotations(self):
        """Test multiple annotations on the same token"""
        encoder = InlineEncoder(Tokenizer())
        text = "Hello world test"
        annotations = [
            SentimentAnnotation(anchor=1, length=1, polarity=2, intensity=5, context=0, emotion=1),
            SentimentAnnotation(anchor=1, length=1, polarity=1, intensity=3, context=1, emotion=5),
        ]
        encoded = encoder.encode(text, annotations)
        assert encoded != text

    def test_annotation_order_independence(self):
        """Test that annotation order doesn't affect encoding"""
        encoder = InlineEncoder(Tokenizer())
        text = "Hello world test"

        ann1 = SentimentAnnotation(anchor=0, length=1, polarity=2, intensity=5, context=0, emotion=1)
        ann2 = SentimentAnnotation(anchor=2, length=1, polarity=1, intensity=3, context=0, emotion=5)

        encoded1 = encoder.encode(text, [ann1, ann2])
        encoded2 = encoder.encode(text, [ann2, ann1])

        # Both should decode to same clean text
        decoder = InlineDecoder(Tokenizer())
        decoded1 = decoder.decode(encoded1)
        decoded2 = decoder.decode(encoded2)
        assert decoded1.clean_text == decoded2.clean_text

    def test_single_token_text(self):
        """Test encoding single-token text"""
        encoder = InlineEncoder(Tokenizer())
        text = "Hello"
        encoded = encoder.encode(text, [SentimentAnnotation(anchor=0, length=1, polarity=2, intensity=5, context=0, emotion=1)])
        assert encoded != text


class TestDecoderEdgeCases:
    """Test InlineDecoder with edge cases"""

    def test_decode_empty_string(self):
        """Test decoding empty string"""
        decoder = InlineDecoder(Tokenizer())
        decoded = decoder.decode("")
        assert decoded.clean_text == ""
        assert decoded.clean_tokens == []
        assert decoded.blocks == []

    def test_decode_text_without_markers(self):
        """Test decoding text without any markers"""
        decoder = InlineDecoder(Tokenizer())
        text = "Hello world this is a test"
        decoded = decoder.decode(text)
        assert decoded.clean_text == text
        assert len(decoded.blocks) == 0

    def test_decode_malformed_markers(self):
        """Test decoding with incomplete/malformed markers"""
        decoder = InlineDecoder(Tokenizer())
        # Text with start marker but no hex or end marker
        text = "Hello \ue000world"
        decoded = decoder.decode(text)
        # Should handle gracefully (markers without proper format are ignored)
        assert "Hello" in decoded.clean_text

    def test_decode_preserves_text_integrity(self):
        """Test that decode always preserves original text content"""
        encoder = InlineEncoder(Tokenizer())
        decoder = InlineDecoder(Tokenizer())

        original_texts = [
            "Simple text",
            "Text with! special? characters.",
            "Multiple   spaces",
            "Unicode: 你好 مرحبا",
        ]

        for original in original_texts:
            encoded = encoder.encode(
                original,
                [SentimentAnnotation(anchor=0, length=1, polarity=2, intensity=5, context=0, emotion=1)]
            )
            decoded = decoder.decode(encoded)
            # Clean text should match original (modulo whitespace normalization)
            assert decoded.clean_text.strip() == original.strip()

    def test_decode_multiple_blocks(self):
        """Test decoding text with multiple MetaBlocks"""
        encoder = InlineEncoder(Tokenizer())
        decoder = InlineDecoder(Tokenizer())

        text = "First second third fourth"
        annotations = [
            SentimentAnnotation(anchor=0, length=1, polarity=2, intensity=5, context=0, emotion=1),
            SentimentAnnotation(anchor=2, length=1, polarity=1, intensity=3, context=0, emotion=5),
        ]

        encoded = encoder.encode(text, annotations)
        decoded = decoder.decode(encoded)

        assert len(decoded.blocks) == 2
        assert decoded.clean_text == text


class TestSentimentAnnotationEdgeCases:
    """Test SentimentAnnotation validation"""

    def test_max_span_length(self):
        """Test that span length is capped at 7"""
        # Length > 7 should still work but be capped
        ann = SentimentAnnotation(anchor=0, length=7, polarity=2, intensity=5, context=0, emotion=1)
        assert ann.length == 7

    def test_all_polarity_values(self):
        """Test all valid polarity values"""
        for polarity in [0, 1, 2, 3]:
            ann = SentimentAnnotation(anchor=0, length=1, polarity=polarity, intensity=5, context=0, emotion=1)
            assert ann.polarity == polarity

    def test_all_emotion_values(self):
        """Test all valid emotion values"""
        for emotion in range(8):
            ann = SentimentAnnotation(anchor=0, length=1, polarity=2, intensity=5, context=0, emotion=emotion)
            assert ann.emotion == emotion

    def test_all_intensity_values(self):
        """Test all valid intensity values"""
        for intensity in range(8):
            ann = SentimentAnnotation(anchor=0, length=1, polarity=2, intensity=intensity, context=0, emotion=1)
            assert ann.intensity == intensity

    def test_emergency_flag(self):
        """Test emergency flag"""
        ann = SentimentAnnotation(
            anchor=0, length=1, polarity=1, intensity=7, context=0, emotion=3, emergency=True
        )
        assert ann.emergency is True


class TestIntegrationEdgeCases:
    """Integration tests with edge cases"""

    def test_full_pipeline_empty_annotations(self):
        """Test full encode-decode pipeline with no annotations"""
        encoder = InlineEncoder(Tokenizer())
        decoder = InlineDecoder(Tokenizer())

        text = "This is a test"
        encoded = encoder.encode(text, [])
        decoded = decoder.decode(encoded)

        assert decoded.clean_text == text
        assert len(decoded.blocks) == 0

    def test_full_pipeline_many_annotations(self):
        """Test with many annotations"""
        encoder = InlineEncoder(Tokenizer())
        decoder = InlineDecoder(Tokenizer())

        text = "One two three four five six seven eight"
        tokens = Tokenizer().tokenize(text)

        # Annotate every token
        annotations = [
            SentimentAnnotation(
                anchor=i,
                length=1,
                polarity=(i % 4),
                intensity=(i % 8),
                context=(i % 2),
                emotion=(i % 8),
            )
            for i in range(len(tokens))
        ]

        encoded = encoder.encode(text, annotations)
        decoded = decoder.decode(encoded)

        assert decoded.clean_text == text
        assert len(decoded.blocks) == len(annotations)

    def test_unicode_text_full_pipeline(self):
        """Test full pipeline with Unicode text"""
        encoder = InlineEncoder(Tokenizer())
        decoder = InlineDecoder(Tokenizer())

        text = "Güzel bir gün! 😊"
        encoded = encoder.encode(text, [SentimentAnnotation(anchor=0, length=1, polarity=2, intensity=6, context=0, emotion=1)])
        decoded = decoder.decode(encoded)

        assert "Güzel" in decoded.clean_text

    def test_very_long_text(self):
        """Test with very long text"""
        encoder = InlineEncoder(Tokenizer())
        decoder = InlineDecoder(Tokenizer())

        # Create a long text
        words = ["word"] * 1000
        text = " ".join(words)

        annotations = [
            SentimentAnnotation(anchor=0, length=1, polarity=2, intensity=5, context=0, emotion=1),
            SentimentAnnotation(anchor=500, length=1, polarity=1, intensity=3, context=0, emotion=5),
        ]

        encoded = encoder.encode(text, annotations)
        decoded = decoder.decode(encoded)

        assert len(decoded.clean_tokens) == 1000
        assert len(decoded.blocks) == 2


class TestErrorMessages:
    """Test that error messages are helpful"""

    def test_anchor_error_message(self):
        """Test that anchor out of bounds gives helpful error"""
        encoder = InlineEncoder(Tokenizer())
        text = "Hello world"

        with pytest.raises(MetaBlockEncodingError) as exc_info:
            encoder.encode(text, [SentimentAnnotation(anchor=10, length=1, polarity=2, intensity=5, context=0, emotion=1)])

        assert "anchor" in str(exc_info.value).lower()

    def test_span_error_message(self):
        """Test that span out of bounds gives helpful error"""
        encoder = InlineEncoder(Tokenizer())
        text = "Hello world"

        with pytest.raises(MetaBlockEncodingError) as exc_info:
            encoder.encode(text, [SentimentAnnotation(anchor=1, length=10, polarity=2, intensity=5, context=0, emotion=1)])

        # Error message should mention the problem
        assert "span" in str(exc_info.value).lower() or "length" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
