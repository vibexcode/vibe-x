"""
Performance and benchmark tests for VIBE-X
Tests encoding/decoding speed and storage efficiency
"""

import pytest
import time
import json
from vibex import (
    InlineEncoder,
    InlineDecoder,
    SentimentAnnotation,
    Tokenizer,
    MetaBlock,
)


class TestPerformance:
    """Performance benchmarks"""

    def test_encoding_speed(self):
        """Measure encoding performance"""
        encoder = InlineEncoder(Tokenizer())
        text = "The movie was absolutely amazing and I loved every minute of it"
        annotation = SentimentAnnotation(anchor=3, length=2, polarity=2, intensity=6, context=0, emotion=1)

        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            encoder.encode(text, [annotation])
        end = time.perf_counter()

        avg_time = (end - start) / iterations * 1_000_000  # microseconds
        print(f"\nEncoding time: {avg_time:.2f} µs per operation")
        assert avg_time < 1000  # Should be under 1ms

    def test_decoding_speed(self):
        """Measure decoding performance"""
        encoder = InlineEncoder(Tokenizer())
        decoder = InlineDecoder(Tokenizer())

        text = "The movie was absolutely amazing and I loved every minute of it"
        annotation = SentimentAnnotation(anchor=3, length=2, polarity=2, intensity=6, context=0, emotion=1)
        encoded = encoder.encode(text, [annotation])

        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            decoder.decode(encoded)
        end = time.perf_counter()

        avg_time = (end - start) / iterations * 1_000_000  # microseconds
        print(f"\nDecoding time: {avg_time:.2f} µs per operation")
        assert avg_time < 1000  # Should be under 1ms

    def test_metablock_decode_speed(self):
        """Measure MetaBlock hex decoding speed"""
        meta = MetaBlock(has_span=True, span=2, polarity=2, intensity=6, context=0, emotion=1)
        hex_val = meta.to_hex()

        iterations = 10000
        start = time.perf_counter()
        for _ in range(iterations):
            MetaBlock.from_hex(hex_val)
        end = time.perf_counter()

        avg_time = (end - start) / iterations * 1_000_000  # microseconds
        print(f"\nMetaBlock decode time: {avg_time:.3f} µs per operation")
        assert avg_time < 100  # Should be very fast

    def test_tokenizer_speed(self):
        """Measure tokenization speed"""
        tokenizer = Tokenizer()
        text = "The quick brown fox jumps over the lazy dog" * 10

        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            tokenizer.tokenize(text)
        end = time.perf_counter()

        avg_time = (end - start) / iterations * 1_000_000  # microseconds
        print(f"\nTokenization time: {avg_time:.2f} µs per operation")
        assert avg_time < 500


class TestStorageEfficiency:
    """Test storage efficiency compared to alternatives"""

    def test_hex_storage_size(self):
        """Test that hex encoding is compact"""
        meta = MetaBlock(has_span=True, span=3, polarity=2, intensity=5, context=1, emotion=4, emergency=True)
        hex_val = meta.to_hex()

        # Hex should be exactly 4 characters
        assert len(hex_val) == 4

    def test_vs_json_storage(self):
        """Compare VIBE-X storage vs JSON"""
        # VIBE-X
        meta = MetaBlock(has_span=True, span=3, polarity=2, intensity=5, context=1, emotion=4)
        vibe_x_size = len(meta.to_hex())  # 4 bytes

        # Equivalent JSON
        json_data = {
            "has_span": True,
            "span": 3,
            "polarity": "positive",
            "intensity": 5,
            "context": "dynamic",
            "emotion": "surprise",
        }
        json_size = len(json.dumps(json_data))

        print(f"\nVIBE-X: {vibe_x_size} bytes")
        print(f"JSON: {json_size} bytes")
        print(f"Savings: {(1 - vibe_x_size/json_size) * 100:.1f}%")

        assert vibe_x_size < json_size
        assert vibe_x_size <= 4  # Should be at most 4 bytes

    def test_storage_at_scale(self):
        """Calculate storage at scale"""
        # 1 million annotations
        count = 1_000_000

        vibe_x_total_mb = (count * 4) / (1024 ** 2)  # 4 bytes per annotation
        json_total_mb = (count * 120) / (1024 ** 2)  # ~120 bytes per JSON object

        print(f"\nAt {count:,} annotations:")
        print(f"  VIBE-X: {vibe_x_total_mb:.2f} MB")
        print(f"  JSON: {json_total_mb:.2f} MB")
        print(f"  Saved: {json_total_mb - vibe_x_total_mb:.2f} MB")

        assert vibe_x_total_mb < 5  # Should be under 5 MB
        assert json_total_mb > 100  # JSON should be over 100 MB


class TestScalability:
    """Test scalability with many annotations"""

    def test_many_annotations_same_text(self):
        """Test encoding many annotations on same text"""
        encoder = InlineEncoder(Tokenizer())
        decoder = InlineDecoder(Tokenizer())

        text = " ".join([f"word{i}" for i in range(100)])
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(text)

        # Create annotation for every 5th token
        annotations = [
            SentimentAnnotation(
                anchor=i,
                length=1,
                polarity=(i % 4),
                intensity=(i % 8),
                context=(i % 2),
                emotion=(i % 8),
            )
            for i in range(0, len(tokens), 5)
        ]

        start = time.perf_counter()
        encoded = encoder.encode(text, annotations)
        encode_time = time.perf_counter() - start

        start = time.perf_counter()
        decoded = decoder.decode(encoded)
        decode_time = time.perf_counter() - start

        print(f"\n{len(annotations)} annotations:")
        print(f"  Encode: {encode_time*1000:.2f} ms")
        print(f"  Decode: {decode_time*1000:.2f} ms")

        assert len(decoded.blocks) == len(annotations)
        assert encode_time < 0.1  # Under 100ms
        assert decode_time < 0.1

    def test_large_batch_processing(self):
        """Test processing a large batch of texts"""
        encoder = InlineEncoder(Tokenizer())
        decoder = InlineDecoder(Tokenizer())

        # Create 100 sample texts
        texts = [f"This is sample text number {i} with some content" for i in range(100)]

        # Encode all
        start = time.perf_counter()
        encoded_texts = []
        for text in texts:
            annotation = SentimentAnnotation(anchor=3, length=2, polarity=2, intensity=5, context=0, emotion=1)
            encoded = encoder.encode(text, [annotation])
            encoded_texts.append(encoded)
        encode_time = time.perf_counter() - start

        # Decode all
        start = time.perf_counter()
        for encoded in encoded_texts:
            decoder.decode(encoded)
        decode_time = time.perf_counter() - start

        print(f"\n{len(texts)} texts:")
        print(f"  Total encode: {encode_time*1000:.2f} ms")
        print(f"  Total decode: {decode_time*1000:.2f} ms")
        print(f"  Avg encode: {encode_time/len(texts)*1000:.2f} ms per text")
        print(f"  Avg decode: {decode_time/len(texts)*1000:.2f} ms per text")

        assert encode_time < 1.0  # Under 1 second total
        assert decode_time < 1.0


class TestMemoryEfficiency:
    """Test memory efficiency"""

    def test_encoded_text_size_overhead(self):
        """Test that encoded text doesn't add too much overhead"""
        encoder = InlineEncoder(Tokenizer())

        text = "This is a sample text for testing"
        annotation = SentimentAnnotation(anchor=3, length=2, polarity=2, intensity=5, context=0, emotion=1)

        encoded = encoder.encode(text, [annotation])

        original_size = len(text)
        encoded_size = len(encoded)
        overhead = encoded_size - original_size

        print(f"\nOriginal: {original_size} bytes")
        print(f"Encoded: {encoded_size} bytes")
        print(f"Overhead: {overhead} bytes ({overhead/original_size*100:.1f}%)")

        # Overhead should be small (markers + hex = ~8-10 bytes per annotation)
        assert overhead < 20
        assert overhead / original_size < 0.5  # Less than 50% overhead


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
