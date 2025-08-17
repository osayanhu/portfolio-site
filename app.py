from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import time
import os, hmac, hashlib
import json
import uuid
from rave_python import Rave,RaveExceptions, Misc
from dotenv import load_dotenv

load_dotenv()



app = Flask(__name__)


MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_LIST_ID = '254358271b'
MAILCHIMP_SERVER = 'us22'
BASE_URL = "https://api.flutterwave.cloud"
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

def create_flutterwave_customer(access_token, first_name, last_name, email):
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

@app.route("/api/create-virtual-account", methods=['POST'])
def create_python_virtual_account():
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')  # optional, Flutterwave doesn't strictly need it here
    full_name = request.form.get('name')
    first_name = full_name.split()[0]
    last_name = ' '.join(full_name.split()[1:])
    amount = request.form.get('amount')
    
    try:
        # Step 1: Get token
        token = get_flutterwave_token()
        
        # Step 2: Create customer
        customer_id = create_flutterwave_customer(token, first_name, last_name, email)
        
        # Step 3: Create virtual account
        va_data = create_flutterwave_virtual_account(token, customer_id, amount, full_name)
        
        return jsonify({"status": "success", "virtual_account": va_data})
    except requests.HTTPError as e:
        return jsonify({"status": "error", "message": str(e), "response": e.response.text}), 400

def verify_webhook_signature(request_data, header_hash):
    hash_calculated = hmac.new(
        key=FLW_SECRET_HASH.encode('utf-8'),
        msg=request_data,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(hash_calculated, header_hash)

def verify_charge(charge_id=None, tx_ref=None):
    if not charge_id and not tx_ref:
        return {"error": "charge_id or tx_ref required"}

    access_token = get_flutterwave_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    if charge_id:
        url = f"https://api.flutterwave.cloud/developersandbox/charges/{charge_id}"
    else:
        url = f"https://api.flutterwave.cloud/developersandbox/transactions/{tx_ref}/verify"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    # Optional: your custom logic to mark order as paid
    if data.get("status") == "success" and data.get("data", {}).get("status") == "succeeded":
        print("Payment verified:", data["data"])
        # Do post-payment processing here
        return {"status": "success", "data": data["data"]}

    return {"status": "pending", "data": data.get("data")}

@app.route('/api/payment-status', methods=['POST'])
def payment_status():
   data = request.get_data()
   json_data = request.json
   tx_ref = json_data.get("tx_ref")
   result = verify_charge(tx_ref=tx_ref)
   if result.get("status") == "success" and result.get("data", {}).get("status") == "succeeded":
        # post-payment external processing (Zapier, etc)
        requests.post(
            "https://python-proc-713130948738.us-central1.run.app/zap/webhook",
            json={
                "name": json_data.get("name"),
                "email": json_data.get("email"),
                "tx_ref": json_data.get("tx_ref")
            }
        )
        return jsonify({"status": "success", "message": "Payment verified"}), 200
   return jsonify({"status": "pending", "message": "Payment not yet completed"}), 200
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
    return response.json()


if __name__ == '__main__':
    app.run(debug=True)
