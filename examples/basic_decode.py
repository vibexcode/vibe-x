from vibex import InlineDecoder, Tokenizer

# Paste here the encoded text you got from basic_encode.py,
# or import it dynamically if running both scripts together.

encoded_text = input("Paste encoded text: ")

decoder = InlineDecoder(Tokenizer())
decoded = decoder.decode(encoded_text)

print("Clean text:", decoded.clean_text)
print("Tokens:", decoded.clean_tokens)

print("\nDecoded MetaBlocks:")
for block in decoded.blocks:
    print(" - HEX:", block.block.to_hex())
    print("   Span:", block.span)
    print("   Polarity:", block.block.polarity)
    print("   Intensity:", block.block.intensity)
    print("   Emotion:", block.block.emotion)
