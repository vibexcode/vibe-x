"""
Real-World Example: Chat Moderation System

This example demonstrates using VIBE-X for real-time chat moderation,
detecting toxicity, harassment, and urgent situations.
"""

from vibex import InlineEncoder, InlineDecoder, SentimentAnnotation, Tokenizer
import time


def simulate_chat_moderation():
    """
    Live chat moderation system:
    1. Analyze messages with toxicity/sentiment model (once)
    2. Encode with VIBE-X
    3. Enable instant moderation decisions
    4. Flag urgent situations (self-harm, threats, etc.)
    """

    encoder = InlineEncoder(Tokenizer())
    decoder = InlineDecoder(Tokenizer())

    # Simulated chat messages
    chat_messages = [
        {
            "id": 1,
            "user": "Player1",
            "text": "Great game everyone! Really enjoyed that match!",
            "timestamp": "14:30:01",
        },
        {
            "id": 2,
            "user": "ToxicUser",
            "text": "You are absolutely terrible at this game. Just quit.",
            "timestamp": "14:30:15",
        },
        {
            "id": 3,
            "user": "Helper",
            "text": "Anyone need tips for the next level?",
            "timestamp": "14:30:22",
        },
        {
            "id": 4,
            "user": "AngryPlayer",
            "text": "This game is rigged! I hate this stupid broken system!",
            "timestamp": "14:30:45",
        },
        {
            "id": 5,
            "user": "Newbie",
            "text": "I'm really struggling with this. Feeling pretty hopeless.",
            "timestamp": "14:31:03",
        },
        {
            "id": 6,
            "user": "Harasser",
            "text": "Wow you suck so bad it's embarrassing. Pathetic performance.",
            "timestamp": "14:31:20",
        },
        {
            "id": 7,
            "user": "Supporter",
            "text": "Don't worry Newbie, we all started somewhere! Keep trying!",
            "timestamp": "14:31:35",
        },
        {
            "id": 8,
            "user": "SarcasticGuy",
            "text": "Oh yeah, that was a brilliant move. Absolutely genius.",
            "timestamp": "14:31:50",
        },
        {
            "id": 9,
            "user": "UrgentUser",
            "text": "URGENT: Someone please help! Account security breach!",
            "timestamp": "14:32:05",
        },
    ]

    # Sentiment/toxicity analysis results
    # In production: output from toxicity detection model (Perspective API, custom BERT, etc.)
    moderation_annotations = [
        # Message 1: Positive, joyful
        [SentimentAnnotation(anchor=0, length=2, polarity=2, intensity=6, context=0, emotion=1)],
        # Message 2: Toxic, negative, disgust
        [SentimentAnnotation(anchor=2, length=2, polarity=1, intensity=7, context=0, emotion=6)],
        # Message 3: Helpful, neutral-positive
        [SentimentAnnotation(anchor=0, length=2, polarity=2, intensity=3, context=0, emotion=2)],
        # Message 4: Angry, intense
        [SentimentAnnotation(anchor=4, length=4, polarity=1, intensity=7, context=0, emotion=7)],
        # Message 5: Concerning, sadness (potential mental health flag)
        [
            SentimentAnnotation(
                anchor=5, length=2, polarity=1, intensity=6, context=0, emotion=5, emergency=True
            )
        ],
        # Message 6: Harassment, very toxic
        [SentimentAnnotation(anchor=2, length=3, polarity=1, intensity=7, context=0, emotion=6)],
        # Message 7: Supportive, positive
        [SentimentAnnotation(anchor=0, length=3, polarity=2, intensity=5, context=0, emotion=2)],
        # Message 8: Sarcastic
        [SentimentAnnotation(anchor=4, length=3, polarity=3, intensity=5, context=1, emotion=7)],
        # Message 9: Emergency
        [
            SentimentAnnotation(
                anchor=0, length=1, polarity=1, intensity=7, context=0, emotion=3, emergency=True
            )
        ],
    ]

    print("=" * 70)
    print("LIVE CHAT MODERATION SYSTEM - VIBE-X DEMO")
    print("=" * 70)
    print("\n🎮 Channel: #general-chat")
    print(f"📊 Monitoring {len(chat_messages)} messages\n")

    # Encode messages (happens in real-time as messages arrive)
    print("=" * 70)
    print("INCOMING MESSAGES (encoded with VIBE-X)")
    print("=" * 70)

    encoded_messages = []
    for msg, annotations in zip(chat_messages, moderation_annotations):
        encoded = encoder.encode(msg["text"], annotations)
        encoded_messages.append({"message": msg, "encoded": encoded})

        # Display message
        print(f"\n[{msg['timestamp']}] {msg['user']}:")
        print(f"  {msg['text']}")

        # Instant moderation check
        decoded = decoder.decode(encoded)

        # Check for emergency
        if any(block.block.emergency for block in decoded.blocks):
            print("  🚨 [AUTO-FLAG: EMERGENCY - requires immediate review]")

        # Check for high toxicity
        elif any(
            block.block.polarity == 1 and block.block.intensity >= 7 for block in decoded.blocks
        ):
            print("  ⚠️  [AUTO-FLAG: High toxicity detected]")

        # Check for sarcasm/potential harassment
        elif any(block.block.polarity == 3 for block in decoded.blocks):
            print("  😏 [AUTO-FLAG: Sarcasm detected - review context]")

        time.sleep(0.1)  # Simulate real-time

    # Moderation Dashboard
    print("\n" + "=" * 70)
    print("MODERATION DASHBOARD")
    print("=" * 70)

    # Emergency messages
    print("\n🚨 EMERGENCY MESSAGES (immediate action required):")
    print("-" * 70)
    emergency_found = False
    for item in encoded_messages:
        decoded = decoder.decode(item["encoded"])
        if any(block.block.emergency for block in decoded.blocks):
            emergency_found = True
            msg = item["message"]
            print(f"[{msg['timestamp']}] {msg['user']}: {msg['text']}")

            # Suggested actions
            blocks = decoded.blocks
            emotions = [block.block.emotion for block in blocks]
            if 5 in emotions:  # Sadness
                print("  → Suggested action: Alert mental health support team")
            elif 3 in emotions:  # Fear
                print("  → Suggested action: Security breach protocol")
    if not emergency_found:
        print("  No emergency messages detected.")

    # Toxic messages
    print("\n⚠️  TOXIC MESSAGES (moderation review):")
    print("-" * 70)
    toxic_count = 0
    for item in encoded_messages:
        decoded = decoder.decode(item["encoded"])
        for block in decoded.blocks:
            if block.block.polarity == 1 and block.block.intensity >= 6:
                toxic_count += 1
                msg = item["message"]
                print(f"[{msg['timestamp']}] {msg['user']}: {msg['text']}")
                print(f"  Toxicity: {block.block.intensity}/7")
                print(
                    f"  Emotion: {['Neutral', 'Joy', 'Trust', 'Fear', 'Surprise', 'Sadness', 'Disgust', 'Anger'][block.block.emotion]}"
                )

                # Auto-moderation suggestion
                if block.block.intensity == 7:
                    print("  → Suggested action: AUTO-TIMEOUT (1 hour)")
                else:
                    print("  → Suggested action: Warning")
                break

    # Positive interactions
    print("\n😊 POSITIVE INTERACTIONS (potential highlights):")
    print("-" * 70)
    for item in encoded_messages:
        decoded = decoder.decode(item["encoded"])
        if any(
            block.block.polarity == 2 and block.block.intensity >= 5 for block in decoded.blocks
        ):
            msg = item["message"]
            print(f"[{msg['timestamp']}] {msg['user']}: {msg['text']}")

    # Statistics
    print("\n" + "=" * 70)
    print("MODERATION STATISTICS")
    print("=" * 70)

    total = len(encoded_messages)
    emergency = sum(
        1
        for item in encoded_messages
        if any(block.block.emergency for block in decoder.decode(item["encoded"]).blocks)
    )
    toxic = toxic_count
    positive = sum(
        1
        for item in encoded_messages
        if any(
            block.block.polarity == 2 and block.block.intensity >= 5
            for block in decoder.decode(item["encoded"]).blocks
        )
    )
    sarcastic = sum(
        1
        for item in encoded_messages
        if any(block.block.polarity == 3 for block in decoder.decode(item["encoded"]).blocks)
    )

    print(f"\nTotal Messages: {total}")
    print(f"🚨 Emergency: {emergency} ({emergency/total*100:.1f}%)")
    print(f"⚠️  Toxic: {toxic} ({toxic/total*100:.1f}%)")
    print(f"😊 Positive: {positive} ({positive/total*100:.1f}%)")
    print(f"😏 Sarcastic: {sarcastic} ({sarcastic/total*100:.1f}%)")

    print(f"\n⚡ Performance Benefits:")
    print(f"  • Each message analyzed ONCE with AI model")
    print(f"  • Metadata stored as 4-byte VIBE-X code")
    print(f"  • Instant moderation decisions (< 1 microsecond)")
    print(f"  • Can re-query message history millions of times at zero cost")
    print(f"  • Perfect for real-time chat with 1000s of messages/second")

    print(f"\n📊 Scalability:")
    print(f"  At 1M messages/day:")
    print(f"    VIBE-X metadata: ~4 MB")
    print(f"    JSON equivalent: ~150 MB")
    print(f"    Savings: 146 MB/day = 53 GB/year")


if __name__ == "__main__":
    simulate_chat_moderation()
