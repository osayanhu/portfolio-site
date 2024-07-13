from flask import Flask, render_template, request,flash

app = Flask(__name__)


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
        with open('contact_submissions.txt', 'a') as f:
            f.write(f"Name: {name}\nEmail: {email}\n\n")
        return render_template('home.html', success=True)
        flash('Thank you for subscribing!', 'success')
    else:
        flash('Please provide a valid email.', 'error')
    return redirect('home.html')

if __name__ == '__main__':
    app.run(debug=True)
