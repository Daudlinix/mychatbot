from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

# 🔹 Website pages to scrape
travel_pages = [
    "https://redstartravels.co/services",
    "https://redstartravels.co/about",
    "https://redstartravels.co/contact",
    "https://redstartravels.co/packages"
]

# 🔸 Web scraping function
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

# 🔥 Scrape on app start
try:
    travel_site_data = scrape_travel_site()
    print("✅ Scraping success")
except Exception as e:
    travel_site_data = "❌ Scraping failed: " + str(e)
    print(travel_site_data)

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/get")
def get_bot_response():
    user_input = request.args.get("msg")

    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    prompt = f"""
    You are a helpful travel assistant. Reply in 1 short line only.

    Website Info:
    {travel_site_data}

    User: {user_input}
    """

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You're a helpful travel AI. Be short and to the point."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        data = res.json()
        if "choices" in data:
            return jsonify(reply=data["choices"][0]["message"]["content"])
        else:
            return jsonify(reply="AI Error: " + str(data))
    except Exception as e:
        return jsonify(reply="Error: " + str(e))

# ✅ For deployment (Railway, Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
