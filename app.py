import joblib
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)

# Load the ML model
model = joblib.load('happiness_model.pkl')

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create the database
with app.app_context():
    db.create_all()

# Utility: Check if logged in
def is_logged_in():
    return 'user_id' in session

@app.route('/')
def home():
    # Redirect to the login page by default
    return redirect(url_for('login'))

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!")
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return render_template('register.html')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('input_page'))

        flash("Invalid credentials. Please Register")
        return redirect(url_for('login'))

    return render_template('login.html')

# Input Page
@app.route('/input', methods=['GET', 'POST'])
def input_page():
    if not is_logged_in():
        flash("Please log in to access this page.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            gdp = float(request.form['gdp'])
            social_support = float(request.form['social_support'])
            life_expectancy = float(request.form['life_expectancy'])
            freedom = float(request.form['freedom'])
            generosity = float(request.form['generosity'])
            corruption = float(request.form['corruption'])

            input_data = np.array([[gdp, social_support, life_expectancy, freedom, generosity, corruption]])
            happiness_prediction = model.predict(input_data)[0]

            return redirect(url_for('result_page', result=round(happiness_prediction, 2)))
        except ValueError:
            flash("Please enter valid numerical values.")
            return redirect(url_for('input_page'))

    return render_template('input_page.html')

# Result Page
@app.route('/result')
def result_page():
    if not is_logged_in():
        flash("Please log in to view the results.")
        return redirect(url_for('login'))

    result = request.args.get('result')
    return render_template('result.html', result=result)

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return render_template('logout.html')

if __name__ == '__main__':
    app.run(debug=True)
