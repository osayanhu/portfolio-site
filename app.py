from flask import Flask, render_template, request, redirect, url_for
import requests
import json


with open('mailchimp.txt') as file:
    lines = [line.rstrip() for line in file]
app = Flask(__name__)

MAILCHIMP_API_KEY = lines[1]
MAILCHIMP_LIST_ID = lines[0]
MAILCHIMP_SERVER = 'us22'

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/courses')
def courses():
    return render_template('courses.html')


@app.route('/subscribe', methods=['POST'])
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
