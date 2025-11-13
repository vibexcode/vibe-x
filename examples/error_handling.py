from vibex import InlineEncoder, SentimentAnnotation, Tokenizer, MetaBlockEncodingError

text = "This is a short text"

encoder = InlineEncoder(Tokenizer())

# Intentional mistake: anchor index out of token range
bad_annotation = SentimentAnnotation(
    anchor=50,   # invalid, out of range
    length=1,
    polarity=1,
    intensity=3,
    context=0,
    emotion=2
)

try:
    encoder.encode(text, [bad_annotation])
except MetaBlockEncodingError as e:
    print("Caught encoding error:", e)
