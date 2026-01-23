"""
VIBE-X Interactive Demo
A Streamlit-based interactive demonstration of the VIBE-X protocol
"""

import streamlit as st
from vibex import InlineEncoder, InlineDecoder, SentimentAnnotation, Tokenizer

# Page configuration
st.set_page_config(
    page_title="VIBE-X Protocol Demo",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    .metadata-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎭 VIBE-X Protocol Demo</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Vector-Integrated Binary Extension — "Encode Once, Query Infinitely."</div>', unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About VIBE-X")
    st.markdown("""
    VIBE-X is a lightweight binary encoding protocol that attaches sentiment and emotional
    metadata directly to UTF-8 text streams.

    **Key Features:**
    - 14-bit compact MetaBlock encoding
    - Polarity, Intensity, Emotion tracking
    - Context-aware (irony/sarcasm)
    - Zero-cost emotional queries
    - 99%+ storage savings vs JSON
    """)

    st.divider()

    st.header("📚 Quick Guide")
    st.markdown("""
    1. **Enter text** in the text area
    2. **Select tokens** to annotate
    3. **Configure sentiment** parameters
    4. **Encode** and see the result
    5. **Decode** to verify metadata
    """)

    st.divider()

    st.markdown("""
    **Emotion Classes:**
    - 0: Neutral
    - 1: Joy
    - 2: Trust
    - 3: Fear
    - 4: Surprise
    - 5: Sadness
    - 6: Disgust
    - 7: Anger
    """)

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🔐 Encode", "🔓 Decode", "📊 Batch Analysis", "🎓 Tutorial"])

with tab1:
    st.header("Encode Text with Emotional Metadata")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Text input
        default_text = "The movie was absolutely amazing!"
        text_input = st.text_area(
            "Enter your text:",
            value=default_text,
            height=100,
            help="Enter any text you want to annotate with emotional metadata"
        )

        # Tokenize and display
        if text_input:
            tokenizer = Tokenizer()
            tokens = tokenizer.tokenize(text_input)
            st.info(f"**Tokens ({len(tokens)}):** {' | '.join([f'{i}:{t}' for i, t in enumerate(tokens)])}")

    with col2:
        st.subheader("Annotation Settings")

        # Annotation controls
        anchor = st.number_input(
            "Token Index (anchor)",
            min_value=0,
            max_value=max(0, len(tokens)-1) if text_input else 0,
            value=min(3, max(0, len(tokens)-1)) if text_input else 0,
            help="Starting token index for the annotation"
        )

        length = st.number_input(
            "Span Length",
            min_value=1,
            max_value=7,
            value=2,
            help="Number of tokens to span (1-7)"
        )

        st.divider()

        # Polarity
        polarity_map = {
            "Neutral": 0,
            "Negative": 1,
            "Positive": 2,
            "Ironic/Sarcastic": 3
        }
        polarity_label = st.select_slider(
            "Polarity",
            options=list(polarity_map.keys()),
            value="Positive",
            help="Emotional polarity of the span"
        )
        polarity = polarity_map[polarity_label]

        # Intensity
        intensity = st.slider(
            "Intensity",
            min_value=0,
            max_value=7,
            value=5,
            help="Emotional intensity (0=weak, 7=very strong)"
        )

        # Context
        context_map = {
            "Literal/Static": 0,
            "Dynamic/Context-dependent": 1
        }
        context_label = st.radio(
            "Context",
            options=list(context_map.keys()),
            help="Whether meaning is literal or context-dependent"
        )
        context = context_map[context_label]

        # Emotion
        emotion = st.selectbox(
            "Emotion Class",
            options=list(range(8)),
            format_func=lambda x: ["Neutral", "Joy", "Trust", "Fear", "Surprise", "Sadness", "Disgust", "Anger"][x],
            index=1,
            help="Primary emotion category"
        )

        # Emergency flag
        emergency = st.checkbox(
            "Emergency Flag",
            value=False,
            help="Mark as urgent/critical"
        )

    # Encode button
    if st.button("🔐 Encode Text", type="primary", use_container_width=True):
        try:
            encoder = InlineEncoder(Tokenizer())

            annotation = SentimentAnnotation(
                anchor=anchor,
                length=length,
                polarity=polarity,
                intensity=intensity,
                context=context,
                emotion=emotion,
                emergency=emergency
            )

            encoded_text = encoder.encode(text_input, [annotation])

            st.success("✅ Encoding successful!")

            # Display encoded text
            st.subheader("Encoded Text")
            st.code(encoded_text, language=None)

            # Show metadata
            st.subheader("Annotation Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Token Span", f"{anchor} → {anchor + length - 1}")
                st.metric("Polarity", polarity_label)
            with col2:
                st.metric("Intensity", f"{intensity}/7")
                st.metric("Context", context_label.split('/')[0])
            with col3:
                st.metric("Emotion", ["Neutral", "Joy", "Trust", "Fear", "Surprise", "Sadness", "Disgust", "Anger"][emotion])
                st.metric("Emergency", "Yes" if emergency else "No")

            # Store in session state for decoding tab
            st.session_state['encoded_text'] = encoded_text

        except Exception as e:
            st.error(f"❌ Encoding error: {str(e)}")

with tab2:
    st.header("Decode and Extract Metadata")

    # Use encoded text from tab1 or allow manual input
    if 'encoded_text' in st.session_state:
        default_encoded = st.session_state['encoded_text']
    else:
        default_encoded = ""

    encoded_input = st.text_area(
        "Enter encoded text:",
        value=default_encoded,
        height=100,
        help="Paste VIBE-X encoded text to decode"
    )

    if st.button("🔓 Decode Text", type="primary"):
        try:
            decoder = InlineDecoder(Tokenizer())
            decoded = decoder.decode(encoded_input)

            st.success("✅ Decoding successful!")

            # Display clean text
            st.subheader("Clean Text (without markers)")
            st.info(decoded.clean_text)

            # Display tokens
            st.subheader("Tokens")
            st.code(" | ".join([f"{i}:{t}" for i, t in enumerate(decoded.clean_tokens)]))

            # Display metadata blocks
            st.subheader("Extracted Metadata Blocks")

            if decoded.blocks:
                for idx, block in enumerate(decoded.blocks):
                    with st.expander(f"📦 MetaBlock {idx + 1} - HEX: {block.block.to_hex()}", expanded=True):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown(f"""
                            **Binary Encoding:**
                            - Hex: `{block.block.to_hex()}`
                            - Int: `{block.block.to_int()}`
                            - Anchor: `{block.anchor}`
                            - Span: `{block.span}` tokens
                            """)

                        with col2:
                            polarity_names = ["Neutral", "Negative", "Positive", "Ironic"]
                            emotion_names = ["Neutral", "Joy", "Trust", "Fear", "Surprise", "Sadness", "Disgust", "Anger"]

                            st.markdown(f"""
                            **Emotional Attributes:**
                            - Polarity: `{polarity_names[block.block.polarity]}`
                            - Intensity: `{block.block.intensity}/7`
                            - Context: `{'Dynamic' if block.block.context else 'Static'}`
                            - Emotion: `{emotion_names[block.block.emotion]}`
                            - Emergency: `{'Yes' if block.block.emergency else 'No'}`
                            """)

                        # Visualization
                        st.progress(block.block.intensity / 7.0, text=f"Intensity: {block.block.intensity}/7")
            else:
                st.warning("No metadata blocks found in the encoded text.")

        except Exception as e:
            st.error(f"❌ Decoding error: {str(e)}")

with tab3:
    st.header("Batch Analysis")
    st.markdown("Analyze multiple sentences with automatic sentiment detection simulation")

    # Sample texts
    sample_texts = [
        ("I absolutely love this product!", 1, 6, 2, 1),  # positive, joy
        ("This is terrible and disappointing.", 3, 5, 1, 5),  # negative, sadness
        ("The weather is okay I guess.", 0, 2, 0, 0),  # neutral
        ("Great service, highly recommend!", 2, 6, 2, 1),  # positive, joy
        ("This is a disaster waiting to happen.", 4, 6, 1, 3),  # negative, fear
    ]

    if st.button("🚀 Run Batch Analysis"):
        encoder = InlineEncoder(Tokenizer())
        decoder = InlineDecoder(Tokenizer())

        results = []

        for text, anchor, intensity, polarity, emotion in sample_texts:
            # Encode
            annotation = SentimentAnnotation(
                anchor=anchor,
                length=1,
                polarity=polarity,
                intensity=intensity,
                context=0,
                emotion=emotion
            )
            encoded = encoder.encode(text, [annotation])

            # Decode
            decoded = decoder.decode(encoded)

            results.append({
                "Original Text": text,
                "Polarity": ["Neutral", "Negative", "Positive", "Ironic"][polarity],
                "Intensity": intensity,
                "Emotion": ["Neutral", "Joy", "Trust", "Fear", "Surprise", "Sadness", "Disgust", "Anger"][emotion],
                "Hex Code": decoded.blocks[0].block.to_hex() if decoded.blocks else "N/A"
            })

        # Display results
        st.dataframe(results, use_container_width=True)

        # Statistics
        st.subheader("📊 Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Processed", len(results))
        with col2:
            avg_intensity = sum(r["Intensity"] for r in results) / len(results)
            st.metric("Avg Intensity", f"{avg_intensity:.2f}/7")
        with col3:
            positive_count = sum(1 for r in results if r["Polarity"] == "Positive")
            st.metric("Positive Ratio", f"{positive_count}/{len(results)}")

with tab4:
    st.header("🎓 Tutorial: Understanding VIBE-X")

    st.markdown("""
    ## What is VIBE-X?

    VIBE-X (Vector-Integrated Binary Extension) is a compact binary encoding protocol that embeds
    emotional and contextual metadata directly into text streams using 14-bit MetaBlocks.

    ### The 14-bit SPICE-R MetaBlock

    Each MetaBlock contains:
    - **S**pan: Flag + Length (4 bits)
    - **P**olarity: Neutral/Negative/Positive/Ironic (2 bits)
    - **I**ntensity: Emotional strength 0-7 (3 bits)
    - **C**ontext: Static/Dynamic (1 bit)
    - **E**motion: 8 emotion classes (3 bits)
    - **R**eserved/Emergency: Future use (1 bit)

    ### Why VIBE-X?

    Traditional sentiment analysis requires running expensive NLP models **every time** you query.

    **VIBE-X approach:**
    1. ✅ Analyze text **once** with your best model
    2. ✅ Encode results as 14-bit MetaBlocks
    3. ✅ Query infinitely with near-zero cost

    ### Performance Benefits

    - **Storage:** >99% savings vs JSON metadata
    - **Speed:** 0.045 µs per MetaBlock decoding
    - **Energy:** 99.9% lower vs re-running BERT
    - **Cost:** Convert OPEX to one-time CAPEX

    ### Real-World Applications

    - 🛡️ Content moderation & safety
    - 🎯 Personalized recommendations
    - 💬 Customer support routing
    - 🔍 Emotion-aware search
    - 📊 Business intelligence
    - 🚨 Emergency detection systems

    ### Try It Yourself!

    1. Go to the **Encode** tab
    2. Enter any text
    3. Select a token span
    4. Configure emotional parameters
    5. See the encoded result
    6. Decode it in the **Decode** tab

    ---

    **Learn more:** [GitHub Repository](https://github.com/vibexcode/vibe-x) |
    [Documentation](https://doi.org/10.5281/zenodo.17228992)
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>VIBE-X Protocol v1.0.0 | MIT License | <a href="https://github.com/vibexcode/vibe-x">GitHub</a></p>
    <p>Created by Uğur Kandemiş | DOI: <a href="https://doi.org/10.5281/zenodo.17228992">10.5281/zenodo.17228992</a></p>
</div>
""", unsafe_allow_html=True)
