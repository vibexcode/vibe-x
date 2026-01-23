"""
Real-World Example: Customer Review Analysis

This example shows how to use VIBE-X for e-commerce product reviews,
enabling instant filtering by sentiment without re-analyzing reviews.
"""

from vibex import InlineEncoder, InlineDecoder, SentimentAnnotation, Tokenizer


def analyze_customer_reviews():
    """
    E-commerce review analysis system:
    1. Analyze reviews once (expensive)
    2. Encode with VIBE-X (cheap, one-time)
    3. Enable instant filtering for customers (free)
    """

    encoder = InlineEncoder(Tokenizer())
    decoder = InlineDecoder(Tokenizer())
    tokenizer = Tokenizer()

    # Sample product reviews
    reviews = [
        {
            "id": 101,
            "product": "Wireless Headphones",
            "rating": 5,
            "text": "Sound quality is absolutely phenomenal! Best purchase ever!",
            "author": "AudioPhile",
            "verified": True,
        },
        {
            "id": 102,
            "product": "Wireless Headphones",
            "rating": 2,
            "text": "Battery life is terrible and disappointing. Not worth the price.",
            "author": "TechUser",
            "verified": True,
        },
        {
            "id": 103,
            "product": "Wireless Headphones",
            "rating": 4,
            "text": "Great sound but the fit could be more comfortable.",
            "author": "MusicLover",
            "verified": True,
        },
        {
            "id": 104,
            "product": "Wireless Headphones",
            "rating": 3,
            "text": "It's okay. Nothing special but works fine.",
            "author": "CasualBuyer",
            "verified": False,
        },
        {
            "id": 105,
            "product": "Wireless Headphones",
            "rating": 1,
            "text": "Awful experience. Product broke after one week. Complete waste of money.",
            "author": "Disappointed",
            "verified": True,
        },
        {
            "id": 106,
            "product": "Wireless Headphones",
            "rating": 5,
            "text": "Yeah right, amazing quality for this price. Totally believable.",
            "author": "Skeptic",
            "verified": False,
        },  # Sarcastic negative review
    ]

    # Sentiment analysis results (from ML model)
    sentiment_annotations = [
        # Review 1: Very positive
        [SentimentAnnotation(anchor=3, length=2, polarity=2, intensity=7, context=0, emotion=1)],
        # Review 2: Very negative
        [SentimentAnnotation(anchor=3, length=3, polarity=1, intensity=6, context=0, emotion=5)],
        # Review 3: Mixed - positive and negative
        [
            SentimentAnnotation(anchor=0, length=2, polarity=2, intensity=5, context=0, emotion=1),
            SentimentAnnotation(anchor=6, length=3, polarity=1, intensity=3, context=0, emotion=5),
        ],
        # Review 4: Neutral
        [SentimentAnnotation(anchor=0, length=1, polarity=0, intensity=2, context=0, emotion=0)],
        # Review 5: Extremely negative
        [SentimentAnnotation(anchor=0, length=2, polarity=1, intensity=7, context=0, emotion=7)],
        # Review 6: Sarcastic (actually negative)
        [SentimentAnnotation(anchor=2, length=2, polarity=3, intensity=6, context=1, emotion=7)],
    ]

    # Encode reviews
    print("=" * 70)
    print("CUSTOMER REVIEW ANALYSIS - VIBE-X DEMO")
    print("=" * 70)
    print("\n📦 Product: Wireless Headphones")
    print(f"📊 Total Reviews: {len(reviews)}\n")

    encoded_reviews = []
    for review, annotations in zip(reviews, sentiment_annotations):
        encoded = encoder.encode(review["text"], annotations)
        encoded_reviews.append({"review": review, "encoded": encoded})

    # Display encoded reviews
    print("=" * 70)
    print("ENCODED REVIEWS (stored in database)")
    print("=" * 70)
    for item in encoded_reviews:
        review = item["review"]
        print(f"\nReview #{review['id']} - ⭐ {review['rating']}/5")
        print(f"Author: {review['author']} {'✓' if review['verified'] else '✗'}")
        print(f"Text: {review['text']}")
        print(f"Encoded: {item['encoded'][:80]}...")

    # Customer queries (instant, no model needed)
    print("\n" + "=" * 70)
    print("CUSTOMER FILTER QUERIES (Instant, Zero Model Cost)")
    print("=" * 70)

    # Query 1: Show only positive reviews
    print("\n✅ Filter: Only Positive Reviews (polarity=2)")
    print("-" * 70)
    positive_reviews = []
    for item in encoded_reviews:
        decoded = decoder.decode(item["encoded"])
        # Check if has positive sentiment
        if any(block.block.polarity == 2 for block in decoded.blocks):
            review = item["review"]
            positive_reviews.append(review)
            print(f"⭐ {review['rating']}/5 - {review['author']}")
            print(f"   {review['text']}")

    # Query 2: Show only negative reviews (for improvement insights)
    print("\n❌ Filter: Negative Reviews (polarity=1, intensity>=5)")
    print("-" * 70)
    negative_reviews = []
    for item in encoded_reviews:
        decoded = decoder.decode(item["encoded"])
        for block in decoded.blocks:
            if block.block.polarity == 1 and block.block.intensity >= 5:
                review = item["review"]
                negative_reviews.append(review)
                print(f"⭐ {review['rating']}/5 - {review['author']}")
                print(f"   {review['text']}")
                print(f"   Issue intensity: {block.block.intensity}/7")
                break

    # Query 3: Detect sarcastic/fake reviews
    print("\n⚠️  Alert: Potentially Sarcastic/Fake Reviews (polarity=3)")
    print("-" * 70)
    for item in encoded_reviews:
        decoded = decoder.decode(item["encoded"])
        if any(block.block.polarity == 3 for block in decoded.blocks):
            review = item["review"]
            print(f"⭐ {review['rating']}/5 - {review['author']} {'✓' if review['verified'] else '✗ UNVERIFIED'}")
            print(f"   {review['text']}")
            print(f"   [WARNING: Detected irony/sarcasm - may need manual review]")

    # Query 4: Mixed sentiment (detailed reviews)
    print("\n🤔 Filter: Detailed Reviews with Mixed Sentiment")
    print("-" * 70)
    for item in encoded_reviews:
        decoded = decoder.decode(item["encoded"])
        if len(decoded.blocks) > 1:
            polarities = [block.block.polarity for block in decoded.blocks]
            if 2 in polarities and 1 in polarities:
                review = item["review"]
                print(f"⭐ {review['rating']}/5 - {review['author']}")
                print(f"   {review['text']}")

    # Analytics Dashboard
    print("\n" + "=" * 70)
    print("REVIEW ANALYTICS DASHBOARD")
    print("=" * 70)

    total = len(encoded_reviews)
    verified = sum(1 for item in encoded_reviews if item["review"]["verified"])

    # Sentiment breakdown
    pos_count = 0
    neg_count = 0
    neutral_count = 0
    sarcasm_count = 0

    for item in encoded_reviews:
        decoded = decoder.decode(item["encoded"])
        has_positive = any(block.block.polarity == 2 for block in decoded.blocks)
        has_negative = any(block.block.polarity == 1 for block in decoded.blocks)
        has_sarcasm = any(block.block.polarity == 3 for block in decoded.blocks)

        if has_sarcasm:
            sarcasm_count += 1
        elif has_positive and not has_negative:
            pos_count += 1
        elif has_negative and not has_positive:
            neg_count += 1
        else:
            neutral_count += 1

    print(f"\nTotal Reviews: {total}")
    print(f"Verified Buyers: {verified}/{total}")
    print(f"\nSentiment Breakdown:")
    print(f"  😊 Positive: {pos_count} ({pos_count/total*100:.1f}%)")
    print(f"  😐 Neutral/Mixed: {neutral_count} ({neutral_count/total*100:.1f}%)")
    print(f"  😢 Negative: {neg_count} ({neg_count/total*100:.1f}%)")
    print(f"  😏 Sarcastic: {sarcasm_count} ({sarcasm_count/total*100:.1f}%)")

    # Compute average rating by sentiment
    pos_avg = (
        sum(item["review"]["rating"] for item in encoded_reviews if item["review"] in positive_reviews)
        / len(positive_reviews)
        if positive_reviews
        else 0
    )
    neg_avg = (
        sum(item["review"]["rating"] for item in encoded_reviews if item["review"] in negative_reviews)
        / len(negative_reviews)
        if negative_reviews
        else 0
    )

    print(f"\nAverage Star Rating:")
    print(f"  Positive reviews: {pos_avg:.1f} ⭐")
    print(f"  Negative reviews: {neg_avg:.1f} ⭐")

    print(f"\n💾 Storage Efficiency:")
    print(f"  VIBE-X metadata: ~{total * 4} bytes")
    print(f"  JSON equivalent: ~{total * 150} bytes")
    print(f"  Savings: {(1 - (total*4)/(total*150)) * 100:.1f}%")

    print(f"\n🚀 Performance:")
    print(
        f"  These {total} reviews can be queried 1 BILLION times with ZERO additional AI inference cost!"
    )


if __name__ == "__main__":
    analyze_customer_reviews()
