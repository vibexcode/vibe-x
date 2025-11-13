from vibex import InlineEncoder, SentimentAnnotation, Tokenizer

text = "The movie was absolutely amazing"

encoder = InlineEncoder(Tokenizer())

annotation = SentimentAnnotation(
    anchor=3,
    length=2,
    polarity=2,
    intensity=5,
    context=0,
    emotion=1
)

encoded = encoder.encode(text, [annotation])
print("Encoded:", encoded)
