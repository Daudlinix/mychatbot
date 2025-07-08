from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# 🔶 Step 1: Tumhare travel website ke pages
travel_pages = [
    "https://redstartravels.co/services",
    "https://redstartravels.co/about",
    "https://redstartravels.co/contact",
    "https://redstartravels.co/packages"
]

# 🔷 Step 2: Scraping function
def scrape_travel_site():
    all_data = ""
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in travel_pages:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            all_data += f"\n\nPAGE: {url}\n{text}"
        except Exception as e:
            all_data += f"\n\nPAGE: {url}\nError: {str(e)}"
    return all_data

# 🔥 Step 3: Load website data once when app starts
try:
    travel_site_data = scrape_travel_site()
    print("✅ Website data scraped successfully")
except Exception as e:
    travel_site_data = "⚠️ Failed to scrape website: " + str(e)
    print(travel_site_data)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/get")
def chatbot_response():
    user_input = request.args.get("msg")
    try:
        headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://daudkhan.com",
            "X-Title": "Khan-Chatbot"
        }

        # ✅ Prompt with scraped website data
        prompt = f"""
        You are a helpful travel assistant.
        Only answer in one line.

        Website info:
        {travel_site_data}

        User: {user_input}
        """

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You're THRILLING TECH helpful AI assistant. Only reply in 1 line."},
                {"role": "user", "content": prompt}
            ]
        }

        res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        data = res.json()

        if "choices" in data:
            return jsonify(reply=data["choices"][0]["message"]["content"])
        else:
            return jsonify(reply="AI Error: " + str(data))

    except Exception as e:
        return jsonify(reply="Error: " + str(e))

# ✅ Render / Railway friendly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
