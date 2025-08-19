from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
from supabase import create_client, Client
import re
import subprocess
import time
import os, hmac, hashlib
import json
import uuid
from rave_python import Rave,RaveExceptions, Misc
from dotenv import load_dotenv
import os
import uuid
import datetime
import smtplib
from google.cloud import storage
import fitz  # PyMuPDF
from email.mime.text import MIMEText
from google.oauth2 import service_account

load_dotenv()



app = Flask(__name__)


MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_LIST_ID = '254358271b'
MAILCHIMP_SERVER = 'us22'
BASE_URL = "https://api.flutterwave.cloud/f4bexperience"
idempotency_key = str(uuid.uuid4())
TOKEN_CACHE = {"access_token": None, "expires_at": 0}  # simple in-memory cache


def get_flutterwave_token():

    now = int(time.time())
    if TOKEN_CACHE["access_token"] and now < TOKEN_CACHE["expires_at"]:
        return TOKEN_CACHE["access_token"]
    client_id = os.getenv("RAVE_PUBLIC_KEY")
    client_secret = os.getenv("RAVE_SECRET_KEY")
    
    url = "https://idp.flutterwave.com/realms/flutterwave/protocol/openid-connect/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    token_data = response.json()
    TOKEN_CACHE["access_token"] = token_data["access_token"]
    TOKEN_CACHE["expires_at"] = now + token_data["expires_in"] - 10  # subtract 10s as buffer


    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()  # Raises an error if the request failed
    return token_data["access_token"]

@app.route('/get-cus', methods=['POST'])
def create_flutterwave_customer():

    access_token = get_flutterwave_token()
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    email = request.args.get("email")
    idempotency_key = str(uuid.uuid4())
    url = f"{BASE_URL}/customers"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "X-Idempotency-Key": idempotency_key
    }
    payload = {
        "name": {
            "first": first_name,
            "last": last_name
        },
        "email": email
    }
    resp = requests.post(url, headers=headers, json=payload)
    print("customer created", resp.json())
    resp.raise_for_status()
    return resp.json()["data"]["id"]



def create_flutterwave_virtual_account(access_token, tx_ref, customer_id, amount, narration):
    url = f"{BASE_URL}/virtual-accounts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "X-Idempotency-Key": idempotency_key
    }
    payload = {
        "reference": tx_ref,
        "customer_id": customer_id,
        "expiry": 60,
        "amount": amount,
        "currency": "NGN",
        "account_type": "dynamic",
        "narration": narration
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()["data"]
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/excelebook')
def excel():
    return render_template('excelebook.html')

@app.route('/pythonebook')
def python():
    return render_template('pythonebook.html')

SENDER_EMAIL = os.getenv("SENDER_EMAIL")  # Your Gmail address
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # App password from Google
GCS_BUCKET = os.getenv("GCS_BUCKET")  # e.g. "my-ebooks-bucket"
SIGNED_URL_EXP_HOURS = int(os.getenv("SIGNED_URL_EXP_HOURS", "72"))

def send_html_email(to_email: str, subject: str, html: str):
    msg = MIMEText(html, "html")
    msg["To"] = to_email
    msg["From"] = SENDER_EMAIL
    msg["Subject"] = subject

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)

# --------------------------
# GCS helpers
# --------------------------
service_account_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
credentials = service_account.Credentials.from_service_account_info(service_account_info)
client = storage.Client(credentials=credentials, project=credentials.project_id)

def gcs_client():
    return storage.Client(credentials=credentials, project=credentials.project_id)

def download_blob_to_bytes(bucket_name: str, cld: str) -> bytes:
    if cld == 'python:'
        blob = gcs_client().bucket(bucket_name).blob('Original/pythonprog.pdf')
    elif cld == 'excel':
        blob = gcs_client().bucket(bucket_name).blob('Original/excelebook.pdf')
    else:
        raise ValueError("Invalid class specified. Use 'python' or 'excel'.")
    return blob.download_as_bytes()

def upload_bytes_to_blob(bucket_name: str, blob_name: str, data: bytes, content_type="application/pdf"):
    blob = gcs_client().bucket(bucket_name).blob(blob_name)
    blob.upload_from_string(data, content_type=content_type)

def generate_signed_url(bucket_name: str, blob_name: str, hours: int) -> str:
    blob = client.bucket(bucket_name).blob(blob_name)
    return blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(hours=hours),
        method="GET",
    )

# --------------------------
# PDF stamping
# --------------------------
def stamp_pdf_bytes(pdf_bytes: bytes, stamp_text: str) -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        rect = page.rect
        margin_x, margin_y = 12, 12
        fontsize = 8
        text_rect = fitz.Rect(
            rect.width - 200 - margin_x,
            rect.height - 20 - margin_y,
            rect.width - margin_x,
            rect.height - margin_y
        )
        page.insert_textbox(
            text_rect,
            stamp_text,
            fontsize=fontsize,
            fontname="helv",
            color=(0, 0, 0),
            align=1
        )
    stamped_bytes = doc.tobytes()
    doc.close()
    return stamped_bytes

# --------------------------
# Flutter endpoint
# --------------------------
@app.route("/flutter/ebook", methods=["POST"])
def flutter_ebook():
    data = request.get_json(force=True, silent=True) or {}
    name = data.get("full_name")
    email = data.get("email")
    transaction_time = data.get("transaction_time")
    cld = data.get("class")

    if not name or not email or not transaction_time:
        return jsonify({"error": "Missing full_name, email, or transaction_time"}), 400

    # Send initial response quickly so Flutter knows request is received
    # (Optional: you can process async with Celery/Cloud Tasks)
    try:
        original_bytes = download_blob_to_bytes(GCS_BUCKET, cld)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch original ebook: {e}"}), 500

    # Stamp PDF
    stamp = f"{email} | {transaction_time}"
    try:
        processed_bytes = stamp_pdf_bytes(original_bytes, stamp)
    except Exception as e:
        return jsonify({"error": f"Failed to stamp ebook: {e}"}), 500

    # Upload processed copy
    processed_key = f"processed/{uuid.uuid4()}.pdf"
    try:
        upload_bytes_to_blob(GCS_BUCKET, processed_key, processed_bytes)
    except Exception as e:
        return jsonify({"error": f"Failed to upload processed ebook: {e}"}), 500

    # Create signed URL
    try:
        signed_url = generate_signed_url(GCS_BUCKET, processed_key, SIGNED_URL_EXP_HOURS)
    except Exception as e:
        return jsonify({"error": f"Failed to generate signed URL: {e}"}), 500

    # Send notification email
    try:
        ready_html = render_template("ebook_ready.html", name=name, cld=cld, download_link=signed_url)
        send_html_email(email, "Your ebook is ready", ready_html)
    except Exception as e:
        return jsonify({"error": f"Failed to send ready email: {e}"}), 500

    return jsonify({
        "status": "ok",
        "message": "Ebook processed successfully",
        "download_link": signed_url
    })
@app.route('/', methods=['POST'])
def subscribe():
    name = request.form.get('name')
    email = request.form.get('email')
    if email:
        subscribe_to_mailchimp(name,email)
        return render_template('home.html', success=True)
    return redirect('home.html')


def subscribe_to_mailchimp(name, email):
    url = f'https://{MAILCHIMP_SERVER}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members'
    data = {
        "email_address": email,
        "status": "subscribed",
        "merge_fields": {
            "FNAME": name
        }
    }
    response = requests.post(url, auth=('anystring', MAILCHIMP_API_KEY), json=data)

# Supabase setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

MOBILE_OFFER = "https://www.transictiopool.wiki/click?offer_id=32308&pub_id=273841&pub_click_id=ADD_CLICK_ID_HERE&site=PASS_SITE_HERE&external_id={{sub_id}}"
DESKTOP_OFFER = "https://lnksforyou.com/view.php?id=5540952&pub=3285829&sub_id={sub_id}"

@app.route("/start", methods=["GET"])
def start_offer():
    name = request.args.get("name")
    email = request.args.get("email")
    user_agent = request.headers.get("User-Agent", "").lower()

    # generate unique sub_id (you can also use email hash)
    sub_id = str(uuid.uuid4())

    # detect device
    if re.search("mobile|android|iphone", user_agent):
        offer_url = MOBILE_OFFER.format(sub_id=sub_id)
        device_type = "mobile"
    else:
        offer_url = DESKTOP_OFFER.format(sub_id=sub_id)
        device_type = "desktop"

    # save to supabase
    supabase.table("offers").insert({
        "sub_id": sub_id,
        "name": name,
        "email": email,
        "device": device_type,
        "status": "started"
    }).execute()

    return redirect(offer_url)

@app.route("/postback", methods=["GET"])
def postback():
    sub_id = request.args.get("sub_id") or request.args.get("pub_click_id")
    payout = request.args.get("payout")

    if not sub_id:
        return "Missing sub_id", 400

    # Lookup user in Supabase
    user_resp = supabase.table("offers").select("full_name, email").eq("sub_id", sub_id).execute()
    if not user_resp.data:
        return "User not found", 404

    user = user_resp.data[0]
    full_name = user["full_name"]
    email = user["email"]

    # Build payload for file download
    payload = {
        "full_name": full_name,
        "email": email,
        "transaction_time": datetime.utcnow().isoformat(),
        "class": "esel"
    }
    FLUTTER_WEBHOOK_URL = "osayanhu.vercel.app/flutter/ebook"
    try:
        r = requests.post(FLUTTER_WEBHOOK_URL, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return f"Error forwarding to webhook: {e}", 500

    # Update conversion in DB
    supabase.table("offers").update({
        "status": "completed",
        "payout": payout,
        "completed_at": datetime.utcnow().isoformat()
    }).eq("sub_id", sub_id).execute()

    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
