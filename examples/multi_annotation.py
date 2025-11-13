from vibex import InlineEncoder, SentimentAnnotation, Tokenizer

text = "I loved the performance but the ending felt rushed"

encoder = InlineEncoder(Tokenizer())

annotations = [
    SentimentAnnotation(
        anchor=1,      # "loved"
        length=1,
        polarity=2,    # positive
        intensity=6,
        context=0,
        emotion=1
    ),
    SentimentAnnotation(
        anchor=7,      # "felt"
        length=2,      # "felt rushed"
        polarity=1,    # negative
        intensity=5,
        context=1,     # dynamic/context-dependent
        emotion=4
    ),
]

encoded = encoder.encode(text, annotations)
print("Encoded text with multiple annotations:")
print(encoded)
