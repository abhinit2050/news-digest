from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client
from flask import Flask, request, jsonify, render_template
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading

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

def send_confirmation_email(to_email, name):
    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:640px;margin:auto;padding:24px;background:#f9f9f9;">
        <div style="background:#ffffff;border-radius:8px;padding:32px;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <h1 style="font-size:24px;color:#1a1a1a;margin-bottom:8px;">📰 Welcome, {name}!</h1>
            <p style="font-size:15px;color:#555555;line-height:1.6;margin-bottom:16px;">You're now subscribed to Morning Digest. Every day at 8AM IST, you'll receive a curated AI-powered news digest based on your chosen categories.</p>
            <p style="font-size:15px;color:#555555;line-height:1.6;margin-bottom:32px;">Sit back and enjoy your morning news — we'll take care of the rest!</p>
            <p style="font-size:11px;color:#aaaaaa;text-align:center;">Changed your mind? <a href="https://news-digest-ieh6.onrender.com/unsubscribe" style="color:#aaaaaa;">Unsubscribe here</a></p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📰 Welcome to Morning Digest!"
    msg["From"] = os.getenv("SENDER_EMAIL")
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASSWORD"))
    server.sendmail(os.getenv("SENDER_EMAIL"), to_email, msg.as_string())
        print(f"Confirmation email sent to {to_email}")



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

    thread = threading.Thread(target=send_confirmation_email, args=(email, name))
    thread.start()
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