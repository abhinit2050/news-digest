from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client
from flask import Flask, request, jsonify, render_template
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/unsubscribe")
def unsubscribe_page():
    return render_template("unsubscribe.html")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.json

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    # Check if email already exists
    existing = supabase.table("subscribers").select("email").eq("email", email).execute()
    if existing.data:
        return jsonify({"error": "This email is already subscribed"}), 400

    # Insert new subscriber
    supabase.table("subscribers").insert({
        "name": name,
        "email": email,
        "general": data.get("general", False),
        "business": data.get("business", False),
        "science_tech": data.get("science_tech", False),
        "sports": data.get("sports", False),
        "entertainment": data.get("entertainment", False),
        "politics": data.get("politics", False),
        "international_events": data.get("international_events", False),
        "is_active": True
    }).execute()

    return jsonify({"message": f"Welcome {name}! You're now subscribed."}), 201


@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    data = request.json
    email = data.get("email", "").strip()

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Check if email exists
    existing = supabase.table("subscribers").select("email").eq("email", email).execute()
    if not existing.data:
        return jsonify({"error": "Email not found"}), 404

    # Set is_active to False
    supabase.table("subscribers").update({"is_active": False}).eq("email", email).execute()

    return jsonify({"message": "You've been unsubscribed successfully."}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True)