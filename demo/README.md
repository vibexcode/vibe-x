# VIBE-X Demos

This directory contains interactive demonstrations of the VIBE-X protocol.

## 🎭 Streamlit Web Demo

Interactive web-based demo with a beautiful UI.

### Run Locally

```bash
# Install demo dependencies
pip install -r ../requirements-demo.txt

# Run Streamlit app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### Features

- **Encode Tab**: Interactively encode text with emotional metadata
- **Decode Tab**: Extract and visualize metadata from encoded text
- **Batch Analysis Tab**: Process multiple texts at once
- **Tutorial Tab**: Learn about VIBE-X protocol

### Deploy to Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy `demo/streamlit_app.py`

## 📓 Jupyter Notebook Tutorial

Comprehensive, interactive tutorial in notebook format.

### Run Locally

```bash
# Install demo dependencies
pip install -r ../requirements-demo.txt

# Launch Jupyter
jupyter notebook interactive_tutorial.ipynb
```

### Run on Google Colab

Click the badge below to open in Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vibexcode/vibe-x/blob/main/demo/interactive_tutorial.ipynb)

### Run on Binder

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/vibexcode/vibe-x/main?filepath=demo/interactive_tutorial.ipynb)

## 📚 What You'll Learn

1. **Basic Encoding & Decoding**: Get started with VIBE-X
2. **Multiple Annotations**: Handle complex sentiment scenarios
3. **MetaBlock Structure**: Understand the 14-bit encoding
4. **Real-World Examples**: See VIBE-X in action
5. **Performance Benchmarks**: Measure efficiency gains
6. **Error Handling**: Robust error management

## 🚀 Next Steps

After trying the demos:

- Explore [real-world examples](../examples/)
- Read the [full documentation](https://doi.org/10.5281/zenodo.17228992)
- Check out the [source code](../src/vibex/)
- Star the [GitHub repository](https://github.com/vibexcode/vibe-x)

## 💡 Tips

- Start with the Streamlit demo for a quick overview
- Use the Jupyter notebook for deeper understanding
- Try encoding your own texts and experimenting with parameters
- Check the real-world examples for production use cases

## 🐛 Issues?

If you encounter any problems:

1. Make sure you've installed dependencies: `pip install -r ../requirements-demo.txt`
2. Check that you're using Python >= 3.10
3. [Open an issue](https://github.com/vibexcode/vibe-x/issues) on GitHub

---

**VIBE-X Protocol v1.0.0** | MIT License | Created by Uğur Kandemiş
