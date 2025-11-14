from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Optional, Iterable, Dict


# =========================================================================
# I. ÇEKİRDEK VIBE-X SINIFLARI (Sizin SRC dosyalarınız)
# =========================================================================

# --- src/vibe_x/exceptions.py ---
class MetaBlockEncodingError(Exception):
    """Raised when an error occurs during MetaBlock encoding."""
    pass


class MetaBlockDecodingError(Exception):
    """Raised when a marker or MetaBlock cannot be parsed correctly."""
    pass


# --- src/vibe_x/tokenizer.py ---
class Tokenizer:
    """A minimal whitespace tokenizer compatible with the VIBE-X encoder/decoder."""

    def tokenize(self, text: str) -> List[str]:
        return text.split()

    def detokenize(self, tokens: List[str]) -> str:
        return " ".join(tokens)


# --- src/vibe_x/metablock.py ---
@dataclass(frozen=True)
class MetaBlock:
    """Represents a 14-bit SPICE-R emotional metadata block."""
    has_span: bool
    span: Optional[int]
    polarity: int
    intensity: int
    context: int
    emotion: int
    reserved: int

    def to_int(self) -> int:
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
        return f"{self.to_int():04x}"

    @classmethod
    def from_hex(cls, hex_str: str) -> MetaBlock:
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
        has_span = bool(has_span)
        if not has_span:
            span = None
        return cls(has_span=has_span, span=span, polarity=polarity, intensity=intensity, context=context,
                   emotion=emotion, reserved=reserved)


@dataclass(frozen=True)
class TokenSpan:
    anchor: int
    length: int


@dataclass(frozen=True)
class InlineMetaBlock:
    block: MetaBlock
    span: TokenSpan
    marker: str  # Gerçek PUA marker string'i (örn: \uE0000a82\uE001)

    def as_marker_payload(self) -> str: return self.marker


@dataclass(frozen=True)
class InlineMarkerConfig:
    prefix: str = "\uE000"
    suffix: str = "\uE001"

    def format_marker(self, hex_payload: str) -> str:
        return f"{self.prefix}{hex_payload}{self.suffix}"


@dataclass(frozen=True)
class SentimentAnnotation:
    anchor: int
    length: int
    polarity: int
    intensity: int
    context: int
    emotion: int
    reserved: int = 0

    def to_metablock(self) -> MetaBlock:
        has_span = self.length > 1
        span_value = (self.length - 1) if has_span else None
        return MetaBlock(has_span=has_span, span=span_value, polarity=self.polarity,
                         intensity=self.intensity, context=self.context,
                         emotion=self.emotion, reserved=self.reserved)

    def to_inline_block(self, marker_config: InlineMarkerConfig) -> InlineMetaBlock:
        block = self.to_metablock()
        span = TokenSpan(anchor=self.anchor, length=self.length)
        marker = marker_config.format_marker(block.to_hex())
        return InlineMetaBlock(block=block, span=span, marker=marker)


# --- src/vibe_x/inline_encoder.py ---
class InlineEncoder:
    def __init__(self, tokenizer: Tokenizer, marker_config: InlineMarkerConfig | None = None) -> None:
        self._tokenizer = tokenizer
        self._marker_config = marker_config or InlineMarkerConfig()

    def encode(self, text: str, annotations: Iterable[SentimentAnnotation]) -> str:
        tokens = self._tokenizer.tokenize(text)
        inline_blocks = [annotation.to_inline_block(self._marker_config) for annotation in annotations]
        for block in inline_blocks:
            if block.span.anchor >= len(tokens):
                raise MetaBlockEncodingError(
                    f"Anchor index {block.span.anchor} is out of bounds for {len(tokens)} tokens.")
        inline_blocks.sort(key=lambda b: b.span.anchor, reverse=True)
        tokens_copy: List[str] = tokens[:]
        for block in inline_blocks:
            idx = block.span.anchor
            tokens_copy[idx] = block.as_marker_payload() + tokens_copy[idx]
        return self._tokenizer.detokenize(tokens_copy)


# --- src/vibe_x/inline_decoder.py (DÜZELTİLMİŞ VE TAM SÜRÜM) ---
@dataclass
class DecodedBlock:
    """Çözümlenmiş MetaBlock ve temiz metindeki yerini tutar."""
    block: MetaBlock
    span: TokenSpan
    marker_hex: str  # Görselleştirme için


@dataclass
class DecodedInlineText:
    clean_text: str
    blocks: List[DecodedBlock]


class InlineDecoder:
    """
    Bu, VIBE-X'in metinsel bütünlüğünü (textual integrity)
    sağlamak için DÜZELTİLMİŞ ve çalışan Decoder'dır.
    """

    def __init__(self, tokenizer: Tokenizer, marker_config: InlineMarkerConfig | None = None) -> None:
        self._tokenizer = tokenizer
        self._marker_config = marker_config or InlineMarkerConfig()

    def decode(self, encoded_text: str) -> DecodedInlineText:
        clean_tokens = []
        extracted_blocks = []
        original_tokens = self._tokenizer.tokenize(encoded_text)

        # 'anchor_offset', PUA marker'larını çıkardıkça
        # 'clean_text' token listesindeki kaymayı takip eder.
        anchor_offset = 0

        for i, token in enumerate(original_tokens):
            if self._marker_config.prefix in token and self._marker_config.suffix in token:
                # 1. MARKER TESPİT EDİLDİ (Ayrıştırma)
                try:
                    start = token.find(self._marker_config.prefix)
                    end = token.find(self._marker_config.suffix, start)

                    if start == -1 or end == -1:
                        raise MetaBlockDecodingError(f"Hatalı marker yapısı: {token}")

                    # A. Hex Payload'u çıkar
                    hex_payload_start = start + len(self._marker_config.prefix)
                    hex_payload = token[hex_payload_start:end]

                    # B. Tam marker string'ini (temizlemek için)
                    full_marker = token[start: end + len(self._marker_config.suffix)]

                    # C. Temiz token'ı (varsa) ayır
                    clean_part = token.replace(full_marker, "")

                    # 2. ÇÖZÜMLEME (Decoding)
                    meta_block = MetaBlock.from_hex(hex_payload)

                    # 3. SPAN ve ANCHOR HESAPLAMA
                    # 'anchor' (çıpa), *temiz* token listesindeki indekstir.
                    current_anchor = i - anchor_offset

                    span_length = (meta_block.span or 0) + 1
                    span_obj = TokenSpan(anchor=current_anchor, length=span_length)

                    extracted_blocks.append(
                        DecodedBlock(
                            block=meta_block,
                            span=span_obj,
                            marker_hex=hex_payload  # Görselleştirme için sakla
                        )
                    )

                    if clean_part:
                        # "great" gibi temiz bir kısım varsa ekle
                        clean_tokens.append(clean_part)
                    else:
                        # Marker token'ı tamamen kapladı (örn: "\uE000...\uE001"),
                        # temiz token listesine bir öğe eklemedik.
                        # Gelecekteki anchor'lar 1 geri kaymalı.
                        anchor_offset += 1

                except Exception as e:
                    print(f"Uyarı: Hatalı VIBE-X marker çözümlenemedi: {e}")
                    clean_tokens.append(token)  # Hatalıysa olduğu gibi bırak
            else:
                # 4. NORMAL TOKEN (Marker içermiyor)
                clean_tokens.append(token)

        # 5. NİHAİ ÇIKTI
        final_clean_text = self._tokenizer.detokenize(clean_tokens)

        return DecodedInlineText(
            clean_text=final_clean_text,
            blocks=extracted_blocks
        )


# =========================================================================
# II. MASTER ANALYZER SİMÜLASYONU VE TEST FONKSİYONU
# =========================================================================

class MasterAnalyzer:
    """
    BERT/Master Analyzer'ın yerini alan simülasyon.
    Encoder'ın ihtiyaç duyduğu Annotation'ı üretir.
    """

    def analyze(self, text: str) -> List[SentimentAnnotation]:
        # Test 1: Pozitif ve Kısa Cümle
        if text == "The movie was great":
            return [
                SentimentAnnotation(
                    anchor=3, length=1, polarity=2, intensity=4, context=0, emotion=1, reserved=0
                )  # Polarity=Positive(2), Intensity=4, Emotion=Joy(1)
            ]
        # Test 2: Sarkazm Örneği
        if text == "Oh great, another meeting at 6 PM.":
            return [
                SentimentAnnotation(
                    anchor=1, length=1, polarity=3, intensity=3, context=1, emotion=4, reserved=0
                )  # Polarity=Ironic(3), Intensity=3, Context=Dynamic(1), Emotion=Disappointment(4)
            ]
        return []


# --- VIBE-X KOD ÇÖZÜM TABLOSU (Görsel Yardımcı Fonksiyon) ---

def get_vibe_x_interpretation(polarity, emotion, context):
    """VIBE-X kodlarını okunabilir etikete dönüştürür."""
    POLARITY_MAP = {0: "Neutral", 1: "Negative", 2: "Positive", 3: "Ironic"}
    EMOTION_MAP = {0: "Neutral/Indecision", 1: "Joy", 2: "Trust", 3: "Fear", 4: "Sadness", 5: "Disgust", 6: "Anger",
                   7: "Surprise"}
    return {
        "Polarity": POLARITY_MAP.get(polarity, "UNKNOWN"),
        "Emotion": EMOTION_MAP.get(emotion, "UNKNOWN"),
        "Context": "Dynamic/Contextual (Sarkazm/Bağlam)" if context == 1 else "Static/Literal (Gerçek)",
    }


def print_test_visualization(scenario_name, original_text, encoded_text, decoded_output, result_block):
    """
    Testin ara ve son çıktılarını görselleştirir.
    (DÜZELTİLMİŞ SÜRÜM)
    """
    # Protokol kodlarını çöz
    interpretation = get_vibe_x_interpretation(result_block.polarity, result_block.emotion, result_block.context)

    # --- DÜZELTİLMİŞ Hex Payload Çıkarma ---
    # Hex payload'u artık DecodedBlock içinden alıyoruz
    hex_payload = decoded_output.blocks[0].marker_hex

    print("\n" + "=" * 60)
    print(f"| {scenario_name.upper()} - VIBE-X PROTOKOL GÖRSELLEŞTİRMESİ")
    print("=" * 60)

    # 1. ENCODING SUCCESSFUL
    print("\n🟢 ADIM 1: ENCODING SUCCESSFUL (Kodlama Başarılı)")
    print(f"   -> Orijinal Metin (Girdi): '{original_text}'")
    print(f"   -> Gömülü Metin (Encoder Çıktısı): '{encoded_text}'")
    print(f"   -> Gömülen Hex Payload (14-bit SPICE-R): {hex_payload}")

    # 2. DECODING SUCCESSFUL
    print("\n✅ ADIM 2: DECODING SUCCESSFUL (Kod Çözme Başarılı)")
    print(f"   -> Analiz Edilen Girdi: '{encoded_text}'")

    # 3. ÇÖZÜMLENEN METADATA
    print("\n   --- Çözümlenen SPICE-R Meta Verileri ---")
    print(f"   [Çözümlenen Temiz Metin] ........: '{decoded_output.clean_text}'")
    print(f"   [Polarity] .....................: {result_block.polarity} ({interpretation['Polarity']})")
    print(f"   [Intensity] ....................: {result_block.intensity} (7 üzerinden)")
    print(f"   [Emotion Class] ................: {result_block.emotion} ({interpretation['Emotion']})")
    print(f"   [Context Flag] .................: {result_block.context} ({interpretation['Context']})")
    print("\n" + "=" * 60)


# =========================================================================
# III. GÜNCELLENMİŞ TEST AKIŞI (Görselleştirmeyi Çağıran)
# =========================================================================

def test_full_vibe_x_round_trip():
    """
    Master Analyzer -> Encoder -> Decoder tam akışını test eder.
    VIBE-X formatının bütünlüğünü ve doğru kodlanıp çözüldüğünü kanıtlar.
    """
    print("\n--- VIBE-X TAM ENTEGRASYON TESTİ BAŞLIYOR ---")

    # 1. Test Ortamını Hazırla
    tokenizer = Tokenizer()
    analyzer = MasterAnalyzer()
    encoder = InlineEncoder(tokenizer)
    decoder = InlineDecoder(tokenizer)  # <-- Düzeltilmiş Decoder'ı kullanıyor

    # TEST SENARYOSU 1: Basit Pozitif Duygu
    text_1 = "The movie was great"
    annotations_1 = analyzer.analyze(text_1)
    encoded_1 = encoder.encode(text_1, annotations_1)
    decoded_1 = decoder.decode(encoded_1)

    # KANITLAMA (Doğrulama)
    assert decoded_1.clean_text.strip() == text_1  # Temiz metin sağlam kalmalı
    assert len(decoded_1.blocks) == 1
    expected_1 = annotations_1[0]
    result_1 = decoded_1.blocks[0].block
    assert result_1.polarity == expected_1.polarity and result_1.polarity == 2
    assert result_1.intensity == expected_1.intensity and result_1.intensity == 4
    assert result_1.emotion == expected_1.emotion and result_1.emotion == 1

    # --- İSTEDİĞİN GÖRSEL ÇIKTI BURADA ---
    print_test_visualization(
        "Senaryo 1: Basit Pozitif Duygu",
        text_1, encoded_1, decoded_1, result_1
    )

    # TEST SENARYOSU 2: Sarkazm / Bağlamsal (Dynamic) Duygu
    text_2 = "Oh great, another meeting at 6 PM."
    annotations_2 = analyzer.analyze(text_2)
    encoded_2 = encoder.encode(text_2, annotations_2)
    decoded_2 = decoder.decode(encoded_2)

    # KANITLAMA (Doğrulama)
    assert decoded_2.clean_text.strip() == text_2  # Temiz metin sağlam kalmalı
    assert len(decoded_2.blocks) == 1
    expected_2 = annotations_2[0]
    result_2 = decoded_2.blocks[0].block
    assert result_2.polarity == expected_2.polarity and result_2.polarity == 3  # Ironic
    assert result_2.context == expected_2.context and result_2.context == 1  # Dynamic
    assert result_2.emotion == expected_2.emotion and result_2.emotion == 4  # Disappointment

    # --- İSTEDİĞİN GÖRSEL ÇIKTI BURADA ---
    print_test_visualization(
        "Senaryo 2: Sarkazm Örneği",
        text_2, encoded_2, decoded_2, result_2
    )

    print("\n--- TÜM ENTEGRASYON TESTLERİ BAŞARIYLA TAMAMLANDI! ---")


if __name__ == '__main__':
    test_full_vibe_x_round_trip()
