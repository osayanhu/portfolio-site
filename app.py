from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import os
from rave_python import Rave,RaveExceptions, Misc


app = Flask(__name__)

MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_LIST_ID = '254358271b'
MAILCHIMP_SERVER = 'us22'

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
    rave = rave = Rave("FLWPUBK-b9e769dcff8ad603d1f5216827f2aa99-X", production=True)
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    first_name = (request.form.get('name')).split()[0]
    last_name = ' '.join((request.form.get('name')).split()[1:])
    amount = request.form.get('amount')
    tx_ref = request.form.get('tx_ref')
    payload = {
        "tx_ref": tx_ref,
        "amount": amount,
        "currency": "NGN",
        "email": email,
        "phone_number": phone_number,
        "first_name": first_name,
        "last_name": last_name
    }
    try:
        response = rave.BankTransfer.charge(payload)
        return response
    except RaveExceptions.TransactionChargeError as e:
        return e.err

@app.route('/api/check-payment-status', methods=['POST'])
def check_payment_status():
    rave = Rave("FLWPUBK-b9e769dcff8ad603d1f5216827f2aa99-X", production=True)
    reference = request.json.get('txref')
    try:
        response = rave.BankTransfer.verify(reference)
        return response
    except RaveExceptions.TransactionVerificationError as e:
        return e.err

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
