from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import os


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
