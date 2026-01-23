"""
Real-World Example: Social Media Post Analysis

This example demonstrates how to use VIBE-X for analyzing social media posts,
detecting emotions, sarcasm, and emergency situations.
"""

from vibex import InlineEncoder, InlineDecoder, SentimentAnnotation, Tokenizer


def analyze_social_media_posts():
    """
    Simulate a social media monitoring system that:
    1. Analyzes posts once with sentiment model
    2. Encodes results with VIBE-X
    3. Enables instant queries without re-running the model
    """

    encoder = InlineEncoder(Tokenizer())
    decoder = InlineDecoder(Tokenizer())
    tokenizer = Tokenizer()

    # Sample social media posts (in real scenario, these would come from API)
    posts = [
        {
            "id": 1,
            "user": "@happyuser",
            "text": "Just got my dream job! Beyond excited!",
            "timestamp": "2025-01-22 10:30",
        },
        {
            "id": 2,
            "user": "@frustrated",
            "text": "This customer service is absolutely terrible and useless.",
            "timestamp": "2025-01-22 11:15",
        },
        {
            "id": 3,
            "user": "@casual",
            "text": "Going to grab some coffee.",
            "timestamp": "2025-01-22 11:45",
        },
        {
            "id": 4,
            "user": "@sarcastic",
            "text": "Oh great, another software update. Just what I needed.",
            "timestamp": "2025-01-22 12:00",
        },
        {
            "id": 5,
            "user": "@urgenthelp",
            "text": "URGENT: My account was hacked! Need immediate assistance!",
            "timestamp": "2025-01-22 12:30",
        },
        {
            "id": 6,
            "user": "@reviewer",
            "text": "The product quality is amazing but shipping was slow.",
            "timestamp": "2025-01-22 13:00",
        },
    ]

    # Simulate sentiment analysis results from ML model
    # In production, this would be output from BERT, RoBERTa, etc.
    sentiment_results = [
        # Post 1: Very positive, joyful
        [SentimentAnnotation(anchor=2, length=3, polarity=2, intensity=7, context=0, emotion=1)],
        # Post 2: Very negative, disgust
        [SentimentAnnotation(anchor=3, length=3, polarity=1, intensity=6, context=0, emotion=6)],
        # Post 3: Neutral
        [SentimentAnnotation(anchor=0, length=1, polarity=0, intensity=1, context=0, emotion=0)],
        # Post 4: Ironic/sarcastic, anger
        [SentimentAnnotation(anchor=1, length=1, polarity=3, intensity=5, context=1, emotion=7)],
        # Post 5: Emergency, fear
        [
            SentimentAnnotation(
                anchor=0, length=1, polarity=1, intensity=7, context=0, emotion=3, reserved=1
            )
        ],
        # Post 6: Mixed sentiment - positive and negative
        [
            SentimentAnnotation(anchor=3, length=2, polarity=2, intensity=6, context=0, emotion=1),
            SentimentAnnotation(anchor=6, length=2, polarity=1, intensity=4, context=0, emotion=5),
        ],
    ]

    # Step 1: Encode all posts (ONE-TIME operation)
    print("=" * 70)
    print("STEP 1: ENCODING POSTS (One-time analysis)")
    print("=" * 70)

    encoded_posts = []
    for post, annotations in zip(posts, sentiment_results):
        encoded = encoder.encode(post["text"], annotations)
        encoded_posts.append({"post": post, "encoded": encoded})
        print(f"\n[{post['timestamp']}] @{post['user']}")
        print(f"Original: {post['text']}")
        print(f"Encoded:  {encoded}")

    # Step 2: Query examples (ZERO-COST operations)
    print("\n" + "=" * 70)
    print("STEP 2: INSTANT QUERIES (No model inference needed!)")
    print("=" * 70)

    # Query 1: Emergency detection
    print("\n🚨 EMERGENCY POSTS (e.g., for priority routing):")
    print("-" * 70)
    for item in encoded_posts:
        decoded = decoder.decode(item["encoded"])
        if any(block.block.reserved for block in decoded.blocks):
            post = item["post"]
            print(f"[URGENT] @{post['user']}: {post['text']}")
            print(f"         Timestamp: {post['timestamp']}")

    # Query 2: Highly negative posts (customer service escalation)
    print("\n😡 HIGHLY NEGATIVE POSTS (intensity >= 5):")
    print("-" * 70)
    for item in encoded_posts:
        decoded = decoder.decode(item["encoded"])
        for block in decoded.blocks:
            if block.block.polarity == 1 and block.block.intensity >= 5:
                post = item["post"]
                print(f"@{post['user']}: {post['text']}")
                print(f"  Intensity: {block.block.intensity}/7")
                break

    # Query 3: Sarcasm detection
    print("\n😏 SARCASTIC/IRONIC POSTS (may need special handling):")
    print("-" * 70)
    for item in encoded_posts:
        decoded = decoder.decode(item["encoded"])
        if any(block.block.polarity == 3 for block in decoded.blocks):
            post = item["post"]
            print(f"@{post['user']}: {post['text']}")

    # Query 4: Positive engagement opportunities
    print("\n😊 JOYFUL POSTS (engagement opportunities):")
    print("-" * 70)
    for item in encoded_posts:
        decoded = decoder.decode(item["encoded"])
        if any(block.block.emotion == 1 and block.block.intensity >= 6 for block in decoded.blocks):
            post = item["post"]
            print(f"@{post['user']}: {post['text']}")

    # Query 5: Mixed sentiment (complex cases)
    print("\n🤔 MIXED SENTIMENT POSTS (may need review):")
    print("-" * 70)
    for item in encoded_posts:
        decoded = decoder.decode(item["encoded"])
        if len(decoded.blocks) > 1:
            polarities = [block.block.polarity for block in decoded.blocks]
            if 2 in polarities and 1 in polarities:  # Has both positive and negative
                post = item["post"]
                print(f"@{post['user']}: {post['text']}")
                print(f"  Contains both positive and negative sentiment")

    # Statistics
    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)

    total_posts = len(encoded_posts)
    emergency_count = sum(
        1
        for item in encoded_posts
        if any(block.block.reserved for block in decoder.decode(item["encoded"]).blocks)
    )
    negative_count = sum(
        1
        for item in encoded_posts
        if any(
            block.block.polarity == 1 and block.block.intensity >= 5
            for block in decoder.decode(item["encoded"]).blocks
        )
    )

    print(f"Total posts analyzed: {total_posts}")
    print(f"Emergency posts: {emergency_count}")
    print(f"Highly negative posts: {negative_count}")
    print(f"Average metadata size: ~4 bytes per annotation (vs ~100+ bytes for JSON)")
    print(
        f"\nWith VIBE-X: Query these {total_posts} posts 1M times with ZERO additional model inference!"
    )


if __name__ == "__main__":
    analyze_social_media_posts()
