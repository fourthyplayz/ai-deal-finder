# AI Deal Finder 🛍️🤖

AI Deal Finder is a smart, interactive command-line tool that uses Google's latest **Gemini AI model** with **Search Grounding** to hunt down the best open deals for you across the internet. 

Instead of manually scraping websites, this tool acts as your personal shopper. It asks what you want, your budget, and your location, then browses the web in real-time to find active deals and outputs them with direct citations/links to the source!

## ✨ Features
*   **Interactive Prompts:** Simply tell the script what you want, your location, and your budget.
*   **Real-time Web Search:** Uses Gemini's Google Search Grounding to find current, up-to-date deals instead of relying on outdated training data.
*   **Inline Citations:** Provides clickable links to the actual websites where the deals were found.
*   **Lightweight & Fast:** Runs in your terminal with minimal setup.

## 🚀 Getting Started

### 1. Prerequisites
*   Python 3.9 or higher
*   A Gemini API Key. You can get one for free at [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Installation
First, clone or download this repository. Then, install the required Google GenAI SDK:

```bash
pip install google-genai
```

### 3. Setup your API Key
Open `deals_finder.py` in your favorite text editor.
At the very top of the file, you will see a variable called `API_KEY`. Paste your Gemini API key there:

```python
# Paste your Gemini API key here
API_KEY = "YOUR_API_KEY_HERE"
```

*(Alternatively, you can set the `GEMINI_API_KEY` environment variable on your system).*

### 4. Usage
Run the script from your terminal:

```bash
python deals_finder.py
```

The AI will ask you a few questions:
1.  **Item/Model:** (e.g., *ASUS TUF A15*)
2.  **Location:** (e.g., *Cairo*, *US*, or *Online*)
3.  **Budget:** (e.g., *Under $700*)

After you answer, it will search the web and return the best deals it found with citations!

---

### ⚠️ Troubleshooting: `429 RESOURCE_EXHAUSTED`
If you encounter an error like `429 RESOURCE_EXHAUSTED`, it means your API key has reached its quota limit.
*   The **Google Search Grounding** tool executes live searches, which consume quota. 
*   If you are on the free tier, ensure you haven't exceeded your daily limit. You can check your usage and billing details on your Google AI Studio dashboard.
