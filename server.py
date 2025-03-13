from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS
import difflib  # For searching similar text

app = Flask(__name__)
CORS(app)

API_KEY = "AIzaSyDemtxd-qnLfXMcGEcesTirNSDq0sbwECI"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Load Handbook Data
with open("amity_handbook.json", "r", encoding="utf-8") as file:
    handbook_data = json.load(file)["content"]

def search_handbook(query):
    """
    Searches for relevant paragraphs in the Amity Handbook.
    Returns the most relevant paragraph.
    """
    matches = difflib.get_close_matches(query, handbook_data, n=1, cutoff=0.3)  # Find closest paragraph
    return matches[0] if matches else None

@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.json
    user_input = data.get("message").lower()

    # Search in the Amity Handbook first
    handbook_response = search_handbook(user_input)
    if handbook_response:
        return jsonify({"message": f"📖 Handbook Reference:\n{handbook_response}"})

    # If no relevant text is found, ask Gemini API
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_input}]}]
    }

    try:
        response = requests.post(GEMINI_API_URL, json=payload)

        # Debugging: Print the raw response
        print("Raw Gemini API Response:", response.text)

        # Ensure the API response is successful
        if response.status_code != 200:
            return jsonify({"error": f"Gemini API Error: {response.status_code}", "details": response.text}), response.status_code

        response_json = response.json()

        # Extract chatbot response
        chatbot_response = (
            response_json.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "Sorry, I didn't understand that.")
        )

        return jsonify({"message": chatbot_response})  # Return only the chatbot text

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to reach Gemini API", "details": str(e)}), 500
    except requests.exceptions.JSONDecodeError:
        return jsonify({"error": "Invalid response from Gemini API", "details": response.text}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
