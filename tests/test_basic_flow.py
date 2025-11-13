from vibex import InlineEncoder, InlineDecoder, SentimentAnnotation, Tokenizer


def test_basic_encode_decode_flow():
    text = "The movie was great"

    encoder = InlineEncoder(Tokenizer())
    decoder = InlineDecoder(Tokenizer())

    annotation = SentimentAnnotation(
        anchor=3,  # "great"
        length=1,
        polarity=2,
        intensity=4,
        context=0,
        emotion=1
    )

    encoded = encoder.encode(text, [annotation])
    decoded = decoder.decode(encoded)

    # Clean text must match original
    assert decoded.clean_text == text

    # At least one MetaBlock extracted
    assert len(decoded.blocks) == 1

    block = decoded.blocks[0].block

    # Metadata values must match
    assert block.polarity == 2
    assert block.intensity == 4
    assert block.context == 0
    assert block.emotion == 1
